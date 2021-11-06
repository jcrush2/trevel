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


TELEGRAM_KEY = os.environ["telegram_token"]
bot = telebot.TeleBot(TELEGRAM_KEY)


@bot.message_handler(commands=["бан2"], func=reply_exist)
def zaBan(msg):
	if msg.chat.type == "private":
		return
		'''
	user = bot.get_chat_member(msg.chat.id, msg.reply_to_message.from_user.id)
	if user.status == 'administrator' or user.status == 'creator':
		return
	bot.send_message(msg.chat.id, f"<a href='tg://user?id=55910350'>🔫</a> <b>{msg.from_user.first_name}</b> предлагает выгнать <b>{msg.reply_to_message.from_user.first_name}</b> из Хабчата!", parse_mode="HTML")
	bot.send_poll(msg.chat.id, f'Согласны выгнать {msg.reply_to_message.from_user.first_name} из Чата?', ['Выгнать', 'Заткнуть', 'Простить'],is_anonymous=False)
	'''
	user = bot.get_chat_member(msg.chat.id, msg.reply_to_message.from_user.id)
	if user.status == 'administrator' or user.status == 'creator':
		return
	mutePoll=bot.send_poll(msg.chat.id, f'{msg.from_user.first_name} предлагает заткнуть {msg.reply_to_message.from_user.first_name}🔫 в Хабчате, Согласны?', ['Заткнуть', 'Простить'], False, close_date=int(round(time.time() + 500)))
	
	print(mutePoll.id)
	pollAnswers = [[],[]]
	pollVoteCount = 0
	@bot.poll_handler(func=lambda m: True)
	def voteCounter(votes):
		global pollVoteCount
		pollVoteCount = votes.total_voter_count
	@bot.poll_answer_handler(func=lambda m: True)
	def polls(count):
		global pollVoteCount
		if (len(count.option_ids) > 0):
			if (count.user.id not in pollAnswers[0]) and (count.user.id not in pollAnswers[1]):
				if (count.option_ids[0] == 0):
					pollAnswers[0].append(count.user.id)
				elif (count.option_ids[0] == 1):
					pollAnswers[1].append(count.user.id)
		else:
			if (count.user.id in pollAnswers[0]):
				pollAnswers[0].remove(count.user.id)
			elif (count.user.id in pollAnswers[1]):
				pollAnswers[1].remove(count.user.id)
		if (len(pollAnswers[0]) >= 1):
			prosent = pollVoteCount / len(pollAnswers[0])
			if (prosent >= 0.7):
				bot.restrict_chat_member(msg.chat.id, msg.reply_to_message.from_user.id, time.time() + 3600, False)
				bot.reply_to(msg, "Участник заткнут на 1 час!")
				print(1, mutePoll.id)
				bot.stop_poll(msg.chat.id, mutePoll.id)


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
