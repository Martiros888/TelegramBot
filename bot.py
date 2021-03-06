import telebot
import config
import telebot.types as types
import qrcode
import json
import jwt
import os
import requests
import asyncio
import numpy as np
from PIL import Image
from random import random
from pythonPDF import RussianVersion
link = "http://192.168.1.2:3000/tokens/"

questions_english = ["name","surname","gender","patronymic","date of birth","date of delivery","address","passport number"]
questions_russian = ["имя","фамилия","пол","отчество","Дата рождения","дата доставки","адрес","номер паспорта"]

users = {}

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=["start"])
def start(message):   
    global users
    users = {**users, message.from_user.id:{}}
    markup = types.InlineKeyboardMarkup(row_width=2)
    button1 = types.InlineKeyboardButton("Russian",callback_data="russian")
    button2 = types.InlineKeyboardButton("English",callback_data="english")
    markup.add(button1,button2)
    bot.send_message(message.chat.id,"Добрый день этот бот поможет вам получить анализ PCR на коронавирус и также сертификаты o вакцинации \n{} прошу вам выбрать язык в котором вам требуется оформление ".format(message.from_user.first_name),reply_markup=markup)



@bot.message_handler(commands=["questions"])
def questions(message):
    if users[message.chat.id]["info"]["language"] == "russian":
        bot.send_message(message.chat.id,"Пожалуйста, введите Ваше имя")
        users[message.from_user.id]["questions"] = ["имя"]
        return 
    bot.send_message(message.chat.id,"please enter name")
    users[message.from_user.id]["questions"] = ["name"]


@bot.callback_query_handler(func=lambda call:True)
def callback_line(call):
    if call.message:
        if call.data == "english":
            markup = types.InlineKeyboardMarkup(row_width=2)
            button1 = types.InlineKeyboardButton("Saint Petersburg",callback_data="petersburg_english")
            button2 = types.InlineKeyboardButton("Moscow",callback_data="moscow_english")
            markup.add(button1,button2)
            bot.delete_message(call.message.chat.id,call.message.message_id)
            bot.send_message(call.message.chat.id,"you choose English",reply_markup=markup)
            return 
        elif call.data == "russian":
            markup = types.InlineKeyboardMarkup(row_width=2)
            button1 = types.InlineKeyboardButton("Санкт-Петербург",callback_data="petersburg_russian")
            button2 = types.InlineKeyboardButton("Москва",callback_data="moscow_russian")
            markup.add(button1,button2)
            bot.delete_message(call.message.chat.id,call.message.message_id)
            bot.send_message(call.message.chat.id,"Вы выбрали русский язык",reply_markup=markup)
            return 
        data = call.data.split("_")
        users[call.message.chat.id]["info"] = {
            "language":data[1],
            "city":data[0],
        }
        if data[1] == "russian":
            bot.delete_message(call.message.chat.id,call.message.message_id)
            bot.send_message(call.message.chat.id,"пожалуйста, нажмите на /questions, чтобы ответить на вопросы")
            return 
        bot.delete_message(call.message.chat.id,call.message.message_id)
        bot.send_message(call.message.chat.id,"please click on /questions for asking questions")
                   
    


@bot.message_handler(content_types=["text"])
def send_message(message):
    if message.chat.id not in users:
        bot.send_message(message.chat.id,"/start for restart")
        return 
    if "info" not in users[message.chat.id]:
        bot.send_message(message.chat.id,"/start for restart you do something error")
        return
    if users[message.chat.id]["info"]["language"] == "english":    
        if "questions" in users[message.from_user.id]:
            user = users[message.from_user.id]
            user[user["questions"][len(user["questions"]) - 1]] = message.text
            if len(user["questions"]) == len(questions_english):
                data = users[message.chat.id]
                arr = np.array([])
                for i in data:
                    arr = [*arr,data[i]]
                dictionary = {
                    "chat_id":message.chat.id,
                    "name":arr[2],
                    "surname":arr[3],
                    "gender":arr[4],
                    "patronymic":arr[5],
                    "date_of_birth":arr[6],
                    "date_of_delivery":arr[7],
                    "address":arr[8],
                    "passport_number":arr[9],
                }
                res = requests.post("http://192.168.1.2:8888/adduser",{"user":json.dumps(dictionary)})
                del users[message.chat.id] 
                if res.text == "error":
                    bot.send_message(message.chat.id,'you wrote something')
                    return 
                encoded_jwt = jwt.encode({"chat_id":message.chat.id},"secretkey",algorithm="HS256")
                qr = qrcode.QRCode(version=1,box_size=10,border=5)
                qr.add_data(link + encoded_jwt)
                qr.make(fit=True)
                img = qr.make_image(fill="black",back_color="white")
                # random_name = "img"+str(random())+".png"
                img.save("images/"+ "qrcode.png")
                img = open("./images/" + "qrcode.png","rb")
                bot.send_photo(message.chat.id,img,reply_markup=None)
                bot.send_message(message.chat.id,link + encoded_jwt)
                return
            bot.send_message(message.chat.id,"please enter " + questions_english[len(user["questions"])])
            user["questions"] = [*user["questions"], questions_english[len(user["questions"])]]
            return 
        return 
    if users[message.chat.id]["info"]["language"] == "russian":
        if "questions" in users[message.from_user.id]:
            user = users[message.from_user.id]
            user[user["questions"][len(user["questions"]) - 1]] = message.text
            if len(user["questions"]) == len(questions_russian):
                data = users[message.chat.id]
                arr = np.array([])
                for i in data:
                    arr = [*arr,data[i]]
                dictionary = {
                    "chat_id":message.chat.id,
                    "name":arr[2],
                    "surname":arr[3],
                    "gender":arr[4],
                    "patronymic":arr[5],
                    "date_of_birth":arr[6],
                    "date_of_delivery":arr[7],
                    "address":arr[8],
                    "passport_number":arr[9],
                }
                res = requests.post("http://192.168.1.2:8888/adduser",{"user":json.dumps(dictionary)})
                del users[message.chat.id] 
                if res.text == "error":
                    bot.send_message(message.chat.id,'you wrote something')
                    return 
                encoded_jwt = jwt.encode({"chat_id":message.chat.id},"secretkey",algorithm="HS256")
                qr = qrcode.QRCode(version=1,box_size=10,border=5)
                qr.add_data(link + encoded_jwt)
                qr.make(fit=True)
                img = qr.make_image(fill="black",back_color="white")
                # random_name = "img"+str(random())+".png"
                img.save("images/"+ "qrcode.png")
                img = open("./images/" + "qrcode.png","rb")
                bot.send_photo(message.chat.id,img,reply_markup=None)
                bot.send_message(message.chat.id,link + encoded_jwt)
                return
            bot.send_message(message.chat.id,"Пожалуйста, введите " + questions_russian[len(user["questions"])])
            user["questions"] = [*user["questions"], questions_russian[len(user["questions"])]]
            return 
    bot.send_message(message.chat.id,"/start for restarting")




bot.polling(none_stop=True)



