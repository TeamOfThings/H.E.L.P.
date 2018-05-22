# Usage : sudo python ./sniffer.py <configuration.json>

from bluepy.btle import Scanner, DefaultDelegate
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publisher
import time
import json
import sys
from threading import Thread, Lock

# Global Variables, init with default value
stationId       = ""
devicesArray    = []
brokerIP        = "127.0.0.1"
pubTopic        = ""
subTopic        = ""
scanInterval    = "1"

configFileName  = ""

devLock         = None

# TODO test

############################## Classes ##############################

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

        devLock.acquire(True)

        for e in devicesArray:
            if e == dev.addr:
                self.__sender.addMeasurement(e, dev.rssi)

        devLock.release()


class Sender(Thread):
    """
        Thread sending the data to the server periodically

        Instances:
            __time:	time to wait before sending data
            __map:  the map <beacon, measure_list>
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
        

############################## MQTT callbacks ##############################

def on_message(client, userdata, message):
    """
        Broker callback once a msg is received
        Message struct:
        {
            "action" : "add" / "delete"
            "mac" : "..."
        }
    """

    jsonMsg = json.loads(message.payload.decode("utf-8"))

    action = jsonMsg["action"]
    userMac = jsonMsg["mac"]

    devLock.acquire(True)

    if action == "delete":
        # Remove pair
        for dev in devicesArray:
            if dev == userMac:
                devicesArray.remove(userMac)
                break

        dumpToFile()

    elif action == "add":
        # Add pair
        devicesArray.append(jsonMsg["mac"])
        dumpToFile()

    else :
        print("Invalid code")

    devLock.release()

def on_connect(client, userdata, flags, rc):
    print('connected')


############################## HELPERS ##############################

def dumpToFile():
    """
        Update the file $configFileName
    """
    data = dict()
    data["id"] = stationId
    data["devices"] = devicesArray
    data["broker_ip"] = brokerIP
    data["publish_topic"] = pubTopic
    data["subscribe_topic"] = subTopic
    data["scan_interval"] = scanInterval
    data["send_interval"] = sendInterval

    with open(configFileName, 'w') as outfile:
        json.dump(data, outfile, indent=4)


############################## MAIN ##############################

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


    #####*****#####
    #####*****#####

    global stationId
    global devicesArray
    global brokerIP
    global pubTopic
    global subTopic
    global scanInterval
    global sendInterval

    global configFileName

    global devLock

    stationId    = json_data["id"]
    devicesArray = json_data["devices"]
    brokerIP     = json_data["broker_ip"]
    pubTopic     = json_data["publish_topic"]
    subTopic     = json_data["subscribe_topic"]
    scanInterval = float(json_data["scan_interval"])
    sendInterval = float(json_data["send_interval"])

    configFileName = sys.argv[1]

    devLock     = Lock()

    # Listen to MQTT server's messages
    client = mqtt.Client(stationId)
    client.connect(brokerIP)
    client.subscribe(subTopic, qos=2)
    client.on_message=on_message
    client.loop_start()

    # Start the routine sending the data to the server
    rssiSender = Sender(sendInterval)
    rssiSender.daemon = True

    # Activate BLE Scanner
    scanner = Scanner().withDelegate(ScanDelegate(rssiSender))


    rssiSender.start()


    # Start scanning
    while (True):
        devices = scanner.scan(scanInterval)


if __name__ == "__main__":
    main()
