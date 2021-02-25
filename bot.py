import telebot
import config
import telebot.types as types
import qrcode
from PIL import Image
from random import random
import asyncio
import os
import jwt
import requests
link = 'http://192.168.1.22:3000/tokens/'



bot = telebot.TeleBot(config.TOKEN)

def deleteImage(url):
    asyncio.sleep(10)
    os.remove('./images/'+url)

@bot.message_handler(commands=['start'])
def start(message):    
    markup = types.InlineKeyboardMarkup(row_width=2)
    button1 = types.InlineKeyboardButton('Analiz',callback_data='analiz')
    button2 = types.InlineKeyboardButton('Test',callback_data='test')
    markup.add(button1,button2)
    bot.send_message(message.chat.id,'Hello {}'.format(message.from_user.first_name),reply_markup=markup)


@bot.callback_query_handler(func=lambda call:True)
def callback_line(call):
    if call.message:
        if call.data == 'analiz':
            bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,reply_markup=None,text='please enter your name, surname, passport')
        elif call.data == 'test':
            bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,reply_markup=None,text='please enter your name, surname, passport')


@bot.message_handler(content_types=['text'])
def lalala(message):
    data = message.text.split(',')
    # res = requests.post('http://192.168.1.22:8888/gettoken',data={'name':data[0],'surname':data[1],'passport_number':data[2]})
    encoded_jwt = jwt.encode({'name':data[0],'surname':data[1],'passport_number':data[2]},'secretkey',algorithm='HS256')
    qr = qrcode.QRCode(version=1,box_size=10,border=5)
    qr.add_data(link+encoded_jwt)
    qr.make(fit=True)
    img = qr.make_image(fill='black',back_color='white')
    random_name = 'img'+str(random())+'.png'
    img.save('images/'+random_name)
    img = open('./images/'+random_name,'rb')
    bot.send_photo(message.chat.id,img,reply_markup=None)
    bot.send_message(message.chat.id,link+encoded_jwt)


bot.polling(none_stop=True)

