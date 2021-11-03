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
	


keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard1.row('Информация')
keyboard2 = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard2.row('1', '2', '3')

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет', reply_markup=keyboard1)
@bot.message_handler(content_types=['text'])
def send_text(message):
	if message.text.lower() == 'привет':
		bot.send_message(message.chat.id, 'ну Привет', reply_markup=keyboard2)


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
