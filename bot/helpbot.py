"""
    Timer Bot to send timed Telegram messages

    Classes
        Bot: Bot handler
        JobQueue: Send timed messages

    Press CTRL-Z to stop the bot
"""

from telegram.ext import Updater, CommandHandler
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import InlineQueryHandler

import logging, sys, json
import requests

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)



def error(bot, update, error):
    """ Helper function: Display error messages """
    logger.warning('Update "%s" caused error "%s"', update, error)


#### LINE COMMANDS ####


def help(bot, update):
    """ Bot LineCommand: /start or /help """

    startText = 'Hi! I am L.U.C.A. bot\n' \
                'Commands:\n' \
                '/getRoom <room> to see who is in that room.\n' \
                '/getUser <user> to see in which room is the user.\n' \
                '/help to display this message again.\n'

    update.message.reply_text(startText)


# TODO
def getUser(bot, update, args, chat_data):
    """
        Get the user's location
    """

    try:
#        user = args[0]
        r = requests.get('http://192.168.1.78:8080/people')

        update.message.reply_text(r.text)

    except (IndexError, ValueError):
        update.message.reply_text('Use /getUser <user>')


# TODO
def getRoom(bot, update, args, chat_data):
    """
        Get the users in a room
    """

    try:
        room = args[0]
        print(room)
        r = requests.get('http://192.168.1.78:8080/rooms/'+room)

        update.message.reply_text(r.text)

    except (IndexError, ValueError):
        update.message.reply_text('Use /getUser <user>')



#### MAIN ####


def main():

    if len(sys.argv) != 2 :
        sys.exit("Wrong number of arguments!\n\tExiting")

    jsonData = json.load(open(sys.argv[1]))

    helpbot=jsonData["token"]
    updater = Updater(helpbot)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("getUser", getUser, pass_args=True, pass_chat_data=True))
    dispatcher.add_handler(CommandHandler("getRoom", getRoom, pass_args=True, pass_chat_data=True))

    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()