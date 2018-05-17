# Usage : sudo python ./sniffer.py <configuration.json>

from bluepy.btle import Scanner, DefaultDelegate
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publisher
import time
import json
import sys
from threading import Thread

# Global Variables, init with default value
stationId       = ""
position        = ""
devicesArray    = []
brokerIP        = "127.0.0.1"
pubTopic           = ""
subTopic           = ""
scanInterval    = "1"


class ScanDelegate(DefaultDelegate):
    """
        Class for the bluetooth interface
        As soon as it reads a new value, it gives it to the sender who collect them

        Instances:
            __sender: a reference to the sender thread
    """
    def __init__(self, sender):
        DefaultDelegate.__init__(self)
        self.__sender = sender


    # Scan methods
    def handleDiscovery(self, dev, isNewDev, isNewData):
        """
            handler after discovered new device
        """

        for e in devicesArray:
            if e["mac"] == dev.addr:
                self.__sender.addMeasurement(e["name"], dev.rssi)



class Sender(Thread):
    """
        Thread sending the data to the server periodically

        Instances:
            __time:	time to wait before sending data
            __map:  the map <beacon, measure_list>

        Doing in this way, instead of sending an rssi as soon as we get it, the logic becomes more complex:
        the station needs to store the entire list of sniffed rssis, and these can come from different beacons;
        so that's why the station needs a map and should send it. The server should, then, unpack it
    """

    def __init__(self, time):
        Thread.__init__(self)
        self.__time = time 
        self.__map = {}
	

    def run(self):
        while(True):
            time.sleep(self.__time)
            payload = self.__buildPayload(self.__map)
            print payload
            publisher.single(pubTopic, payload, hostname=brokerIP)
            self.__map = {} # reset map
            

    def addMeasurement(self, name, rssi):
        if not self.__map.has_key(name):
            self.__map[name] = []

        self.__map[name].append(int(rssi))


    def __buildPayload(self, map):
        payload = {}
        payload["station-id"] = str(stationId)
        payload["map"] = map

        return json.dumps(payload)
        


def on_message(client, userdata, message):
	"""
		Broker callback once a msg is received
	"""

	jsonMsg = json.loads(message.payload.decode("utf-8"))
    # Update my data
        # I receive a new pair <user - beaconMAC>
    userName = jsonMsg["name"]
    userMAC = jsonMsg["mac"]


def on_connect(client, userdata, flags, rc):
    print('connected')


def main():
    """
        Usage:
            sudo python sniffer.py station.json

            sudo:           important!!
            station.json:   configuration file for the environment setup
    """
    scanner = None
    json_data = None

    if len(sys.argv) != 2:
        sys.exit("Wrong number of arguments")

    print ("Initializing station")
    json_data = json.load(open(sys.argv[1]))

    rssiSender = Sender(float(json_data["send-interval"]))
    rssiSender.daemon = True

    scanner = Scanner().withDelegate(ScanDelegate(rssiSender))


    #####*****#####
    #####*****#####

    global stationId
    global devicesArray
    global brokerIP
    global pubTopic
    global subTopic
    global scanInterval

    stationId    = json_data["id"]
    devicesArray = json_data["devices"]
    brokerIP     = json_data["broker-ip"]
    pubTopic     = json_data["publish_topic"]
    subTopic     = json_data["subscribe_topic"]
    scanInterval = float(json_data["scan_interval"])

    # Listen to MQTT server's messages
    client = mqtt.Client("P1")
    client.connect(brokerIP)
    client.subscribe(subTopic)
    client.on_message=on_message
    client.loop_start()

    # Start the routine sending the data to the server
    rssiSender.start()

    # Start scanning
    while (True):
        devices = scanner.scan(scanInterval)


if __name__ == "__main__":
    main()
