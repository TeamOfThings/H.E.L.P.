import paho.mqtt.client as mqtt
import paho.mqtt.publish as publisher
import time
import json
import numpy as np
import sys
import copy
import pymongo
import pymongo.collection
import signal
from pymongo import MongoClient
from flask import Flask, abort, Response, request
from threading import Thread, Lock


# beacon dictionary <name, BeaconInfo>
beaconTable = {}

# Content of configuration file
configFileContent = {}

# Mutex for beaconTable
beaconTableLocker = None

# Mutex for configFileContent
configFCLocker = None

# Configuration file name
configFileName = ""

# Topic's name on which publish updates for sniffers
pubTopic= ""

# Instance of web-server
webApp = Flask(__name__)



"""
	Instance of the database
"""
database = None



# Function to save configFileContent to to the file
def  storeConfigurationFile () :
	print ("Saving configuration to " + configFileName)
	f= open(configFileName, 'w')
	json.dump (configFileContent, f)
	f.close()



# Function to convert rooms list to an array
def roomsToArray () :
	arr= []
	for p in configFileContent["positions"] :
		arr.append (configFileContent["positions"][p])
	return arr



# Function to translate room name to room id
def roomNameToId (rn) :
	rid= ""
	if rn != "" :
		for p in configFileContent["positions"] :
			if (configFileContent["positions"][p] == rn) :
				rid = p
				break
	return p



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

			beaconTableLocker.acquire(True)
			# copy of the current beacon table
			temp_table = copy.deepcopy(beaconTable)
			# beacon table reset
			for b in beaconTable :
				beaconTable[b].cleanInfo()

			beaconTableLocker.release()

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
					database.insert_db_entry(bea, stanza)
					roomId= beaconTable[bea].getLast()
					print(bea + " - " + configFileContent["positions"][roomId] + " :: " + str(info[pos]["lis"]) + " mean : " + str(info[pos]["mean"]))

			print("---------------------------------------------")








class BeaconInfo():
	"""
		Class for a beacon

		Instances:
			__map: 	a dictionary map <room, measure_list>
			__id:	Beacon's id
			__sniffId: list of registered sniffers ID
			__last:	last room a person was detected
	"""


	def __init__(self, id, sids):
		self.__map = dict()
		self.__id = id
		self.__last = ""
		self.__sniffIds= sids


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
	def addMeasure(self, sid, measure):
		"""
			Add a received measure from a given room
		"""

		# Checking if requested room already exists
		if not sid in self.__sniffIds:
			print "Room  " + sid + "  doesn't exists (NOT REGISTERED!)"
			return

		if not self.__map.has_key(str(sid)):
			self.__map[str(sid)] = []

		self.__map[str(sid)].extend(measure)


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
	return Response(json.dumps(roomsToArray()), status=200, content_type="application/json")

#####
#####     /rooms/<rn>
@webApp.route("/rooms/<rn>", methods=['GET'])
def getRooms (rn):
	rooms= roomsToArray()
	rid = roomNameToId(rn)

	if rn == "" : 
		return Response("Room is empty", status=400, content_type="text/plain")
	elif not rn in rooms :
		return Response("Requested room doesn't exists", status=400, content_type="text/plain")
	else :
		ls = []
		beaconTableLocker.acquire (True)
		# Searching all people in a required room
		for b in beaconTable :
			if beaconTable[b].getLast() == rid :
				ls.append(beaconTable[b].getId())
		beaconTableLocker.release()
		return Response (json.dumps(ls), status=200, content_type="application/json")


# FIXME
@webApp.route("/rooms/<rn>", methods=['POST'])
def postRooms(rn):
	toRet= None
	configFCLocker.acquire(True)
	if rid == "" :
		toRet= Response("Room is empty!", status=400, content_type="text/plain")
	elif rid in rooms :
		toRet= Response("Requested room already exists!", status=400, content_type="text/plain")
	else :
		#print ("Creating room " + rid)
		rooms.append(rid)
		configFileContent["rooms"].append(rid)
		storeConfigurationFile ()
		toRet= Response("", status=201, content_type="text/plain")
	configFCLocker.release()
	return toRet


# FIXME
@webApp.route("/rooms/<rn>", methods=['DELETE'])
def deleteRooms(rn):
	toRet= None
	configFCLocker.acquire(True)
	if rid == "" :
		toRet= Response("Room name is empty!", status=400, content_type="text/plain")
	elif not rid in rooms :
		toRet= Response("Room name  " + rid + "  doesn't exist!", status=400, content_type="text/plain")
	else :
		beaconTableLocker.acquire(True)
		rooms.remove (rid)
		configFileContent["rooms"].remove(rid)
		storeConfigurationFile ()
		
		for b in beaconTable :
			bo = beaconTable[b]
			if bo.getLast() == rid :
				bo.setLast("")
		beaconTableLocker.release ()
		database.delete_room_entries(rid)
		toRet= Response("", status=200, content_type="text/plain")
	configFCLocker.release()
	return toRet



#####
#####     /readings/<bid>
@webApp.route("/readings/<bid>", methods=['GET'])
def getReadings(bid):
	if bid == "" :
		return Response("Beacon id is empty!", status=400, content_type="text/plain")
	elif not beaconTable.has_key(bid) :
		return Response("Beacon id  " + bid + "  doesn't exist!", status=400, content_type="text/plain")
	else :
		beaconTableLocker.acquire(True)
		res= json.dumps(beaconTable[bid].getMap())
		beaconTableLocker.release ()
		return Response(res, status=200, content_type="application/javascript")


@webApp.route("/readings/<bid>", methods=['DELETE'])
def deleteReadings(bid):
	if bid == "" :
		return Response("Beacon id is empty!", status=400, content_type="text/plain")
	elif not beaconTable.has_key(bid) :
		return Response("Beacon id  " + bid + "  doesn't exist!", status=400, content_type="text/plain")
	else :
		beaconTableLocker.acquire(True)
		beaconTable[bid].cleanInfo()
		beaconTableLocker.release ()
		return Response("", status=200, content_type="text/plain")


#####
##### TODO un metodo per prendere tutte le persone registrate


#####
#####     /people
@webApp.route("/people", methods=["GET"])
def getPeopleLocations():

	people = dict()
	beaconTableLocker.acquire (True)
	for b in beaconTable:
		if not beaconTable[b].getLast() == "" :
			rid = beaconTable[b].getLast()
			people[b] = str(configFileContent["positions"][rid])
	beaconTableLocker.release()
	print(people)
	return Response(json.dumps(people), status=200, content_type="application/json")


#####
#####     /people/<rid>
@webApp.route("/people/<pid>", methods=["POST"])
def postPeople(pid):
	toRet= None
	configFCLocker.acquire(True)
	beaconTableLocker.acquire(True)
	if pid == "" :
		toRet= Response("Beacon id is empty!", status=400, content_type="text/plain")
	elif beaconTable.has_key (pid) :
		toRet= Response("Beacon with id  " + pid + "  already exists!", status=400, content_type="text/plain")
	else :
		rs= roomsToArray()
		beaconTable[pid]= BeaconInfo(pid, rs)
		configFileContent["devices"].append(pid)
		storeConfigurationFile()
		
		# Publishing new person to all people with mac address
		payload = {
			"action" : "add",
			"name" : pid,
			"mac" : request.data
		}
		brokerAddress = configFileContent["broker-ip"]
		publisher.single (pubTopic, json.dumps(payload), hostname=brokerAddress)

		toRet= Response('', status=201, content_type="text/plain")
	beaconTableLocker.release()
	configFCLocker.release()
	return toRet



@webApp.route("/people/<pid>", methods=["DELETE"])
def deletePeople(pid):
	toRet= None
	configFCLocker.acquire(True)
	beaconTableLocker.acquire(True)

	if pid == "" :
		toRet= Response("Beacon id is empty!", status=400, content_type="text/plain")
	elif not beaconTable.has_key (pid) :
		toRet= Response("Beacon with id  ' + pid + '  doesn't exist!", status=400, content_type="text/plain")
	else :
		beaconTable.pop(pid)
		database.delete_device_entries(pid)
		storeConfigurationFile()
		
		# Deleting person
		payload = {
			"action" : "delete",
			"name" : pid,
		}
		brokerAddress = configFileContent["broker-ip"]
		publisher.single (pubTopic, json.dumps(payload), hostname=brokerAddress)

		toRet= Response('', status=200, content_type="application/json")
	beaconTableLocker.release()
	configFCLocker.release()
	return toRet








def on_message(client, userdata, message):
	"""
		Broker callback once a msg is received
	"""

	jsonMsg = json.loads(message.payload.decode("utf-8"))
	beaconTableLocker.acquire(True)

	for b in jsonMsg["map"] :
		if beaconTable.has_key(b) :
			beaconTable[b].addMeasure(jsonMsg["station-id"],  jsonMsg["map"][b])
		
	beaconTableLocker.release()
	"""
		forma del payload
		{
			"stid" : value
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

	global beaconTable
	global beaconTableLocker
	global database
	global configFileContent
	global configFCLocker
	global configFileName
	global pubTopic


	print ("Initializing server")
	configFileName= sys.argv[1]
	configFileContent = json.load(open(configFileName))
	#print(json.dumps(configFileContent))

	beaconTable = dict()
	beaconTableLocker = Lock()
	configFCLocker= Lock()

	tmpIds= []
	for p in configFileContent["positions"] :
		tmpIds.append (p)

	for b in configFileContent["devices"] :
		beaconTable[b]= BeaconInfo(b, tmpIds)

	
	# Instantiate Broker
	broker_address = configFileContent["broker-ip"]
	subTopic = configFileContent["subscribe_topic"]
	pubTopic = configFileContent["publish_topic"]

	print ("Init broker")

	client = mqtt.Client("P1")
	client.connect(broker_address)
	print ("Subscription to " + broker_address + " on topic " + subTopic)
	client.subscribe(subTopic, qos=2)
	client.on_message=on_message
	client.loop_start()

	# Initiate connection with MongoDB
	database = DBInterface(configFileContent["DB_connection_params"])

	# Activate triangulator thread
	triangulate = Triangulate(int(configFileContent["algorithm-interval"]))
	triangulate.daemon = True
	triangulate.start()

    # Activating web-server thread
	webServer= WebServer(webApp, configFileContent["server-ip"], int(configFileContent["server-port"]))
	webServer.daemon = True
	webServer.start()

	
	print ("Starting loop")

	while True:
		time.sleep(1)




if __name__ == "__main__":
	main()
