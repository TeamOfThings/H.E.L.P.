# Usage : sudo python ./sniffer.py <configuration.json>

from bluepy.btle import Scanner, DefaultDelegate
import paho.mqtt.client
import paho.mqtt.publish as publisher
import json
import sys

# Global Variables, init with default value
stationId       = ""
position        = ""
devicesArray    = []
brokerIP        = "127.0.0.1"
topic           = ""
scanInterval    = "1"


def main():
    """
        Usage:
            sudo python sniffer station.json

            sudo:           important!!
            station.json:   configuration file for the environment setup
    """
    scanner = None
    json_data = None

    if len(sys.argv) != 2:
        sys.exit("Wrong number of arguments")

    print ("Initializing station")
    scanner = Scanner().withDelegate(ScanDelegate())

    json_data = json.load(open(sys.argv[1]))

    #####*****#####
    #####*****#####

    global stationId
    global position
    global devicesArray
    global brokerIP
    global topic
    global scanInterval

    stationId    = json_data["id"]
    position     = json_data["position"]
    devicesArray = json_data["devices"]
    brokerIP     = json_data["broker-ip"]
    topic        = json_data["topic"]
    scanInterval = float(json_data["scan_interval"])

    while (True):
        devices = scanner.scan(scanInterval)


class ScanDelegate(DefaultDelegate):
    """
        Class for the bluetooth intervace
    """
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        """
            handler after discovered new device
        """

        for e in devicesArray:
            if e["mac"] == dev.addr:
                payload = buildStringPayload(e["name"], dev.rssi)
                print payload
                publisher.single(topic, payload, hostname=brokerIP)


def on_connect(client, userdata, flags, rc):
    print('connected')


def buildStringPayload(name, rssi):
    """
        Build the payload of our beacon frame
    """
    payload = {}
    payload["station-id"] = str(stationId)
    payload["position"] = str(position)
    payload["name"] = str(name)
    payload["rssi"] = str(rssi)

    return json.dumps(payload)


if __name__ == "__main__":
    main()
