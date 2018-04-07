# Usage : sudo python ./sniffer.py <configuration.json>

from bluepy.btle import Scanner, DefaultDelegate
import paho.mqtt.client
import paho.mqtt.publish as publisher
import json

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print "MAC Address: ",  dev.addr,  " RSSI: ", dev.rssi
            publisher.single('hello', dev.rssi, hostname='192.168.1.75')
       #elif isNewData:
        #    print "Received new data from", dev.addr, " -> ", dev.rssi'''

scanner = Scanner().withDelegate(ScanDelegate())

def on_connect(client, userdata, flags, rc):
    print('connected')

while(True):
	devices = scanner.scan(0.5)
	
	#for dev in devices:
	#	print "Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi)
	#	for (adtype, desc, value) in dev.getScanData():
	#		print "  %s = %s" % (desc, value)
