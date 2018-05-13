import paho.mqtt.client as mqtt
import paho.mqtt.publish as publisher
import time
import json
import numpy as np
import sys
import copy
import pymongo
import pymongo.collection
from pymongo import MongoClient
from flask import Flask, abort, Response, request
from threading import Thread, Lock

"""
	beacon dictionary <name, BeaconInfo>
"""
beaconTable = {}

#List of registered rooms
rooms= []

"""
	Lock
"""
lock = None

"""
    Instance of web-server
"""
webApp = Flask(__name__)

"""
	Instance of the database
"""
database = None

class DBInterface():
	
	"""
	Class used to interface with the MongoDB host.
	A DB entry is seen as a dictionary, so all the query methods return a list of dictionaries.
	"""

	def __init__(self, __connection_parameters):
		self.__connection_parameters = __connection_parameters
		self.__client = MongoClient(
    		'mongodb://{user}:{password}@{host}:'
   			'{port}/{namespace}'.format(**self.__connection_parameters)
		)
		self.__collection = self.__client["help_db"]["LocalizationResults"]

	# Insert a new entry in the database
	def insert_db_entry(self, device, location):
		self.__collection.insert_one({"device":device, "room":location})

	# Delete a specific DB entry
	def delete_db_entry(self, device, location):
		self.__collection.delete_one({"device":device, "room":location})

	# Delete all the entries relative to a specific device
	def delete_device_entries(self, device):
		self.__collection.delete_many({"device":device})

	# Delete all the entries relative to a specific room
	def delete_room_entries(self, room):
		self.__collection.delete_many({"room":room})

	# Delete all the entries in the DB
	def clean_db(self):
		self.__collection.delete_many({})

	# Retrieve all the entries in the DB
	def get_all_entries(self):
		return self.__collection.find({})

	#Retrieve all the entries relative to a specific device
	def get_device(self, device):
		return self.__collection.find({"device":device})

	#Retrieve all the entries relative to a specific room
	def get_room(self, room):
		return self.__collection.find({"room":room})
	



class Triangulate(Thread):
	"""
		Thread performing the triangulation
	
		Instances:
			__time:	time to wait before performing triagulation
			
	"""

	def __init__(self, time):
		Thread.__init__(self)
		self.__time = time

	
	def run(self):
		while(True):
			time.sleep(self.__time)

			lock.acquire(True)
			# copy of the current beacon table
			temp_table = copy.deepcopy(beaconTable)
			# beacon table reset
			for b in beaconTable :
				beaconTable[b].cleanInfo()

			lock.release()

			for bea in temp_table :
				# For each beacon

				info = {}
				sumLen = 0

				for pos in temp_table[bea].getMap():
					# For each room

					s = sum(temp_table[bea].getMap()[pos])
					l = len(temp_table[bea].getMap()[pos])
					sumLen += l

					info[pos] = dict()
					info[pos]["lis"] = temp_table[bea].getMap()[pos]
					if l == 0 :
						# No msg received
						info[pos]["mean"] = float("-inf")
						info[pos]["var"] = float("-inf")
						info[pos]["len"] = float("-inf")
					else:
						info[pos]["mean"] = s / l
						info[pos]["var"] = float(np.var(info[pos]["lis"]))
						info[pos]["len"] = l

				# Get located room
				MAXIMO = float("-inf")
				stanza = ""
				for pos in info :

					if info[pos]["mean"] > MAXIMO:
						stanza = pos					
						MAXIMO = info[pos]["mean"]
				
				if stanza != "":
					beaconTable[bea].setLast(stanza)
					print(beaconTable[bea].getLast())








class BeaconInfo():
	"""
		Class for a beacon

		Instances:
			__map: 	a dictionary map <room, measure_list>
			__id:	Beacon's id
			__rooms: list of registered rooms 
			__last:	last room a person was detected
	"""


	def __init__(self, id, rs):
		self.__map = dict()
		self.__id = id
		self.__last = ""
		self.__rooms= rs


	# Getters
	def getMap(self):
		return self.__map


	def getId(self):
		return self.__id


	def getLast(self):
		return self.__last


	# Setters
	def setLast(self, last):
		self.__last = last


	# Other Methods
	def addMeasure(self, room, measure):
		"""
			Add a received measure from a given room
		"""

		# Checking if requested room already exists
		if not room in self.__rooms:
			print "Room  " + room + "  doesn't exists (NOT REGISTERED!)"
			return

		if not self.__map.has_key(str(room)):
			self.__map[str(room)] = []

		self.__map[str(room)].extend(measure)


	def cleanInfo(self):
		"""
			Clean the current (rssi) values from the map
		"""
		for e in self.__map:
			self.__map[e] = []









class WebServer(Thread):
    """
        Thread running the web server
    """

    def __init__(self, app, ip, port):
		Thread.__init__(self)
		self.__flaskApp= app
		self.__port= port
		self.__ip = ip


    def run(self):
		self.__flaskApp.run(self.__ip, self.__port)


## Routing rules for web server thread
@webApp.route('/')
def root():
    return Response("Welcome to REST API!", status=200, content_type="text/plain")

#####
#####     /rooms
@webApp.route("/rooms", methods=["GET"])
def roomsGet():
    return Response(json.dumps(rooms), status=200, content_type="application/json")

#####
#####     /rooms/<rid>
@webApp.route("/rooms/<rid>", methods=['GET'])
def getRooms (rid):
	if rid == "" : 
		return Response("Room is empty", status=400, content_type="text/plain")
	elif not rid in rooms :
		return Response("Requested room doesn't exists", status=400, content_type="text/plain")
	else :
		ls = []
		lock.acquire (True)
		for b in beaconTable :
			if beaconTable[b].getLast() == rid :
				ls.append(beaconTable[b].getId())
		lock.release()
		return Response (json.dumps(ls), status=200, content_type="application/json")


@webApp.route("/rooms/<rid>", methods=['POST'])
def postRooms(rid):
	if rid == "" :
		return Response("Room is empty!", status=400, content_type="text/plain")
	elif rid in rooms :
		return Response("Requested room already exists!", status=400, content_type="text/plain")
	else :
		#print ("Creating room " + rid)
		rooms.append(rid)
		return Response("", status=201, content_type="text/plain")


@webApp.route("/rooms/<rid>", methods=['DELETE'])
def deleteRooms(rid):
	if rid == "" :
		return Response("Room name is empty!", status=400, content_type="text/plain")
	elif not rid in rooms :
		return Response("Room name  " + rid + "  doesn't exist!", status=400, content_type="text/plain")
	else :
		lock.acquire(True)
		rooms.remove (rid)
		for b in beaconTable :
			bo = beaconTable[b]
			if bo.getLast() == rid :
				bo.setLast("")
		lock.release ()
		return Response("", status=200, content_type="text/plain")

#####
#####     /readings/<bid>
@webApp.route("/readings/<bid>", methods=['GET'])
def getReadings(bid):
	if bid == "" :
		return Response("Beacon id is empty!", status=400, content_type="text/plain")
	elif not beaconTable.has_key(bid) :
		return Response("Beacon id  " + bid + "  doesn't exist!", status=400, content_type="text/plain")
	else :
		lock.acquire(True)
		res= json.dumps(beaconTable[bid].getMap())
		lock.release ()
		return Response(res, status=200, content_type="application/javascript")


@webApp.route("/readings/<bid>", methods=['DELETE'])
def deleteReadings(bid):
	if bid == "" :
		return Response("Beacon id is empty!", status=400, content_type="text/plain")
	elif not beaconTable.has_key(bid) :
		return Response("Beacon id  " + bid + "  doesn't exist!", status=400, content_type="text/plain")
	else :
		lock.acquire(True)
		beaconTable[bid].cleanInfo()
		lock.release ()
		return Response("", status=200, content_type="text/plain")


#####
#####     /people
@webApp.route("/people", methods=["GET"])
def getPeopleLocations():

	people = dict()
	for b in beaconTable:
		if not beaconTable[b].getLast() == "":
			people[b] = str(beaconTable[b].getLast())
	print(people)
	return Response(json.dumps(people), status=200, content_type="application/json")


#####
#####     /people/<rid>
@webApp.route("/people/<rid>", methods=["GET"])
def getPeople(rid):
    return Response('["TODO list of people in a room"]', status=200, content_type="application/json")


@webApp.route("/people/<pid>", methods=["POST"])
def postPeople(pid):
	if pid == "" :
		return Response("Beacon id is empty!", status=400, content_type="text/plain")
	elif beaconTable.has_key (pid) :
		return Response("Beacon with id  " + pid + "  already exists!", status=400, content_type="text/plain")
	else :
		lock.acquire(True)
		beaconTable[pid]= BeaconInfo(pid, rooms)		
		lock.release ()
		return Response('', status=200, content_type="text/plain")


@webApp.route("/people/<pid>", methods=["DELETE"])
def deletePeople(pid):
	if pid == "" :
		return Response("Beacon id is empty!", status=400, content_type="text/plain")
	elif not beaconTable.has_key (pid) :
		return Response("Beacon with id  ' + pid + '  doesn't exist!", status=400, content_type="text/plain")
	else :
		lock.acquire(True)
		beaconTable.pop(pid)
		lock.release ()
		return Response('', status=200, content_type="application/json")








def on_message(client, userdata, message):
	"""
		Broker callback once a msg is received
	"""

	jsonMsg = json.loads(message.payload.decode("utf-8"))

	lock.acquire(True)

	for b in jsonMsg["map"] :
		if beaconTable.has_key(b) :
			beaconTable[b].addMeasure(jsonMsg["position"],  jsonMsg["map"][b])
		
	lock.release()
	"""
		forma del payload
		{
			"id" : value
			"position" : value
			{
				"andrea" : [rssi_1, ..., rssi_n]
				"luca" : [rssi_1, ..., rssi_n]
				"chiara" : [rssi_1, ..., rssi_n]
				"nerfgun" : [rssi_1, ..., rssi_n]
			}
		}
	"""



def main():
	"""
		Main
	"""

	if len(sys.argv) != 2 :
		sys.exit("Wrong number of arguments!\n\tExiting")

	print ("Initializing server")
	jsonData = json.load(open(sys.argv[1]))
	#print(json.dumps(jsonData))

	global beaconTable
	global lock
	global rooms
	global database


	beaconTable = dict()
	lock = Lock()

	for r in jsonData["rooms"] :
		rooms.append(r)
		
	for b in jsonData["devices"] :
		beaconTable[b]= BeaconInfo(b, rooms)

	
	# Instantiate Broker
	broker_address = jsonData["broker-ip"]
	topic = jsonData["topic"]

	print ("Init broker")

	client = mqtt.Client("P1")
	client.connect(broker_address)
	client.subscribe(topic)
	client.on_message=on_message
	client.loop_start()

	# Initiate connection with MongoDB
	database = DBInterface(jsonData["DB_connection_params"])

	# Activate triangulator thread
	triangulate = Triangulate(int(jsonData["algorithm-interval"]))
	triangulate.daemon = True
	triangulate.start()

    # Activating web-server thread
	webServer= WebServer(webApp, jsonData["server-ip"], int(jsonData["server-port"]))
	webServer.daemon = True
	webServer.start()

	print ("Starting loop")

	while True:
		time.sleep(1)




if __name__ == "__main__":
	main()
