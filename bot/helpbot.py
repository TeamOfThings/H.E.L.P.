"""
    Timer Bot to send timed Telegram messages

    Classes
        Bot: Bot handler
        JobQueue: Send timed messages

    Press CTRL-Z to stop the bot
"""

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import InlineQueryHandler

import logging, sys, json
import requests

from pyzbar.pyzbar import decode
from PIL import Image


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# HTTP Status code
OKGET = 200
OKPOST = 201
OKDELETE = 200

def error(bot, update, error):
    """ Helper function: Display error messages """
    logger.warning('Update "%s" caused error "%s"', update, error)


#### MESSAGES ####
# TODO fare la post di utente e mac address
def getImage(bot, update):

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
                last_address = text[-1].data
                name = update.message.caption
                update.message.reply_text('Decoded message is: '+last_address+"\n\n"+"User "+name+" associated to Mac Address "+last_address)

    except (IndexError, ValueError):
        update.message.reply_text('Inserire messaggio di errore')



#### LINE COMMANDS ####

# TODO scrivere meglio messaggi di HTTP error, e non "error" come sto facendo adesso, paxxerellino pigrotto XDXD asdasd

def help(bot, update):
    """ Bot LineCommand: /start or /help """

    startText = 'Hi! I am L.U.C.A. bot\n' \
                '\n'\
                'Ask me about your indoor localization system:\n' \
                'Commands:\n' \
                '/getUser <user> to see in which room is the user;\n' \
                '/getUsers to see the position of all users;\n' \
                '/roomList to see the list of your rooms;\n' \
                '/getRoom <room> to see who is in that room;\n' \
                '\n'\
                'Maybe do you want me to add some new things to your system?\n' \
                'Commands:\n' \
                'If you want to add a new user send me a picture of the QR code on the device that you want to associate with that user and specify in the caption the name of the new user.\n'\
                '/addUser <newUser> to add a new user in your system;\n' \
                '/addRoom <newRoom> to add a new room in your system;\n' \
                '\n'\
                'Or do you want me to remove somethings/one from your system?\n' \
                'Commands:\n' \
                '/deleteUser <user> to remove a user from your system;\n' \
                '/deleteRoom <room> to remove a room from your system;\n' \
                '\n'\
                'Anyway, write /help to display this message again.\n' \

    update.message.reply_text(startText)

#######################################   GET   #######################################


########## Single User

def getUser(bot, update, args, chat_data):
    """
        Get a user location
    """

    try:
        user = args[0]
        req = requests.get('http://192.168.1.78:8080/people')

        if(req.status_code == OKGET):
            txt = user + " not at home"
            msg = req.json()
            if user in msg.keys():
                txt = str(user) + " in " + str(msg[user])

            update.message.reply_text(txt)
        else :
            update.message.reply_text("Connection error")

    except (IndexError, ValueError):
        update.message.reply_text('Use /getUser <user>')


########## All Users

def getUsers(bot, update):
    """
        Get all user locations
    """

    try:
        req = requests.get('http://192.168.1.78:8080/people')

        if(req.status_code == OKGET):
            txt = ""
            msg = req.json()
            for b in msg:
                txt += str(b) + " in " + str(msg[b]) + "\n"

            update.message.reply_text(txt)
        else :
            update.message.reply_text("Connection error")

    except (IndexError, ValueError):
        update.message.reply_text('Use /getUsers')


########## Room List

def getRoomList(bot, update):
    """
        Get the list of the rooms
    """

    try:
        r = requests.get('http://192.168.1.78:8080/rooms')

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
        update.message.reply_text('Use /roomList')


########## Users in a Room

def getRoom(bot, update, args, chat_data):
    """
        Get the users in a room
    """

    try:
        room = args[0]
        r = requests.get('http://192.168.1.78:8080/rooms/'+room)

        if r.status_code == OKGET:

            msg = r.json()
            txt = ""
            for user in msg:
                txt += str(user) + "\n"

            if txt == "":
                txt = "No one in " + room

            update.message.reply_text(txt)

        else :
            update.message.reply_text("Connection error")

    except (IndexError, ValueError):
        update.message.reply_text('Use /getRoom <room>')


#######################################   POST   #######################################

########## NEW User

def addUser(bot, update, args):
    """
        Add a user to the system 
    """

    try:
        user = args[0]

        update.message.reply_text("Added " + user)
        """
        r = requests.post('http://192.168.1.78:8080/rooms/'+room)

        if r.status_code == OKPOST:

            update.message.reply_text("Added " + room)
        else :
            update.message.reply_text("Connection error")
        """
    except (IndexError, ValueError):
        update.message.reply_text('Use /addUser <newUser>')


########## NEW Room

def addRoom(bot, update, args):
    """
        Add a room to the system 
    """

    try:
        room = args[0]

        update.message.reply_text("Added " + room)
        """
        r = requests.post('http://192.168.1.78:8080/rooms/'+room)

        if r.status_code == OKPOST:

            update.message.reply_text("Added " + room)
        else :
            update.message.reply_text("Connection error")
        """
    except (IndexError, ValueError):
        update.message.reply_text('Use /addRoom <newRoom>')


#######################################   DELETE   #######################################

########## DELETE User

def deleteUser(bot, update, args):
    """
        Delete a user from the system 
    """

    try:
        user = args[0]

        update.message.reply_text("Removed " + user)
        """
        r = requests.delete('http://192.168.1.78:8080/rooms/'+room)

        if r.status_code == OKDELETE:

            update.message.reply_text("Removed " + user)
        else :
            update.message.reply_text("Connection error")
        """
    except (IndexError, ValueError):
        update.message.reply_text('Use /deleteUser <user>')


########## DELETE Room

def deleteRoom(bot, update, args):
    """
        Delete a user from the system 
    """

    try:
        room = args[0]

        update.message.reply_text("Removed " + room)
        """
        r = requests.delete('http://192.168.1.78:8080/rooms/'+room)

        if r.status_code == OKDELETE:

            update.message.reply_text("Removed " + room)
        else :
            update.message.reply_text("Connection error")
        """
    except (IndexError, ValueError):
        update.message.reply_text('Use /deleteRoom <room>')


#### MAIN ####


def main():
    global waiting_for_name
    global last_address

    if len(sys.argv) != 2 :
        sys.exit("Wrong number of arguments!\n\tExiting")

    jsonData = json.load(open(sys.argv[1]))

    helpbot=jsonData["token"]
    updater = Updater(helpbot)
    dispatcher = updater.dispatcher

    waiting_for_name = False
    last_address = None

    # Add commands to the bot
    dispatcher.add_handler(CommandHandler("start", help))
    dispatcher.add_handler(CommandHandler("help", help))
    
    dispatcher.add_handler(CommandHandler("getUser", getUser, pass_args=True, pass_chat_data=True))
    dispatcher.add_handler(CommandHandler("getUsers", getUsers))
    dispatcher.add_handler(CommandHandler("roomList", getRoomList))    
    dispatcher.add_handler(CommandHandler("getRoom", getRoom, pass_args=True, pass_chat_data=True))

    dispatcher.add_handler(CommandHandler("addUser", addRoom, pass_args=True))
    dispatcher.add_handler(CommandHandler("addRoom", addUser, pass_args=True))

    dispatcher.add_handler(CommandHandler("deleteUser", deleteUser, pass_args=True))
    dispatcher.add_handler(CommandHandler("deleteRoom", deleteRoom, pass_args=True))

    # Handler for messages which are a photo
    dispatcher.add_handler(MessageHandler(Filters.photo, getImage))

    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()