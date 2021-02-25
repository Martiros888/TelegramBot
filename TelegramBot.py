import config
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

logger = logging.getLogger(__name__)



def start(update, context):
    print(update)
    keyboard = [
        [InlineKeyboardButton("English", callback_data='callback_1')],
        [InlineKeyboardButton("Russian", callback_data='callback_2')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message_reply_text = 'Click one of these buttons'
    update.message.reply_text(message_reply_text, reply_markup=reply_markup)

def helpCommand(update, context):
    print(update)
    update.message.reply_text('Help')

def echo(update, context):
    print(update)
    update.message.reply_text(update.message.text)

def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    updater = Updater(config.TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()