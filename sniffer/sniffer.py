# Usage : sudo python ./sniffer.py <configuration.json>

from bluepy.btle import Scanner, DefaultDelegate
import paho.mqtt.client
import paho.mqtt.publish as publisher
import json
import sys

devicesArray = []


### ####
### MAIN
def main():
    scanner = None
    json_data = None

    print ("Hello client!")
    if len(sys.argv) != 2:
        sys.exit("Wrong numer of arguments")

    print ("Initializing station..")
    scanner = Scanner().withDelegate(ScanDelegate())

    json_data = json.load(open(sys.argv[1]))

    #####*****#####
    #####*****#####

    global devicesArray
    print ("Station ID is: " + json_data["id"])
    devicesArray = json_data["devices"]

    while (True):
        devices = scanner.scan(float(json_data["scan_interval"]))
    ## Test code..


# for dev in devices:
#	print "Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi)
#	for (adtype, desc, value) in dev.getScanData():
#		print "  %s = %s" % (desc, value)


class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            for e in devicesArray:
                if e["mac"] == dev.addr:
                    print "Name: ", e["name"], "\tRSSI: ", dev.rssi
        # publisher.single('hello', dev.rssi, hostname='192.168.1.75')
    # elif isNewData:
    #    print "Received new data from", dev.addr, " -> ", dev.rssi'''


def on_connect(client, userdata, flags, rc):
    print('connected')


if __name__ == "__main__":
    main()
