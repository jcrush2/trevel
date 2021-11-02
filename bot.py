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

@bot.message_handler(commands=["bo"])
def bomb(msg):
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
	

	if  call.data == "1":
		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="💥", reply_markup=keyboard)
		bot.send_message(call.message.chat.id, f"💥 {call.from_user.first_name} подорвался -5, перезапустить /bomb", parse_mode="HTML")
	
	if  call.data == "2":
		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="💣", reply_markup=keyboard)
		bot.send_message(call.message.chat.id, f"🎉 {call.from_user.first_name} обезвредил бомбу +5, перезапустить /bomb", parse_mode="HTML")
	
	else:
		bot.send_message(call.message.chat.id, f"🎉 {call.from_user.first_name} мимо бомбу +5, перезапустить /bomb", parse_mode="HTML")	
		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="0", reply_markup=keyboard)
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
