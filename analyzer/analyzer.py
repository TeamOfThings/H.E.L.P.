import paho.mqtt.client as mqtt
import paho.mqtt.publish as publisher
import time
import json
import numpy

from threading import Thread

"""
	beacon dictionary <name, BeaconInfo>
"""
beaconTable = {}


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
			print("Thread computing")
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



def on_message(client, userdata, message):
	"""
		Broker callback once a msg is received
	"""

	jsonMsg = json.loads(str(message.payload.decode("utf-8")))

	beaconTable[jsonMsg["name"]].addMeasure(str(jsonMsg["position"]), str(jsonMsg["rssi"]))


def main():
	"""
		Main
	"""

	global beaconTable

	beaconTable = dict()
	beaconTable["nerfgun"] = BeaconInfo("nerfgun")
	beaconTable["luca"] = BeaconInfo("luca")
	beaconTable["chiara"] = BeaconInfo("chiara")
	beaconTable["andrea"] = BeaconInfo("andrea")
	#####
	# TODO: prendere questi dati da un file prodotto da una precedente fase di installazione o in altro modo salvato 
	#####
	
	# Instantiate Broker
	broker_address = "localhost" 
	topic = "update/sensors"

	print ("Init broker")

	client = mqtt.Client("P1")
	client.connect(broker_address)
	client.subscribe(topic)
	client.on_message=on_message
	client.loop_start()

	# Activate triangulator thread
	triangulate = Triangulate(5)
	triangulate.daemon = True
	triangulate.start()

	print ("Starting loop")

	while True:
		time.sleep(1)




if __name__ == "__main__":
	main()
