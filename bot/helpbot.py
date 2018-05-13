"""
    Timer Bot to send timed Telegram messages

    Classes
        Bot: Bot handler
        JobQueue: Send timed messages

    Press CTRL-C to stop the bot
"""

from telegram.ext import Updater, CommandHandler
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import InlineQueryHandler

import logging, sys, json

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

#### HELPER FUNCTIONS ####


def parse_time(time):
    """ Helper function: Parse time
        Possible formats: ss ; mm:ss ; hh:mm:ss
    """

    if len(time) == 1:
        """ Read seconds """
        return abs(int(time[0]))

    elif len(time) == 2:
        """ Read minutes + seconds """
        return abs(int(time[0])*60) + abs(int(time[1]))

    elif len(time) == 3:
        """ Read hours + minutes + seconds """
        return abs(int(time[0])*60*60) + abs(int(time[1])*60) + abs(int(time[2]))

    else:
        """ Error """
        return -1


def alarm(bot, job):
    """ Helper function: Set the alarm
        job.context[0] = chat_id
        job.context[1] = text to show
    """
    if not job.context[1]:
        bot.send_message(job.context[0], text="Beep!")
    else:
        bot.send_message(job.context[0], text=job.context[1])


def error(bot, update, error):
    """ Helper function: Display error messages """
    logger.warning('Update "%s" caused error "%s"', update, error)


#### LINE COMMANDS ####


def start(bot, update):
    """ Bot LineCommand: /start or /help"""

    startText = 'Hi! I am a simple reminder bot\n' \
                'Use /set <time> <msg> to set a timer and display <msg>\n' \
                '<time> can have formats <ss>, <mm:ss> or <hh:mm:ss>\n' \
                'Uset /help or /start to display this message again'

    update.message.reply_text(startText)


def set_timer(bot, update, args, job_queue, chat_data):
    """ Bot LineCommand: /set
        Set a timer
        Create a job and put into the job_queue
    """

    chat_id = update.message.chat_id
    try:
        time = parse_time(args[0].split(':'))

        if time < 0:
            update.message.reply_text('Use /set <hh:mm:ss> <msg>')
            return

        """ Create text to show """
        text = args
        del text[0]
        text = ' '.join(text)

        """ Data bundle for the callback alarm """
        bundle = list()
        bundle.append(chat_id)
        bundle.append(text)

        job = job_queue.run_once(alarm, time, context=bundle)
        chat_data['job'] = job

        update.message.reply_text('Timer successfully set')

    except (IndexError, ValueError):
        update.message.reply_text('Use /set <hh:mm:ss> <msg>')


def unset(bot, update, chat_data):
    """ Bot LineCommand: /unset
        Unset LAST timer
        TODO: ..update!?
    """
    if 'job' not in chat_data:
        update.message.reply_text('No active timer set')
        return

    job = chat_data['job']
    job.schedule_removal()
    del chat_data['job']

    update.message.reply_text('Timer unset')


#### MAIN ####


def main():

    if len(sys.argv) != 2 :
        sys.exit("Wrong number of arguments!\n\tExiting")

    jsonData = json.load(open(sys.argv[1]))

    helpbot=jsonData["token"]
    updater = Updater(helpbot)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", start))
    dispatcher.add_handler(CommandHandler("set", set_timer,
                                          pass_args=True,
                                          pass_job_queue=True,
                                          pass_chat_data=True))
    dispatcher.add_handler(CommandHandler("unset", unset, pass_chat_data=True))

    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()