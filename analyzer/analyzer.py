import paho.mqtt.client as mqtt
import paho.mqtt.publish as publisher
import time

def on_message(client, userdata, message):
	"""
		Broker callback once a msg is received
	"""
	print("message received ", str(message.payload.decode("utf-8")))
	print("topic: ", message.topic)
	print("qos: ", message.qos)
	print("message retain flag", message.retain)
	

broker_address = "localhost" 
topic = "update/sensors"

client = mqtt.Client("P1")
client.connect(broker_address)
client.subscribe(topic)
client.on_message=on_message
client.loop_start()

while True:
	time.sleep(1)
