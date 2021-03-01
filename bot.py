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

questions_enlish = ['name','surname','age']
questions_russian = ['имя','фамилия','возраст']

users = {}

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def start(message):   
    global users
    users = {**users, message.from_user.id:{}}
    r = types.InlineQueryResultArticle('1', 'Result1', types.InputTextMessageContent('hi'))
    markup = types.InlineKeyboardMarkup(row_width=2)
    button1 = types.InlineKeyboardButton('Russian',callback_data='russian')
    button2 = types.InlineKeyboardButton('English',callback_data='english')
    markup.add(button1,button2)
    bot.send_message(message.chat.id,'Hello {} \nplease enter your name, username, passport_number, date_of_gettting \nin this format \nname - exampleName \nplease click /questions'.format(message.from_user.first_name),reply_markup=markup)


@bot.message_handler(commands=['questions'])
def questions(message):
    bot.send_message(message.chat.id,"Пожалуйста, введите Ваше имя")
    users[message.from_user.id]['questions'] = ['name']


@bot.callback_query_handler(func=lambda call:True)
def callback_line(call):
    if call.message:
        if call.data == 'english':
            bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)
            bot.send_message(call.message.chat.id,'you choose English')
            # bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,reply_markup=None,text='please enter your name, surname, passport')
        elif call.data == 'russian':
            bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)
            bot.send_message(call.message.chat.id,'you choose Russian')
            # bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,reply_markup=None,text='please enter your name, surname, passport')



@bot.message_handler(content_types=['text'])
def send_message(message):
    if 'questions' in users[message.from_user.id]:
        user = users[message.from_user.id]
        user[user['questions'][len(user['questions']) - 1]] = message.text
        print(user['questions'])
        if len(user['questions']) == len(questions_enlish):
            del user['questions'] 
            encoded_jwt = jwt.encode(user,'secretkey',algorithm='HS256')
            qr = qrcode.QRCode(version=1,box_size=10,border=5)
            qr.add_data(link+encoded_jwt)
            qr.make(fit=True)
            img = qr.make_image(fill='black',back_color='white')
            random_name = 'img'+str(random())+'.png'
            img.save('images/'+random_name)
            img = open('./images/'+random_name,'rb')
            bot.send_photo(message.chat.id,img,reply_markup=None)
            bot.send_message(message.chat.id,link+encoded_jwt)
            return
        bot.send_message(message.chat.id,'please enter your '+ questions_enlish[len(user['questions'])])
        user['questions'] = [*user['questions'], questions_enlish[len(user['questions'])]]
    print(users)


        # print(questions_enlish[len(user['questions'])])
        # user['questions'] = [*user['questions'], questions_enlish[len(user['questions']-1)]]
        # bot.send_message(message.chat.id,'please enter your'+questions_enlish[len(user['questions'])])
    # if len(users[message.from_user.id].questions) != 0:
    #     print('this is answer question')
    # data = message.text.split('-')
    # res = requests.post('http://192.168.1.22:8888/gettoken',data={'name':data[0],'surname':data[1],'passport_number':data[2]})
    # if data[0].strip() == 'username':
    # if data[0].strip() == 'name':
    # bot.send_message(message.chat.id,'wait please')
    # encoded_jwt = jwt.encode({'name':data[0],'surname':data[1],'passport_number':data[2]},'secretkey',algorithm='HS256')
    # qr = qrcode.QRCode(version=1,box_size=10,border=5)
    # qr.add_data(link+encoded_jwt)
    # qr.make(fit=True)
    # img = qr.make_image(fill='black',back_color='white')
    # random_name = 'img'+str(random())+'.png'
    # img.save('images/'+random_name)
    # img = open('./images/'+random_name,'rb')
    # bot.send_photo(message.chat.id,img,reply_markup=None)
    # bot.send_message(message.chat.id,link+encoded_jwt)



bot.polling(none_stop=True)

