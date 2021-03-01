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

questions_english = ['name','surname','age']
questions_russian = ['имя','фамилия','возраст']

users = {}

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def start(message):   
    global users
    users = {**users, message.from_user.id:{}}
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
        print(call.data)
        if call.data == 'english':
            markup = types.InlineKeyboardMarkup(row_width=2)
            button1 = types.InlineKeyboardButton('Saint Petersburg',callback_data='petersburg_english')
            button2 = types.InlineKeyboardButton('Moscow',callback_data='moscow_english')
            markup.add(button1,button2)
            bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)
            bot.send_message(call.message.chat.id,'you choose English',reply_markup=markup)
            return 
        elif call.data == 'russian':
            markup = types.InlineKeyboardMarkup(row_width=2)
            button1 = types.InlineKeyboardButton('Санкт-Петербург',callback_data='petersburg_russian')
            button2 = types.InlineKeyboardButton('Москва',callback_data='moscow_russian')
            markup.add(button1,button2)
            bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)
            bot.send_message(call.message.chat.id,'вы выбрали русский язык',reply_markup=markup)
            return 
        data = call.data.split('_')
        users[call.message.chat.id]['info'] = {
            'language':data[1],
            'city':data[0],
        }
        if data[1] == 'russian':
            bot.send_message(call.message.chat.id,'пожалуйста, нажмите на /questions, чтобы ответить на вопросы')
            return 
        bot.send_message(call.message.chat.id,'please click on /questions for asking questions')
                   
    


@bot.message_handler(content_types=['text'])
def send_message(message):
    print(users)
    if users[message.chat.id]['info']['language'] == 'english':    
        if 'questions' in users[message.from_user.id]:
            user = users[message.from_user.id]
            user[user['questions'][len(user['questions']) - 1]] = message.text
            if len(user['questions']) == len(questions_english):
                del user['questions'] 
                encoded_jwt = jwt.encode(user,'secretkey',algorithm='HS256')
                qr = qrcode.QRCode(version=1,box_size=10,border=5)
                qr.add_data(link + encoded_jwt)
                qr.make(fit=True)
                img = qr.make_image(fill='black',back_color='white')
                random_name = 'img'+str(random())+'.png'
                img.save('images/'+random_name)
                img = open('./images/'+random_name,'rb')
                bot.send_photo(message.chat.id,img,reply_markup=None)
                bot.send_message(message.chat.id,link + encoded_jwt)
                return
            bot.send_message(message.chat.id,'please enter your '+ questions_english[len(user['questions'])])
            user['questions'] = [*user['questions'], questions_english[len(user['questions'])]]
        return 
    if users[message.chat.id]['info']['language'] == 'russian':
        if 'questions' in users[message.from_user.id]:
            user = users[message.from_user.id]
            user[user['questions'][len(user['questions']) - 1]] = message.text
            if len(user['questions']) == len(questions_russian):
                del user['questions'] 
                encoded_jwt = jwt.encode(user,'secretkey',algorithm='HS256')
                qr = qrcode.QRCode(version=1,box_size=10,border=5)
                qr.add_data(link + encoded_jwt)
                qr.make(fit=True)
                img = qr.make_image(fill='black',back_color='white')
                random_name = 'img'+str(random())+'.png'
                img.save('images/'+random_name)
                img = open('./images/'+random_name,'rb')
                bot.send_photo(message.chat.id,img,reply_markup=None)
                bot.send_message(message.chat.id,link + encoded_jwt)
                return
            bot.send_message(message.chat.id,'Пожалуйста, введите Ваше '+ questions_russian[len(user['questions'])])
            user['questions'] = [*user['questions'], questions_russian[len(user['questions'])]]
            return 
    bot.send_message(message.chat.id,'/questions')        




bot.polling(none_stop=True)



