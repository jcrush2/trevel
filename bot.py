#!usr/bin/python3
import datetime
import hashlib
import string
import os 
import random
import requests
import json
import re

import md5
from xml.etree import ElementTree

from flask import Flask, request
import telebot
from telebot import types
import config

YANDEX_KEY = 'ce2ee061-4d3f-40aa-adfe-6af946fd65a4'
VOICE_LANGUAGE = 'ru-RU'
MAX_MESSAGE_SIZE = 1000 * 50  # in bytes
MAX_MESSAGE_DURATION = 15  # in seconds
language='ru_RU'

TELEGRAM_KEY = os.environ["telegram_token"]
bot = telebot.TeleBot(TELEGRAM_KEY)

@bot.message_handler(commands=['start'])
def start_prompt(message):
    """Print prompt to input voice message.
    """
  
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
