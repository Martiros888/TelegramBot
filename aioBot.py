from aiogram import Bot, Dispatcher, executor
from config import TOKEN
import asyncio

loop = asyncio.get_event_loop()
bot = Bot(TOKEN,parse_mode='HTML')
dp = Dispatcher(bot,loop=loop)

@dp.message_handler()
def lalal(message):
    bot.send_message(message.chat.id,text='hello')
    

if __name__ == '__name__':
    executor.start_polling()