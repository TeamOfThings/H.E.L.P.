# Locator Used by Chiara and Andrea (L.U.C.A)

**Notice: sniffer program have to be executed as root!**

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

### REST API
||GET|POST|DELETE|
|---|---|---|---|
|**/rooms/**|Get the list of all rooms|-|-|
|**/rooms/[rid]**|-|Create new room (given as parameter)|Delete a room (given as parameter)|
|**/readings/[bId]**|Get the list of readings about a beacon (grouped by room)|-|Delete ALL readings about a beacon|
|**/people/[rId]**|Get list of people locations|-|-|
|**/people/[rId]**|Get the list of people (iBeacon) in the selected room|-|-|

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
