import paho.mqtt.client as mqtt
import paho.mqtt.publish as publisher
import time
import json

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

	# Salvati le cose

	# Deidere quando fare la triangolazione , luca è stupido lol

	

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
