from bluepy.btle import Scanner, DefaultDelegate
import paho.mqtt.client
import paho.mqtt.publish as publisher
import json

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print "Discovered device",  dev.addr,  " -> ", dev.rssi
            publisher.single('update/sensors', dev.rssi, hostname='127.0.0.1')
        elif isNewData:
            print "Received new data from", dev.addr, " -> ", dev.rssi

scanner = Scanner().withDelegate(ScanDelegate())







def on_connect(client, userdata, flags, rc):
    print('connected')

while(True):
	devices = scanner.scan(1)
	
	#for dev in devices:
	#	print "Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi)
	#	for (adtype, desc, value) in dev.getScanData():
	#		print "  %s = %s" % (desc, value)
