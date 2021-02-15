#!usr/bin/python3
import hashlib
import string
import os
import re
from flask import Flask, request
import telebot
from telebot import types
import config

TELEGRAM_API = os.environ["telegram_token"]
bot = telebot.TeleBot(TELEGRAM_API)
	
def otzyv(msg):        
	keyboard = types.InlineKeyboardMarkup()
	url_button = types.InlineKeyboardButton(text=f"Отзывы - {msg.from_user.first_name} 💬", url=f"https://khabara.ru/tg/{msg.from_user.id}-id.html")
	keyboard.add(url_button)
	bot.reply_to(msg, f'ℹ️ Объявление от <a href="tg://user?id={msg.from_user.id}">{msg.from_user.first_name}</a>\n<i>Оставить отзыв ⬇️️️</i>', parse_mode="HTML", reply_markup=keyboard)
			
		
def antispam(msg):
				
	if msg.caption !=None:
		textspam=msg.caption.lower()
	else:
		textspam=msg.text.lower()
	if msg.chat.id==-1001422750282:
		keywords_work = ("рабо", "вакан","требу", "ищу", "график","свобод", "зар", "плат", "услов", "опыт", "обязанн", "резюме", "нуж", "зп")
		if any(word in textspam for word in keywords_work):
			bot.send_chat_action(msg.chat.id, "typing")
		else:
			bot.delete_message(msg.chat.id, msg.message_id)

	keywords = ("zwzff", "wa.me", "www", "http", "t.me", "www")
	if textspam is None or len(textspam) < 4 or re.search('\d', textspam) == None or any(word in textspam for word in keywords):
		bot.delete_message(msg.chat.id, msg.message_id)
	else:
		otzyv(msg)
		
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
