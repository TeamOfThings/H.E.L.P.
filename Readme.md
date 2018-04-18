# Locator Used by Chiara and Andrea (L.U.C.A)

**Notice: sniffer program have to be executed as root!**

### Software requirements
* https://www.elinux.org/RPi_Bluetooth_LE
* http://ianharvey.github.io/bluepy-doc/
* http://flask.pocoo.org/
* https://medium.com/@erinus/mosquitto-paho-mqtt-python-29cadb6f8f5c
* https://github.com/eclipse/paho.mqtt.python
* https://docs.python.org/2/library/json.html

## TODO
- [ ] Dormire
- [x] ~chiedere la macchina virtuale al chessa~
- [ ] sniffer  : leggere il file di configurazione per settare le variabili
- [ ] sniffer  : inviare al broker un messaggio formattato json contenente macAddrBeacon, idRaspberry, RSSI, timestamp (?)
- [ ] analyzer : registrarlo al topic mqtt e raggruppare i dati per macAddrBeacon[].idRaspberry[]
- [ ] analyzer : todo
