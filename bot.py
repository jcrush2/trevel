#!usr/bin/python3
import datetime
import hashlib
import string
import os
import random
import requests
import json
import re
from flask import Flask, request
import telebot
from telebot import types
import config

TELEGRAM_API = os.environ["telegram_token"]
bot = telebot.TeleBot(TELEGRAM_API)
	

@bot.message_handler(commands=["start"])
def start(msg):
	"""
	Функция для ответа на сообщение-команду для приветствия пользователя.
	:param msg: Объект сообщения-команды
	"""
	reply_text = (
			"Здравствуйте, я бот, который отвечает за " +
			" подсчет кармы в чате @khvchat.")
	bot.send_message(msg.chat.id, reply_text)

def weather_key(text):
    weather = types.InlineKeyboardMarkup()
    weather.add(
        types.InlineKeyboardButton(text=text, callback_data='weather_now'))
    return weather
    
@bot.message_handler(commands=['123'])
def handle_docs_photo(message):
    bot.send_message(message.chat.id, 'текст над кнопкой', reply_markup=weather_func('lalala'))

@bot.callback_query_handler(func=lambda call: True)
def handler_call(call):
    if call.data == 'weather_now':
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=get_weather_now(),
            reply_markup=weather_func('blala'),
            parse_mode='Markdown')

'''
@bot.message_handler(commands=["bo"])
def keyboard(msg):
	if len(msg.text.split()) == 1:
		n=10
	else:
		n = int(msg.text.split()[1])
		
	nums=list(range(1, n))
	random.shuffle(nums)
	keyboard = telebot.types.InlineKeyboardMarkup()
	button_list = [telebot.types.InlineKeyboardButton(text='•', callback_data=x) for x in nums]
	keyboard.add(*button_list)
	bot.send_message(chat_id=msg.chat.id, text='Разминируйте минное поле',reply_markup=keyboard)
		
@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
	if call.message:
		if  call.data == "1":
			keyboard=[[InlineKeyboardButton('Happy 1',callback_data='1')],[InlineKeyboardButton('Happy 2',callback_data='2')],[InlineKeyboardButton('Happy 3',callback_data='3')]]
			
			reply_markup=InlineKeyboardMarkup(keyboard)
			bot.editMessageText(chat_id=call.message.chat_id,message_id=call.message.message_id,reply_markup=reply_markup)
          
			

			bot.send_message(call.message.chat.id, f"🎉 1 {call.from_user.first_name} обезвредил бомбу +5, перезапустить /bomb", parse_mode="HTML")
			bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Пыщь1", reply_markup=keyboard)
			

			return
		if  call.data == "2":
			bot.send_message(call.message.chat.id, f"🎉 2 {call.from_user.first_name} обезвредил бомбу +5, перезапустить /bomb", parse_mode="HTML")
			bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Пыщь2", reply_markup=keyboard)
			return
		else:
			bot.send_message(call.message.chat.id, f"🎉 3 {call.from_user.first_name} обезвредил бомбу +5, перезапустить /bomb", parse_mode="HTML")
			bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Пыщь3", reply_markup=keyboard)
			return
'''
# Дальнейший код используется для установки и удаления вебхуков
server = Flask(__name__)


@server.route("/bot", methods=['POST'])
def get_message():
	""" TODO """
	decode_json = request.stream.read().decode("utf-8")
	bot.process_new_updates([telebot.types.Update.de_json(decode_json)])
	return "!", 200


@server.route("/")
def webhook_add():
	""" TODO """
	bot.remove_webhook()
	bot.set_webhook(url=config.url)
	return "!", 200

@server.route("/<password>")
def webhook_rem(password):
	""" TODO """
	password_hash = hashlib.md5(bytes(password, encoding="utf-8")).hexdigest()
	if password_hash == "5b4ae01462b2930e129e31636e2fdb68":
		bot.remove_webhook()
		return "Webhook removed", 200
	else:
		return "Invalid password", 200


server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
