# H.E.L.P. Home Environment Locating People

Project of Mobile and Cyber Physical Systems, University of Pisa, 2017 / 2018.

This project is conceived and developed by

- [Chiara Baraglia](https://github.com/CB-92)
- [Luca Di Mauro](https://github.com/dima91)
- [Andrea Lisi](https://github.com/0Alic)

Thanks to CNR of Pisa for the hardware.

## Overview

A simple indoor localization system based on wearable BLE tags, with support of a notification system and RESTful service.

## Hardware

This system is tested with this hardware:

- **Wereable BLE tag**: [RadBeacon dot](https://store.radiusnetworks.com/collections/all/products/radbeacon-dot)
- **Stations**: Raspberry PI (with a bluetooth dongle if bluetooth isn't integrated already);
- **Server**: one of our laptops.

## Software

Both stations and server run python scripts, so in all of them a python 2 interpreter is needed. 

**Stations:** to scan for bluetooth messages is used the library [BluePy](http://ianharvey.github.io/bluepy-doc/).

**Server:** the server runs a [MQTT broker](https://medium.com/@erinus/mosquitto-paho-mqtt-python-29cadb6f8f5c), it connects to a [MongoDB](http://api.mongodb.com/python/current/index.html) database and uses [Flask](http://flask.pocoo.org/) as REST api to give the ability of user interaction.

**Server(bot):** a telegram bot developed with [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot).

## More information

### REST API
||GET|POST|DELETE|
|---|---|---|---|
|**/rooms**|Get the list of all rooms|-|-|
|**/rooms/[rn]**|Get list of people in room  **rn**|Create new room **rn**|Delete a room  **rn**|
|**/readings/[bId]**|Get the list of readings about a beacon (grouped by room)|-|Delete ALL readings about a beacon|
|**/peopleList**|get the list of users registered to the service|-|-|
|**/people**|Get list of people locations|-|-|
|**/people/[pId]**|-|Create user **pId**|Delete user **pId**|

### Documentation
https://docs.readthedocs.io/en/latest/index.html

### Software requirements
* https://www.elinux.org/RPi_Bluetooth_LE
* http://ianharvey.github.io/bluepy-doc/
* http://flask.pocoo.org/
* https://medium.com/@erinus/mosquitto-paho-mqtt-python-29cadb6f8f5c
* https://github.com/eclipse/paho.mqtt.python
* https://docs.python.org/2/library/json.html
* https://github.com/python-telegram-bot/python-telegram-bot
* http://api.mongodb.com/python/current/index.html

## TODO
- [ ] Dormire :lollipop:
- [x] ~chiedere la macchina virtuale al chessa~ :disappointed:
- [x] sniffer  : leggere il file di configurazione per settare le variabili
- [X] sniffer  : inviare al broker un messaggio formattato json contenente macAddrBeacon, idRaspberry, RSSI, timestamp :collision:
- [X] analyzer : registrarlo al topic mqtt e raggruppare i dati per macAddrBeacon[].idRaspberry[]
- [X] analyzer : trovare un algoritmo di triangolazione (leggere bene su RSSI distanza stimata), per esempio media pesata con maggior peso alla stazione da cui abbiamo ricevuto più messaggi (perché magari le altre sono fuori portata / al di là di un ostacolo) , varianza :tractor:
- [x] analyzer : creare logFile per quando riceve messaggi (on_message) 
- [ ] ~**Se c'è tempo** analyzer : raffinare algoritmo di localizzazione~
- [ ] ~**Raffinamento** perimetro di misure agli angoli delle stanze~
- [ ] ~**Raffinamento++** definirsi una fingermap di misure per le stanze in cui non abbiamo una stazione~


- [X] **MANDATORY** RESTful : scrivere il API servizio (soprattutto pensare alla fase di installazione ed aggiunta di nuovi dispositivi / attori)
- [X] **MANDATORY** bot telegram
- [ ] **BOT** aggiungere command list da BotFather
