import paho.mqtt.client as mqtt
import paho.mqtt.publish as publisher
import time
import json
import numpy
import sys
from flask import Flask, abort, Response 
from threading import Thread

"""
	beacon dictionary <name, BeaconInfo>
"""
beaconTable = {}

"""
    Instance of web-server
"""
webApp = Flask(__name__)



class Triangulate(Thread):
	"""
		Thread performing the triangulation
	
		Instances:
			__time:	time to wait before performing triagulation

		##### 
		# TODO (nota): ho pensato ad un thread cosi' che ogni "IntervalloDiTempo" faccia la triangolazione, ed il main continua a raccogliare dati
		#####
	"""

	def __init__(self, time):
		Thread.__init__(self)
		self.__time = time

	
	def run(self):
		while(True):
			time.sleep(self.__time)
			print("TODO: Thread computing")
			#####
			# TODO: Inserire qui codice di triangolazione
			#####



class BeaconInfo():
	"""
		Class for a beacon

		Instances:
			__map: 	a dictionary map <room, measure_list>
			__id:	Beacon's id
			__last:	last room a person was detected
	"""


	def __init__(self, id):
		self.__map = dict()
		self.__id = id
		self.__last = ""


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
		
		if not self.__map.has_key(room):
			self.__map[room] = []

		self.__map[room].append(int(measure))


	def cleanInfo(self):
		"""
			Clean the current (rssi) values from the map
		"""
		self.__map = self.__map.fromkeys(self.__map, [])



class WebServer(Thread):
    """
        Thread running the web server
    """

    def __init__(self, app, port):
        Thread.__init__(self)
        self.__flaskApp= app
        self.__port= port


    def run(self):
        self.__flaskApp.run("0.0.0.0", self.__port)


## Routing rules for web server thread
@webApp.route('/')
def root():
    return Response("Welcome to REST API!", status=200, content_type="text/plain")

#####
#####     /rooms
@webApp.route("/rooms", methods=["GET"])
def roomsGet():
    rooms= {}
    return Response('["list of all rooms"]', status=200, content_type="application/json")

#####
#####     /rooms/<rid>
@webApp.route("/rooms/<rid>", methods=['POST'])
def postRooms(rid):
    return Response("Creating room " + rid, status=201, content_type="test/plain")

@webApp.route("/rooms/<rid>", methods=['DELETE'])
def deleteRooms(rid):
    return Response("Deleting room " + rid, status=200, content_type="test/plain")

#####
#####     /readings/<bid>
@webApp.route("/readings/<bid>", methods=['GET'])
def getReadings(bid):
    return Response("Retrieving all readings about a beacon grouped by rooms (json object of json array)", status=200, content_type="test/plain")

@webApp.route("/readings/<bid>", methods=['DELETE'])
def deleteReadings(bid):
    return Response("Deleting readings for " + bid, status=200, content_type="test/plain")

#####
#####     /people/<rid>
@webApp.route("/people/<rid>", methods=["GET"])
def getPeople(rid):
    return Response('["list of people in a room"]', status=200, content_type="application/json")



def on_message(client, userdata, message):
	"""
		Broker callback once a msg is received
	"""

	jsonMsg = json.loads(str(message.payload.decode("utf-8")))
	print(jsonMsg)
	#beaconTable[jsonMsg["name"]].addMeasure(str(jsonMsg["position"]), str(jsonMsg["rssi"]))
	#####
	# TODO: Spacchettare il payload ricevuto, decidere come salvarsi i dati per il thread Triangulate
	#####
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
	beaconTable = dict()
	for b in jsonData["devices"] :
		beaconTable[b]= BeaconInfo(b)
	#print (beaconTable)
	
	# Instantiate Broker
	broker_address = jsonData["broker-ip"]
	topic = jsonData["topic"]

	print ("Init broker")

	client = mqtt.Client("P1")
	client.connect(broker_address)
	client.subscribe(topic)
	client.on_message=on_message
	client.loop_start()

	# Activate triangulator thread
	triangulate = Triangulate(int(jsonData["algorithm-interval"]))
	triangulate.daemon = True
#	triangulate.start()

    # Activating web-server thread
	webServer= WebServer(webApp, int(jsonData["listening-port"]))
	webServer.daemon = True
#	webServer.start()

	print ("Starting loop")

	while True:
		time.sleep(1)




if __name__ == "__main__":
	main()
