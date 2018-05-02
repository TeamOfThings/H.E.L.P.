import paho.mqtt.client as mqtt
import paho.mqtt.publish as publisher
import time
import json

# Salvarci gli rssi

def on_message(client, userdata, message):
	"""
		Broker callback once a msg is received
	"""

	s = str(message.payload.decode("utf-8"))
	print(s)
	jsonMsg = json.loads(s)
#	print(jsonMsg)

	# Calcola

#	print("topic: ", message.topic)
#	print("qos: ", message.qos)
#	print("message retain flag", message.retain)
	

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
