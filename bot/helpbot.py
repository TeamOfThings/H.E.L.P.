"""
    Timer Bot to send timed Telegram messages

    Classes
        Bot: Bot handler
        JobQueue: Send timed messages

    Press CTRL-Z to stop the bot
"""
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import InlineQueryHandler

import logging, sys, json
import requests

from pyzbar.pyzbar import decode
from PIL import Image

import re


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

ip_address = ""

# HTTP Status code
OKGET = 200
OKPOST = 201
OKDELETE = 200

# Patterns
mac_pattern = "^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"
station_pattern = "^([0-9A-Fa-f]{6})$"

def error(bot, update, error):
    """ Helper function: Display error messages """
    logger.warning('Update "%s" caused error "%s"', update, error)



#### LINE COMMANDS ####

# TODO scrivere meglio messaggi di HTTP error, e non "error" come sto facendo adesso, paxxerellino pigrotto XDXD asdasd

def help(bot, update, chat_data):
    """ Bot LineCommand: /start or /help """

    startText = 'Hi! I am HELPbot\n' \
                '\n\n'\
                'Ask me some *information* about your indoor localization system:\n\n' \
                '_Commands_:\n' \
                '/whereis <user> to see in which room is the user;\n' \
                '/whereareall to see the position of all users;\n' \
                '/roomlist to see the list of your rooms;\n' \
                '/userlist to see the list of registered users;\n' \
                '/whoisin <room> to see who is in that room;\n' \
                '\n\n'\
                'Maybe do you want me to *add* some new things to your system?\n\n' \
                '_Commands_:\n' \
                'To add a new user send me a picture of the QR code on the device that you want to associate with that user and specify in the caption the name of the new user;\n'\
                'To add a new station send me a picture of the QR code on the station that you want to associate with that room and specify in the caption the name of the room;\n'\
                '\n\n'\
                'Or do you want me to *remove* something/one from your system?\n\n' \
                '_Commands_:\n' \
                '- /deleteuser <user> to remove a user from your system;\n' \
                '- /deleteroom <room> to remove a room from your system;\n' \
                '\n\n'\
                'Anyway, write /help to display this message again.\n' \

    chat_id = update.message.chat_id
    bot.send_message(chat_id, startText, parse_mode=telegram.ParseMode.MARKDOWN)

#######################################   GET   #######################################

########## User List
def getUserList(bot, update):
    """
        Get the list of all the users
    """
    try:
        req = requests.get('http://'+ip_address+':8080/peopleList')

        if(req.status_code == OKGET):
            txt = ""
            msg = req.json()
            for b in msg:
                txt += str(b) + "\n"

            update.message.reply_text(txt)
        else :
            update.message.reply_text("Connection error")

    except (IndexError, ValueError):
        update.message.reply_text('Use /userlist')



########## Single User

def getUser(bot, update, args, chat_data):
    """
        Get a user location
    """

    try:
        user = args[0]
        req = requests.get('http://'+ip_address+':8080/people')

        if(req.status_code == OKGET):
            txt = user + " not at home"
            msg = req.json()
            if user in msg.keys():
                txt = str(user) + " in " + str(msg[user])

            update.message.reply_text(txt)
        else :
            update.message.reply_text("Connection error")

    except (IndexError, ValueError):
        update.message.reply_text('Use /whereis <user>')


########## All Users

def getUsers(bot, update):
    """
        Get all user locations
    """

    try:
        req = requests.get('http://'+ip_address+':8080/people')

        if(req.status_code == OKGET):
            txt = ""
            msg = req.json()
            for b in msg:
                txt += str(b) + " in " + str(msg[b]) + "\n"

            update.message.reply_text(txt)
        else :
            update.message.reply_text("Connection error")

    except (IndexError, ValueError):
        update.message.reply_text('Use /whereareall')


########## Room List

def getRoomList(bot, update):
    """
        Get the list of the rooms
    """

    try:
        r = requests.get('http://'+ip_address+':8080/rooms')

        if r.status_code == OKGET:
            msg = r.json()
            txt = ""
            for room in msg:
                txt += str(room) + "\n"

            if txt == "":
                txt = "No registered rooms in your service"

            update.message.reply_text(txt)
        else :
            update.message.reply_text("Connection error")
            
    except (IndexError, ValueError):
        update.message.reply_text('Use /roomlist')


########## Users in a Room

def getRoom(bot, update, args, chat_data):
    """
        Get the users in a room
    """

    try:
        room = args[0]
        r = requests.get('http://'+ip_address+':8080/rooms/'+room)

        if r.status_code == OKGET:

            msg = r.json()
            txt = ""
            for user in msg:
                txt += str(user) + "\n"

            if txt == "":
                txt = "No one in " + room

            update.message.reply_text(txt)
        
        elif r.content == "Room is empty":
            update.message.reply_text("You didn't specify the room!")
        
        elif r.content == "Requested room doesn't exists":
            update.message.reply_text("Requested room doesn't exists!\nTry again!")

        else :
            update.message.reply_text("Connection error")

    except (IndexError, ValueError):
        update.message.reply_text('Use /whoisin <room>')


#######################################   POST   #######################################


########## NEW User

def add(bot, update):


    try:
        if update.message.photo is None:
            update.message.reply_text('no foto')
        elif update.message.caption is None:
            update.message.reply_text("Missing caption")
        else:
            img_id = update.message.photo[-1].file_id
            newFile = bot.get_file(img_id)
            newFile.download('qrcode.png')

            text = decode(Image.open("qrcode.png"))
            
            if len(text) == 0:
                update.message.reply_text("No QR code found!")
            else:
                name = update.message.caption
                data = text[-1].data

                if re.match(mac_pattern, data):
                    # QR code content is a mac address
                    r = requests.post('http://'+ip_address+':8080/people/'+name, data=data)
                    if r.status_code == OKPOST:
                        update.message.reply_text("User "+name+" associated to Mac Address "+data)
                    elif r.content=="Beacon with id  " + name + "  already exists!":
                        update.message.reply_text("User "+name+" is already associated with a device!\nTry again!")
                    elif r.content=="Mac address  " + data + "  already in use!":
                        update.message.reply_text("This device is already associated to an user!")
                    else :
                        update.message.reply_text("Connection error: "+ r.content)
                elif re.match(station_pattern, data):
                    # QR code content is a station id
                    r = requests.post('http://'+ip_address+':8080/rooms/'+name, data=data)
                    if r.status_code == OKPOST:
                        update.message.reply_text("Room: "+name+" associated to station "+data)
                    elif r.content=="Requested room already exists!":
                        update.message.reply_text("Room "+name+" already exist!")
                    elif r.content=="Station id already associated!":
                        update.message.reply_text("This station is already associated to a room!")
                    else:
                        update.message.reply_text("Connection error: "+r.content)
                else:
                    # QR code doesn't match any pattern
                    update.message.reply_text("QR code format not supported.")
               
                

    except (IndexError, ValueError):
        update.message.reply_text('Inserire messaggio di errore')


#######################################   DELETE   #######################################

########## DELETE User

def deleteUser(bot, update, args):
    """
        Delete a user from the system 
    """

    try:
        user = args[0]

        #update.message.reply_text("Removed " + user)
        
        r = requests.delete('http://'+ip_address+':8080/people/'+user)

        if r.status_code == OKDELETE:
            update.message.reply_text("Removed " + user)
        elif r.content=="Beacon id is empty!":
            update.message.reply_text("Please specify the user you want to delete.")
        elif r.content=="Beacon with id  " + user + "  doesn't exist!":
            update.message.reply_text("This user is not associated to any device.")
        else :
            update.message.reply_text("Connection error")
        
    except (IndexError, ValueError):
        update.message.reply_text('Use /deleteuser <user>')


########## DELETE Room

def deleteRoom(bot, update, args):
    """
        Delete a user from the system 
    """

    try:
        room = args[0]

        r = requests.delete('http://'+ip_address+':8080/rooms/'+room)

        if r.status_code == OKDELETE:
            update.message.reply_text("Removed " + room)
        elif r.content=="Room name is empty!":
            update.message.reply_text("You didn't specify the name of the room you want to delete.")
        elif r.content=="Room name  " + room + "  doesn't exist!":
            update.message.reply_text("Room "+room+" doesn't exist!")
        else :
            update.message.reply_text("Connection error")
        
    except (IndexError, ValueError):
        update.message.reply_text('Use /deleteroom <room>')


#### MAIN ####


def main():
    global ip_address

    if len(sys.argv) != 2 :
        sys.exit("Wrong number of arguments!\n\tExiting")

    jsonData = json.load(open(sys.argv[1]))

    helpbot=jsonData["token"]
    updater = Updater(helpbot)
    dispatcher = updater.dispatcher

    ip_address = jsonData["ip_address"]

    # Add commands to the bot
    dispatcher.add_handler(CommandHandler("start", help, pass_chat_data=True))
    dispatcher.add_handler(CommandHandler("help", help, pass_chat_data=True))
    
    dispatcher.add_handler(CommandHandler("whereis", getUser, pass_args=True, pass_chat_data=True))
    dispatcher.add_handler(CommandHandler("whereareall", getUsers))
    dispatcher.add_handler(CommandHandler("userlist", getUserList))
    dispatcher.add_handler(CommandHandler("roomlist", getRoomList))    
    dispatcher.add_handler(CommandHandler("whoisin", getRoom, pass_args=True, pass_chat_data=True))

    dispatcher.add_handler(CommandHandler("deleteuser", deleteUser, pass_args=True))
    dispatcher.add_handler(CommandHandler("deleteroom", deleteRoom, pass_args=True))

    # Handler for messages which are a photo
    dispatcher.add_handler(MessageHandler(Filters.photo, add))

    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()