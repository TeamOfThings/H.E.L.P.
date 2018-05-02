import paho.mqtt.client as mqtt
import paho.mqtt.publish as publisher
import time
import json
import numpy


beaconTable = {}

class BeaconInfo():
	"""
		Class for a beacon
	"""


	def __init__(self, id):
		self.__map = dict()
		self.__id = id


	def getMap(self):
		return self.__map


	def getId(self):
		return self.__id


	def addMeasure(self, room, measure):
		"""
			Add a received measure from a given room
		"""
		
		if not self.__map.has_key(room):
			self.__map[room] = []
			print("NEW ROOOM " + room)

		self.__map[room].append(int(measure))
		print("NEW MEASUS " + measure)


# tabella per ogni rasperry, per ogni beacon ricevuto
	# Determinare dimensione max tabella (ie quando fare triangolazione)
	# fare triangolazione



# Salvarci gli rssi
#

def on_message(client, userdata, message):
	"""
		Broker callback once a msg is received
	"""

	s = str(message.payload.decode("utf-8"))
	jsonMsg = json.loads(s)

	beaconTable[jsonMsg["name"]].addMeasure(str(jsonMsg["position"]), str(jsonMsg["rssi"]))


	# Salvati le cose

	# Deidere quando fare la triangolazione , luca  stupido lol


def main():

	global beaconTable

	beaconTable = dict()
	beaconTable["nerfgun"] = BeaconInfo("nerfgun")


	broker_address = "localhost" 
	topic = "update/sensors"

	print ("Init broker")

	client = mqtt.Client("P1")
	client.connect(broker_address)
	client.subscribe(topic)
	client.on_message=on_message
	client.loop_start()

	print ("Starting loop")

	while True:
		time.sleep(1)




if __name__ == "__main__":
	main()
