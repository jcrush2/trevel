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

# https://tech.yandex.ru/speechkit/cloud/doc/dg/concepts/speechkit-dg-overview-technology-recogn-docpage/
# Language code for speech recognition. You can use: ru-RU, en-US, uk-UK, tr-TR
VOICE_LANGUAGE = 'ru-RU'

MAX_MESSAGE_SIZE = 1000 * 50  # in bytes
MAX_MESSAGE_DURATION = 15  # in seconds

language='ru_RU'
TELEGRAM_API = os.environ["telegram_token"]
bot = telebot.TeleBot(TELEGRAM_API)

@bot.message_handler(commands=['start'])
def start_prompt(message):
    """Print prompt to input voice message.
    """
    reply = ' '.join((
      "Press and hold screen button with microphone picture.",
      "Say your phrase and release the button.",
    ))
    return bot.reply_to(message, reply)


@bot.message_handler(content_types=['voice'])
def echo_voice(message):
    """Voice message handler.
    """
    data = message.voice
    if (data.file_size > MAX_MESSAGE_SIZE) or (data.duration > MAX_MESSAGE_DURATION):
        reply = ' '.join((
          "The voice message is too big.",
          "Maximum duration: {} sec.".format(MAX_MESSAGE_DURATION),
          "Try to speak in short.",
        ))
        return bot.reply_to(message, reply)

    file_url = "https://api.telegram.org/file/bot{}/{}".format(
      bot.token,
      bot.get_file(data.file_id).file_path
    )

    xml_data = requests.post(
      "https://asr.yandex.net/asr_xml?uuid={}&key={}&topic={}&lang={}".format(
        md5.new(str(message.from_user.id)).hexdigest(),
        YANDEX_KEY,
        'queries',
        VOICE_LANGUAGE
      ),
      data=requests.get(file_url).content,
      headers={"Content-type": 'audio/ogg;codecs=opus'}
    ).content

    e_tree = ElementTree.fromstring(xml_data)
    if not int(e_tree.attrib.get('success', '0')):
        return bot.reply_to(message, "ERROR: {}".format(xml_data))

    text = e_tree[0].text

    if ('<censored>' in text) or (not text):
        return bot.reply_to(message, "Don't understand you, please repeat.")

    return bot.reply_to(message, text)
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
