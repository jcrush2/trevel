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
	

		
def antispam(msg):
				
	if msg.text.lower() in ['билет']:
		bot.send_chat_action(msg.chat.id, "typing")
		send_bilet=f"✈️ билеты\n\n"
		
		url = "https://api.travelpayouts.com/v1/prices/cheap"
		a = datetime.datetime.now().strftime("%Y-%m")
		querystring = {"origin":"KHV","destination":"-","depart_date":f"{a}"}
		headers = {'x-access-token': '83a5fe66f97a36e6f0be4b2be21a5552'}
		response = requests.request("GET", url, headers=headers, params=querystring)
		data = response.json()
		try:
			BKK = data['data']['BKK']['1']['price']
			BKK2 = data['data']['BKK']['1']['departure_at']
			send_bilet+=f"✈️ Бангкок (Таиланд), цена: {BKK}, вылет: {BKK2}\n\n"
		except Exception:
			 print("Some other error")
		try:
			HKG = data['data']['HKG']['1']['price']
			HKG2 = data['data']['HKG']['1']['departure_at']
			send_bilet+=f"✈️ Гонконг (Китай), цена: {HKG}, вылет: {HKG2}\n\n"
		except Exception:
			 print("Some other error")
		try:
			NHA = data['data']['NHA']['1']['price']
			NHA2 = data['data']['NHA']['1']['departure_at']
			send_bilet+=f"✈️ Нячанг (Вьетнам), цена: {NHA}, вылет: {NHA2}\n\n"
		except Exception:
			 print("Some other error")
		try:
			AYT = data['data']['AYT']['1']['price']
			AYT2 = data['data']['AYT']['1']['departure_at']
			send_bilet+=f"✈️ Анталья (Турция), цена: {AYT}, вылет: {AYT2}\n\n"
		except Exception:
			 print("Some other error")
		try:
			BJS = data['data']['BJS']['1']['price']
			BJS2 = data['data']['BJS']['1']['departure_at']
			send_bilet+=f"✈️ Пекин (Китай), цена: {BJS}, вылет: {BJS2}\n\n"
		except Exception:
			 print("Some other error")
		try:
			CAN = data['data']['CAN']['1']['price']
			CAN2 = data['data']['CAN']['1']['departure_at']
			send_bilet+=f"✈️ Гуанчжоу (Китай), цена: {CAN}, вылет: {CAN2}\n\n"
		except Exception:
			 print("Some other error")
		try:
			CEB = data['data']['CEB']['1']['price']
			CEB2 = data['data']['CEB']['1']['departure_at']
			send_bilet+=f"✈️ Кебу (Филиппины), цена: {CEB}, вылет: {CEB2}\n\n"
		except Exception:
			 print("Some other error")

		bot.send_message(msg.chat.id, send_bilet, parse_mode="HTML")

		keyboard = types.InlineKeyboardMarkup()
		url_button = types.InlineKeyboardButton(text="Посмотреть", url="https://tp.media/r?marker=13972&trs=10984&p=4114&u=https%3A%2F%2Fwww.aviasales.ru%2Fsearch%2FKHV")
		keyboard.add(url_button)
		bot.send_message(msg.chat.id, "Вы можете купить билет, оплатив по кнопке ниже.", reply_markup=keyboard)
		
def antispam_media(msg):
	if msg.forward_from_chat != None:
		bot.delete_message(msg.chat.id, msg.message_id)
	else:
		if msg.caption !=None:
			antispam(msg)
		else:
			bot.delete_message(msg.chat.id, msg.message_id)

def reply_exist(msg):
	return msg.reply_to_message

@bot.message_handler(content_types=["text", "photo","video"], func=reply_exist)
def reply_text(msg):
	bot.delete_message(msg.chat.id, msg.message_id)

@bot.message_handler(content_types=['text'])	
def antispam_text(msg):
	if msg.forward_from_chat != None:
		bot.delete_message(msg.chat.id, msg.message_id)
	else:
		antispam(msg)
	
@bot.message_handler(content_types=['photo','video'])	
def antispam_photo(msg):
	antispam_media(msg)
		
		

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
