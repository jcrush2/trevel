#!usr/bin/python3
import datetime
import time
import hashlib
import string
import os
import random
import requests
import re
import bs4


from flask import Flask, request
import peewee as pw
import telebot

from database import KarmaUser, Limitation
from telebot import types
import config


TELEGRAM_API = os.environ["telegram_token"]
bot = telebot.TeleBot(TELEGRAM_API)

saves_database = {}
database="crocodila"
database_vopros="victorina"
database_id=0
message_id_del="111111"
message_id_del2="2"
database_time="3333"
change_croco_2=2
database_id_mute=2
database_id_time=0

def is_my_message(msg):
	"""
	Функция для проверки, какому боту отправлено сообщение.
	Для того, чтобы не реагировать на команды для других ботов.
	:param msg: Объект сообщения, для которого проводится проверка.
	"""
	if msg.chat.type == "private":
		return
	text = msg.text.split()[0].split("@")
	if len(text) > 1:
		if text[1] != config.bot_name:
			return False
	return True
	
def reply_exist(msg):
	return msg.reply_to_message

@bot.message_handler(commands=["start"], func=is_my_message)
def start(msg):
	"""
	Функция для ответа на сообщение-команду для приветствия пользователя.
	:param msg: Объект сообщения-команды
	"""
	reply_text = (
			"Здравствуйте, я бот, который отвечает за " +
			" подсчет кармы в чате @khvchat.")
	bot.send_message(msg.chat.id, reply_text)

@bot.message_handler(commands=["h","help"], func=is_my_message)
def helps(msg):
	help_mess = "<b>ХабЧат</b> - чат города Хабаровска.\
	\n\nℹ️ Выражения похвалы и общение в положительном ключе повышают карму, ругательства понижают.\
	\n\n<b>Команды:</b>\
	\n/h - Справка\
	\n/weather - Погода\
	\n/news - Новости\
	\n/croco - Игра в Крокодил\
	\n/slovo - Игра в Слова\
	\n/stat - Статистика\
	\n/report - Отправить жалобу\
	\n\n/привет /утра /цитата /дата /гороскоп /кот /шутка /? /к /пи /фсб /фото /бан - Ответом на сообщение\
	\n\n<b>Карма:</b>\
	\n/my - Своя карма\
	\n/top - Топ чата\
	\n/gift - Подарить 🎁🌹❤\
	\n/mine - Заработать карму\
	\n/z - Заморозка 🥶\
	\n/f - Разморозка\
	\n/b - Безлимит 😎\
	\n<b>/тиндер</b> - Найти пару\
	\n<b>/лимит</b> - Снять лимит\
	\n🔫🔪🪓⚔️🏹 🧨💣 - Дуэль\
	\n🥊 - Супер удар\
	\n🦾 - Удар Халка\
	\n☠ - Смертельный удар\
	\n🎲🎰🏀🎳⚽️ - Рандом"
	
	bot.send_message(msg.chat.id, help_mess, parse_mode="HTML")


@bot.message_handler(commands=["weather","погода"], func=is_my_message)
def weather(msg):
	a = datetime.datetime.today()
	bot.reply_to(msg, f"<a href='https://khabara.ru/weather.html?{a}'>🌡</a>", parse_mode="HTML")
	Limitation.delete().where(Limitation.chatid == msg.chat.id).execute()

@bot.message_handler(commands=["news"], func=is_my_message)
def news_khv(msg):
	a = datetime.datetime.today()
	bot.reply_to(msg, f"<a href='https://khabara.ru/rss.html?{a}'>📰</a>", parse_mode="HTML")

@bot.message_handler(commands=["tg"], func=is_my_message)
def tg_group(msg):
	bot.forward_message(msg.chat.id, -1001119365436, 6203)

@bot.message_handler(commands=["report"], func=is_my_message)
def report(msg):
	"""
	Функция, для жалоб админам
	"""    
	report_text = f"<a href='tg://user?id=55910350'>⚠</a>️ Жалоба от <b>{msg.from_user.first_name}</b> получена + в карму<a href='tg://user?id=34817120'>.</a><a href='tg://user?id=73762291'>.</a>"
	bot.reply_to(msg, report_text, parse_mode="HTML")
	bot.delete_message(msg.chat.id, msg.message_id)

@bot.message_handler(commands=["no"], func=is_my_message)
def nos(msg):
	"""
	Функция, для маркета
	"""
	nos_text = "ℹ️ Здесь Чат общения, для объявлений воспользуйтесь группами: @market27 или @khvjob"
	user = bot.get_chat_member(msg.chat.id, msg.from_user.id)
	if msg.reply_to_message:
		bot.reply_to(msg.reply_to_message,nos_text)
		if user.status == 'administrator' or user.status == 'creator':
			bot.delete_message(msg.chat.id, msg.reply_to_message.message_id)
	else:
		bot.reply_to(msg,nos_text)
	bot.delete_message(msg.chat.id, msg.message_id)
	
def duel(msg):
	if is_karma_abuse(msg):
		return
	if is_karma_freezed(msg):
		return
	if msg.from_user.id == msg.reply_to_message.from_user.id:
		bot.reply_to(msg, "⚰️ самоликвидировался")
		change_karma(msg.from_user, msg.chat, -15)
		return
	if msg.reply_to_message.from_user.is_bot:
		change_karma(msg.from_user, msg.chat, -15)
		return
	user = select_user(msg.from_user, msg.chat)

	if user.is_freezed!=None:
		zamorozka(msg)
	user2 = select_user(msg.reply_to_message.from_user, msg.chat)
	n=10
	try:
		s=msg.text.count("💣")
		q=msg.text.count("🧨")
		n=10+(s+q)
	except:
		print("error")

	if user.karma > n and user2.karma > n:
		otvet=f"💥 Дуэль!"
	else:
		bot.reply_to(msg, f"⚰ То, что мертво, умереть не может! Мало кармы.", parse_mode="HTML")
		return
	random.seed(msg.message_id)
	if msg.text=='🥊' and user.karma > 100 and user2.karma > 100:
		otvet=f"⚡️ Супер удар!"
		n=random.randint(10, 100)
		
	if msg.text=='🦾' and user.karma > 300 and user2.karma > 300:
		otvet=f"⚡️⚡️⚡️ Удар Халка!"
		n=random.randint(100, 300)
		
	if msg.text=='☠️'and msg.reply_to_message.text =='☠️' and user.karma > 1000 and user2.karma > 1000:
		otvet=f"💀 Смертельный удар!"
		n=random.randint(300, 1000)
		
	x=random.randint(1,3)
	if x==1:
		otvetx=f"<b>{msg.from_user.first_name}</b> (+{n}) убил <b>{msg.reply_to_message.from_user.first_name}</b> (-{n})"
		change_karma(msg.from_user, msg.chat, n)
		change_karma(msg.reply_to_message.from_user, msg.chat, -n)
	if x==2:
		otvetx=f"<b>{msg.reply_to_message.from_user.first_name}</b> (+{n}) убил <b>{msg.from_user.first_name}</b> (-{n})"
		change_karma(msg.reply_to_message.from_user, msg.chat, n) 
		change_karma(msg.from_user, msg.chat, -n)
	if x==3:
		otvetx=f"<b>{msg.from_user.first_name}</b> vs <b>{msg.reply_to_message.from_user.first_name}</b> - промазал!"
		change_karma(msg.from_user, msg.chat, -10)
		
	bot.reply_to(msg, f"{otvet}\n{otvetx}", parse_mode="HTML")
				
def select_user(user, chat):
	"""
	Функция для извлечения данных о пользователе
	:param user: пользователь, данные которого необходимы
	:param chat: чат, в котором находится пользователь

	TODO Хотелось бы избавиться от этой функции
	"""
	selected_user = KarmaUser.select().where(
		(KarmaUser.chatid == chat.id) &
		(KarmaUser.userid == user.id))

	if not selected_user:
		insert_user(user, chat)
		
	selected_user = KarmaUser.select().where(
		(KarmaUser.userid == user.id) &
		(KarmaUser.chatid == chat.id)).get()
	return selected_user


def insert_user(user, chat):
	"""
	Функция для добавления нового пользователя
	:param user: данные добавляемого пользователя
	:param chat: чат, в котором находится пользователь

	TODO Хотелось бы избавиться от этой функции
	"""
	# 'user_name' состоит из имени и фамилии. Но разные пользователь по разному
	# подходят к заполнению этих полей и могут не указать имя или фамилию.
	# А если имя или фамилия отсутствуют, то обращение к ним
	# возвращает 'None', а не пустую строку. С 'user_nick' та же ситуация.
	user_name = (user.first_name or "") + " " + (user.last_name or "")
	user_nick = user.username or ""

	new_user = KarmaUser.create(
				userid=user.id,
				chatid=chat.id,
				karma=0,
				user_count=0,
				user_name=user_name,
				user_nick=user_nick,
				is_freezed=False)
	new_user.save()


def change_karma(user, chat, result):
	"""
	Функция для изменения значения кармы пользователя
	:param user: пользователь, которому нужно изменить карму
	:param chat: чат, в котором находится пользователь
	:param result: на сколько нужно изменить карму
	"""
	selected_user = KarmaUser.select().where(
		(KarmaUser.chatid == chat.id) &
		(KarmaUser.userid == user.id))

	if not selected_user:
		insert_user(user, chat)

	# 'user_name' состоит из имени и фамилии. Но разные пользователь по разному
	# подходят к заполнению этих полей и могут не указать имя или фамилию.
	# А если имя или фамилия отсутствуют, то обращение к ним
	# возвращает 'None', а не пустую строку. С 'user_nick' та же ситуация.
	user_name = (user.first_name or "") + " " + (user.last_name or "")
	user_nick = user.username or ""

	update_user = KarmaUser.update(
							karma=(KarmaUser.karma + result),
							user_count=(KarmaUser.user_count + 1),
							user_name=user_name,
							user_nick=user_nick
						).where(
							(KarmaUser.userid == user.id) &
							(KarmaUser.chatid == chat.id))
	update_user.execute()

def users_karma(userkarma):
	dictionary = {1 : "👤\n      Никто", 2 : "🐛\n      Личинка", 3 : "👾\n      Гость", 4 : "🤫\n      Тихоня", 5 : "🐤\n      Прохожий", 6 : "🎗\n      Новичок", 7 : "🔱\n      Любопытный", 8 : "⚜️\n      Странник", 9 : "✨\n      Бывалый", 10 : "🥉\n      Постоялец", 11 : "🥈\n      Завсегдатай", 12 : "🥇\n      Местный житель", 13 : "🎖\n      Городовой", 14 : "🏅\n      Хабаровчанин", 15 : "⭐️\n      ХабАктивист", 16 : "🌟\n      Дальневосточник", 17 : "🏵\n      Старожил", 18 : "💫\n      Сталкер", 19 : "💥\n      Ветеран", 20 : "🎭\n      Философ", 21 : "🎓\n      Мыслитель", 22 : "🛠\n      Мастер", 23 : "☀️\n      Спец", 24 : "🔮\n      Оракул", 25 : "🗽\n      Легенда", 26 : "🏆\n      Гуру", 27 : "👑\n      Элита", 28 : "🧠\n      Мудрец", 29 : "👁\n      Смотритель", 30 : "🏹\n      Вождь", 31 : "🧘\n      Дзэн", 32 : "✝️\n      Бог", 33 : "⚡️\n      Верховный Бог", 34 : "⚡⚡️️️\n      Пантеон", 35: "🦾\n      Сломал систему"}
	user_rang="🤖\n      Бот"
	level=0
	for level, rang in dictionary.items(): 
		if userkarma >= level**3*10:
			user_rang=rang
			user_level=level
	return user_rang, user_level
	
@bot.message_handler(commands=["my","карма"], func=is_my_message)
def my_karma(msg):
	"""
	Функция, которая выводит значение кармы для пользователя.
	Выводится карма для пользователя, который вызвал функцию
	:param msg: Объект сообщения-команды
	"""

	user = select_user(msg.from_user, msg.chat)
	
	frez=""
	if user.is_freezed:
		frez=" 🥶"
	if user.is_freezed==None:
		frez=" 😎"

	if user.user_name:
		name = user.user_name.strip()
	else:
		name = user.user_nick.strip()
	userkarma=user.karma+user.user_count
	
	
	hours_ago_12 = pw.SQL(f"current_timestamp-interval'{random.randint(10, 120)} minutes'")
	limitation_request = Limitation.select().where(
		(Limitation.timer > hours_ago_12) &
		(Limitation.userid == msg.from_user.id) &
		(Limitation.chatid == msg.chat.id))
	timer = "-"

	if len(limitation_request) > 1:
		timer = limitation_request[0].timer + datetime.timedelta(hours=12)
		timer = timer.strftime("%H:%M")
	x,y = users_karma(userkarma)
	now_karma = f"ℹ️ <b>{name}</b>\nСообщений: {user.user_count}\nКарма: {user.karma}{frez}\nЛимит: {timer}\nРанг: {y} {x}"
	bot.reply_to(msg, now_karma, parse_mode="HTML")
    
@bot.message_handler(commands=["top","топ"], func=is_my_message)
def top_best(msg):
	
	"""
	Функция которая выводит список пользователей с найбольшим значением кармы
	:param msg: Объект сообщения-команды
	"""

	if len(msg.text.split()) == 1:
		result=10
	else:
		result = int(msg.text.split()[1])	
	selected_user = KarmaUser.select()\
		.where(((KarmaUser.user_count+ KarmaUser.karma) > 0) & (KarmaUser.chatid == msg.chat.id))\
		.order_by((KarmaUser.user_count+KarmaUser.karma).desc())\
		.limit(result)
	user_rang = "🤖 Бот"
	top_mess = "📈 Топ ХабЧата\n\n"
	for i, user in enumerate(selected_user):
		if user.user_name:
			name = user.user_name.strip()
		else:
			name = user.user_nick.strip()
		try:

			userstatus = bot.get_chat_member(msg.chat.id,user.userid)
			if userstatus.status == 'creator' or userstatus.status == 'member' or userstatus.status == 'administrator' or userstatus.status != 'left' or userstatus.status != 'kicked' or userstatus.status != 'restricted':
				userkarma=user.karma+user.user_count
				user_rang,y=users_karma(userkarma)
				if userstatus.status == 'left' or userstatus.status == 'kicked':
					user_rang = "💀️️️\n      Выбыл"
					update_user = KarmaUser.update(
							karma=(0),
							user_count=KarmaUser.user_count,
							user_name=user.user_name.strip(),
							user_nick=user.user_nick.strip()
						).where(
							(KarmaUser.userid == user.userid) &
							(KarmaUser.chatid == msg.chat.id))
					update_user.execute()

				frez=""
				if user.is_freezed:
					frez=" 🥶"
				if user.is_freezed==None:
					frez=" 😎"

				top_mess += f"{i+1}. <b>{name}</b>{frez} ({user.user_count}) {user_rang} ({user.karma})\n"
		except Exception:
				top_mess += f"{i+1}. <b>{name}</b> ({user.user_count}) 🗑\n      Удаленный\n"
				update_user = KarmaUser.update(
							karma=(0),
							user_count=KarmaUser.user_count,
							user_name=user.user_name.strip(),
							user_nick=user.user_nick.strip()
						).where(
							(KarmaUser.userid == user.userid) &
							(KarmaUser.chatid == msg.chat.id))
				update_user.execute()

	if not selected_user:
		top_mess = "Никто еще не заслужил быть в этом списке."
	bot.send_message(msg.chat.id, top_mess, parse_mode="HTML")
	
	
@bot.message_handler(commands=["tinder", "тиндер"], func=is_my_message)
def tinder(msg):
	"""
	Функция которая выводит пару дня
	""" 
	if is_game_abuse(msg):
		return
	user = select_user(msg.from_user, msg.chat)

	if user.is_freezed!=None:
		zamorozka(msg)
		
	if user.is_freezed:
		bot.reply_to(msg, f"Разморозьте карму чтобы играть!", parse_mode="HTML")
		return

	else:
		if user.karma > 100:
			random.seed(msg.message_id)
			user = bot.get_chat_member(msg.chat.id, msg.from_user.id)
			if user.status == 'creator':
				change_karma(msg.from_user, msg.chat, +5)
			else:
				change_karma(msg.from_user, msg.chat, -30)

			selected_user = KarmaUser.select()\
				.where((KarmaUser.karma > 100) & (KarmaUser.chatid == msg.chat.id))\
				.order_by(KarmaUser.karma.desc())\
				.limit(200)
			top_mess = f"🤚"
			selected_user = random.choices(selected_user)
			for i, user in enumerate(selected_user):
			
				if user.is_freezed:
					top_mess +=  f"Сегодня ночь самопознания✊"
				else:
					nick = user.user_nick.strip()
					name = user.user_name.strip()
					userid = user.userid
					gender = ''
					if name.endswith('а') or name.endswith('я') or name.endswith('a'):
						
						gender = f'девушкой'
					else:
						gender = f'парнем'
					if msg.from_user.id == userid:
						gender = 'самим собой'
					try:
						userstatus = bot.get_chat_member(msg.chat.id,user.userid)
						if userstatus.status == 'creator' or userstatus.status == 'member' or userstatus.status == 'administrator':
							change_karma(userstatus.user, msg.chat, +2)
							top_mess = f"❤️ Вы образовали пару с {gender}!\n<a href='tg://user?id={msg.from_user.first_name}'>{msg.from_user.id}</a> ➕ <a href='tg://user?id={userid}'>{name}</a>️"

						if userstatus.status == 'left' or userstatus.status == 'kicked':
							top_mess = f"💀️ Вы образовали пару с усопшим <b>{name}</b>"
							update_user = KarmaUser.update(
							karma=(0),
							user_count=KarmaUser.user_count,
							user_name=user.user_name.strip(),
							user_nick=user.user_nick.strip()
							).where(
							(KarmaUser.userid == user.userid) &
							(KarmaUser.chatid == msg.chat.id))
							update_user.execute()
					except Exception:
						top_mess+= f"Сегодня вечер самопознания🤚"
		else:
#			top_mess= f"Нехватает кармы для любви"
			bot.delete_message(msg.chat.id, msg.message_id)

	bot.reply_to(msg, top_mess, parse_mode="HTML")
	
@bot.message_handler(commands=["к"], func=is_my_message)
def krasava(msg):
	"""
	Функция которая выводит пару дня
	""" 
	if is_game_abuse(msg):
		return
	user = select_user(msg.from_user, msg.chat)
	
	if user.is_freezed!=None:
		zamorozka(msg)
		
	if user.is_freezed:
		bot.reply_to(msg, f"Разморозьте карму чтобы играть!", parse_mode="HTML")
		return

	else:
		if user.karma > 100:
			random.seed(msg.message_id)
			user = bot.get_chat_member(msg.chat.id, msg.from_user.id)
			if user.status == 'creator':
				change_karma(msg.from_user, msg.chat, +100)
			else:
				change_karma(msg.from_user, msg.chat, -30)

			selected_user = KarmaUser.select()\
				.where((KarmaUser.karma > 100) & (KarmaUser.chatid == msg.chat.id))\
				.order_by(KarmaUser.karma.desc())\
				.limit(200)
			top_mess = f"🥲"
			selected_user = random.choices(selected_user)
			for i, user in enumerate(selected_user):
			
				if user.is_freezed:
					top_mess +=  f"🥲 Сегодня нет Красав"
				else:
					nick = user.user_nick.strip()
					name = user.user_name.strip()

					try:
						userstatus = bot.get_chat_member(msg.chat.id,user.userid)
						if userstatus.status == 'creator' or userstatus.status == 'member' or userstatus.status == 'administrator':
							change_karma(userstatus.user, msg.chat, +2)
							top_mess = f"🎉🎉🎉 красавчик дня <a href='tg://user?id={user.userid}'>{name}</a>."

						if userstatus.status == 'left' or userstatus.status == 'kicked':
							top_mess = f"🎉️ Кто красавчик? <b>ХабЧат!</b>"
							update_user = KarmaUser.update(
							karma=(0),
							user_count=KarmaUser.user_count,
							user_name=user.user_name.strip(),
							user_nick=user.user_nick.strip()
							).where(
							(KarmaUser.userid == user.userid) &
							(KarmaUser.chatid == msg.chat.id))
							update_user.execute()
					except Exception:
						top_mess+= f"🥲 Сегодня нет Красав"
		else:
			top_mess+= f"Нехватает кармы"
			bot.delete_message(msg.chat.id, msg.message_id)

	bot.send_photo(msg.chat.id, f"https://telegra.ph/file/b2219190b996c55d8ef84.jpg", caption = top_mess, parse_mode="HTML")

	
@bot.message_handler(commands=["dellid"], func=is_my_message)
def dellid(msg):
	bot.delete_message(msg.chat.id, msg.message_id)
	if msg.from_user.id not in config.gods:
		return
	selected_user = KarmaUser.select() \
		.where((KarmaUser.karma <= 3000) & (KarmaUser.chatid == msg.chat.id)) \
		.order_by(KarmaUser.karma.asc()) \
		.limit(5000)
	for i, user in enumerate(selected_user):
		try:
			if i % 20 == 0:
				time.sleep(1)
			userstatus = bot.get_chat_member(msg.chat.id,user.userid)
			if userstatus.status == 'left' or userstatus.status == 'kicked' or userstatus.status != 'member':
				query = KarmaUser.delete().where((KarmaUser.userid == user.userid) & (KarmaUser.chatid == msg.chat.id))
				query.execute()
		except:
			continue
			


@bot.message_handler(commands=["b", "z", "f"], func=is_my_message)
def freeze_me(msg):
	"""
	Функция, которая используется для заморозки значения кармы.
	"""
	user = select_user(msg.from_user, msg.chat)

	s=""
	if msg.text[1:2] == "b":
		n=10000
		if user.karma < n:
			bot.reply_to(msg, "Требуется кармы +10000")
			return
		freeze = None
		s="😎 безлимит на игры -10к"
	if msg.text[1:2] == "z":
		n=100
		if user.karma < n:
			bot.reply_to(msg, "Требуется кармы +100")
			return
		freeze = True
		s="🥶 карма заморожена -100"
	if msg.text[1:2] == "f":
		n=10
		freeze = False

	KarmaUser.update(is_freezed=freeze).where(
		(KarmaUser.userid == msg.from_user.id) &
		(KarmaUser.chatid == msg.chat.id)).execute()
	bot.reply_to(msg, f"Статус изменен {s}")
	user = bot.get_chat_member(msg.chat.id, msg.from_user.id)
	if user.status == 'creator':
		change_karma(msg.from_user, msg.chat, +50)
	else:
		change_karma(msg.from_user, msg.chat, -n)


@bot.message_handler(commands=["god"], func=is_my_message)
def gods(msg):
	"""
	позволяет создателю бота 
	добавить кому
	"""
	if len(msg.text.split()) == 1:
		return

	if msg.from_user.id not in config.gods:
		bot.reply_to(msg, "Ты не имеешь власти.")
		return
	result = int(msg.text.split()[1])
	change_karma(msg.reply_to_message.from_user, msg.chat, result)
	bot.delete_message(msg.chat.id, msg.message_id)


@bot.message_handler(commands=["gift"], func=reply_exist)
def gift_karma(msg):
	if msg.reply_to_message.from_user.is_bot:
		return
	if is_karma_abuse(msg):
		return
	if is_karma_freezed(msg):
		bot.reply_to(msg, "Разморозьте карму чтобы дарить!")
		return

	if msg.from_user.id == msg.reply_to_message.from_user.id:
		return
	
	user = select_user(msg.from_user, msg.chat)
	
	if user.is_freezed!=None:
		zamorozka(msg)
	random.seed(msg.message_id)
	newkarma =10
	try:
		if len(msg.text.split()) > 1:
			new = int(msg.text.split()[1])
			newkarma = abs(new)
			
		q=msg.text.count('🌹')
		if q>1:
			newkarma=10+q
			
		s=msg.text.count('❤')
		if s>1:
			newkarma=10+s
		
		if msg.text== '🎁':
			newkarma=random.randint(10, 100)
			
	except:
		print("error")
		
	if user.karma < newkarma:
		bot.reply_to(msg, "🎁 Нехватает кармы для подарка.")
		return
		
	otvet=""
	usera = bot.get_chat_member(msg.chat.id, msg.from_user.id)
	if usera.status == 'creator':
		change_karma(msg.reply_to_message.from_user, msg.chat, newkarma)
		otvet= f"🎁 Вам подарок <b>+{newkarma}</b>"
	else:
		change_karma(msg.from_user, msg.chat, -newkarma)
		change_karma(msg.reply_to_message.from_user, msg.chat, newkarma) 
		otvet= f"🎁 Вам подарок <b>+{newkarma}</b>"
			
	bot.reply_to(msg.reply_to_message, otvet, parse_mode="HTML")


@bot.message_handler(commands=["un"], func=is_my_message)
def un_mute(msg):
	"""
	Команда для создателя. Позволяет снять с 1-го пользователя ограничение
	на изменение кармы
	:param msg: Объект сообщения-команды
	"""
	if msg.from_user.id not in config.gods:
		return
	Limitation.delete().where(
		(Limitation.userid == msg.reply_to_message.from_user.id) &
		(Limitation.chatid == msg.chat.id)).execute()
	bot.send_message(msg.chat.id, "Возможность менять карму возвращена.")

def is_karma_changing(text):
	result = []
	# Проверка изменения кармы по смайликам
	if len(text) == 1:
		if text in config.good_emoji:
			result.append(1)
		if text in config.bad_emoji:
			result.append(-1)
		return result

	# Обработка текста для анализа
	text = text.lower()
	for punc in string.punctuation:
		text = text.replace(punc, "")
	for white in string.whitespace[1:]:
		text = text.replace(white, "")

	# Проверка изменения кармы по тексту сообщения
	for word in config.good_words:
		if word == text \
				or (" "+word+" " in text) \
				or text.startswith(word) \
				or text.endswith(word):
			result.append(1)

	for word in config.bad_words:
		if word in text \
				or (" "+word+" " in text) \
				or text.startswith(word) \
				or text.endswith(word):
			result.append(-1)
		
			
	return result
	
def is_karma_changing_mat(text):
	result = []
		
	if len(text)==1:
		result.append(-1)
	else:
		result.append(0)

			# Обработка текста для анализа
	text = text.lower()
	for punc in string.punctuation:
		text = text.replace(punc, "")
	for white in string.whitespace[1:]:
		text = text.replace(white, "")
		
	for word in config.mat_words:
		if word in text \
				or (" "+word+" " in text) \
				or text.startswith(word) \
				or text.endswith(word):
			result.append(-15)
			
	if len(text.split()) > 2:
		for word in config.heppy_words:
			if word in text \
					or (" "+word+" " in text) \
					or text.startswith(word) \
					or text.endswith(word):
				result.append(5)
	return result

def is_karma_freezed(msg):
	"""
	Функция для проверки индивидуальной блокировки кармы.
	"""

	# Выборка пользователей, связаных с сообщением.
	banned_request = KarmaUser.select().where(
		(KarmaUser.chatid == msg.chat.id) &
		(
			(KarmaUser.userid == msg.from_user.id) |
			(KarmaUser.userid == msg.reply_to_message.from_user.id)
		)
	)
	# У выбраных пользователей проверяется статус заморозки
	for req in banned_request:
		if req.is_freezed:
			return True
	return False


def is_game_abuse(msg):
	hours_ago_12 = pw.SQL(f"current_timestamp-interval'{random.randint(10, 120)} minutes'")
	limitation_request = Limitation.select().where(
		(Limitation.timer > hours_ago_12) &
		(Limitation.userid == msg.from_user.id) &
		(Limitation.chatid == msg.chat.id))

	if len(limitation_request) > 1:
		bot.delete_message(msg.chat.id, msg.message_id)
		return True
	return False
	
def is_karma_abuse(msg):
	hours_ago_12 = pw.SQL(f"current_timestamp-interval'{random.randint(5, 60)} minutes'")
	limitation_request = Limitation.select().where(
		(Limitation.timer > hours_ago_12) &
		(Limitation.userid == msg.from_user.id) &
		(Limitation.chatid == msg.chat.id))

	if len(limitation_request) > 2:
		return True
	return False


@bot.message_handler(commands=["бан"], func=reply_exist)
def zaBan(msg):
	if msg.chat.type == "private":
		return
	user = bot.get_chat_member(msg.chat.id, msg.reply_to_message.from_user.id)
	if user.status == 'administrator' or user.status == 'creator':
		return
	bot.send_message(msg.chat.id, f"<a href='tg://user?id=55910350'>🔫</a> <b>{msg.from_user.first_name}</b> предлагает выгнать <b>{msg.reply_to_message.from_user.first_name}</b> из Хабчата!", parse_mode="HTML")
	bot.send_poll(msg.chat.id, f'Согласны выгнать {msg.reply_to_message.from_user.first_name} из Чата?', ['Выгнать', 'Заткнуть', 'Простить'],is_anonymous=False)
	"""
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
				ot.stop_poll(msg.chat.id, mutePoll.id)
	"""
@bot.message_handler(commands=["stat"], func=is_my_message)
def stat(msg):

	result = KarmaUser.select(pw.fn.SUM(KarmaUser.karma).alias('total'))\
	.where(KarmaUser.chatid == msg.chat.id)

	bank=result.dicts()[0].get('total')
	
	

	bot.send_message(msg.chat.id,f'📊 Статистика <b>ХабЧата</b>\n\nУчастников: {bot.get_chat_members_count(chat_id=msg.chat.id)}\nВсего сообщений: <b>{msg.message_id}</b>\nБанк кармы: {bank}\n\nДень рождения: 19.04.2017', parse_mode="HTML")

def zamorozka(msg):
	usera = bot.get_chat_member(msg.chat.id, msg.from_user.id)
	if usera.status != 'creator':
		Limitation.create(
			timer=pw.SQL("current_timestamp"),
			userid=msg.from_user.id,
			chatid=msg.chat.id)
	
@bot.message_handler(commands=["пи","сиси"], func=is_my_message)
def cock(msg):
	user = select_user(msg.from_user, msg.chat)

	
	if is_game_abuse(msg):
		return
	if user.is_freezed!=None:
		zamorozka(msg)

	if user.is_freezed:
		bot.reply_to(msg, "Разморозьте карму чтобы играть!")
	else:
		if user.karma > 25:
			
			cock = random.randint(3, 25)
			if cock < 15: user_rang = "🙁" 
			if 15 <= cock < 20: user_rang = "😃"
			if 20 <= cock < 25: user_rang = "😎"
			random_karma = random.choice(["-","+"])
			change_karma(msg.from_user, msg.chat, f"{random_karma}{cock}")
			if msg.text[1:3] == "пи":
				bot.reply_to(msg,f"Мой писюн {random_karma}{cock}см {user_rang}", parse_mode="HTML")
			else:
				bot.reply_to(msg,f"Мои сиси {random_karma}{cock}-го размера {user_rang}", parse_mode="HTML")
		else:
			bot.delete_message(msg.chat.id, msg.message_id)

			
def commands(msg, text):
	if msg.reply_to_message:
		if msg.text.lower() == "/привет":
			bot.reply_to(msg.reply_to_message,f"✌ <b>{msg.reply_to_message.from_user.first_name}</b> приветствуем тебя в <b>ХабЧате</b>! По доброй традиции, желательно представиться и рассказать немного о себе.", parse_mode="HTML")
			return
		if msg.text.lower() == "/фото":
			bot.reply_to(msg.reply_to_message,f"<b>{msg.reply_to_message.from_user.first_name}</b> не соблаговолите ли вы скинуть в чат свою фоточку, нам будет очень приятно вас лицезреть 🙂", parse_mode="HTML")
			return
		if msg.text.lower() == "/фсб":
			bot.reply_to(msg.reply_to_message,f"<a href='https://telegra.ph/file/1a296399c86ac7a19777f.jpg'>😎</a> <b>{msg.reply_to_message.from_user.first_name}</b> за вами уже выехали!", parse_mode="HTML")
			return
		if msg.text.lower() == "/love":
			bot.reply_to(msg.reply_to_message, "❤ Знакомства в Хабаровске: @love_khv", parse_mode="HTML")
			return
	
	if msg.text.lower() == "/гороскоп":
		a = datetime.datetime.today()
		bot.reply_to(msg, f"<a href='https://khabara.ru/horoscop.html?{a}'>🔯</a>", parse_mode="HTML")
	        
	if msg.text.lower() == "/лимит":
		Limitation.delete().where(
			(Limitation.userid == msg.from_user.id) &
			(Limitation.chatid == msg.chat.id)).execute()
		change_karma(msg.from_user, msg.chat, -15)
		bot.reply_to(msg, "Лимит снят -15 кармы")
		return
		
	if msg.text.lower() == "/купить":
		bot.reply_to(msg,f"купить карму можно по <a href='https://khabara.ru/informer.html'>➡️ ссылке</a> +1 кармы = 1 р.", parse_mode="HTML")
		return
	if msg.text.lower() == "/кот":
		a = datetime.datetime.today()
		bot.send_photo(msg.chat.id, f"http://thecatapi.com/api/images/get?{a}", caption = f"ХабЧат 🐈 котик")
		return
	if msg.text.lower() == "/дата":
		a=datetime.datetime.today()+datetime.timedelta(hours=58)
		t = a.strftime("%Y%m%d")
		bot.send_photo(msg.chat.id, f"https://www.calend.ru/img/export/informer_names.png?{t}?{datetime.datetime.today()}", caption = f"ХабЧат 💬 есть неплохие поводы...")
		return
		
	if msg.text.lower() == "/qr":
		bot.send_photo(msg.chat.id, f"https://telegra.ph/file/9a1bc1986d13b024657c8.jpg", caption = f"QR-код сертификата вакцинации ХабЧатом")
		return
		
	if msg.text.lower() == "/утра":
		bot.reply_to(msg, f"С добрым утром, Хабаровск! ☀️ Вам отличного и позитивного настроения!!!", parse_mode="HTML")
		return
	if msg.text.lower() == "/шутка":
		bot.reply_to(msg, f"🤪 {getanekdot()}", parse_mode="HTML")
		return
	if msg.text.lower() == "/цитата":
		url = 'http://api.forismatic.com/api/1.0/'
		payload  = {'method': 'getQuote', 'format': 'json', 'lang': 'ru'}
		res = requests.get(url, params=payload)
		data = res.json()
		quote = data['quoteText']
		author = data['quoteAuthor']
		bot.reply_to(msg, f"📍 <i>{quote}</i> ©️ <b>{author}</b>", parse_mode="HTML")
		return
		
	seves = saves_database.get(database)
	if msg.text.lower() == seves:
		if saves_database.get(database_vopros)=="slovo":
			saves_database[database_vopros] = "victorina"
			try:
				bot.delete_message(msg.chat.id, saves_database.get(message_id_del2))
			except:
				print("error")
			msg_id = bot.reply_to(msg,f"🎉 Правильный ответ: <b>{seves}</b> +5 кармы\n Запустить Слово /slovo", parse_mode="HTML").message_id
			saves_database[message_id_del2] =msg_id
			change_karma(msg.from_user, msg.chat, 5)
			try:
				bot.delete_message(msg.chat.id, saves_database.get(message_id_del))
			except:
				print("error")
			return
		if saves_database.get(database_vopros)=="croco":
		
			seves_id = saves_database.get(database_id)
			seves_id_mute = saves_database.get(msg.from_user.id)
			seves_id_time = saves_database.get(msg.from_user.id+1)
			if seves_id_mute == 1:
				a=datetime.datetime.today() 
				b= seves_id_time+datetime.timedelta(minutes=15)
				if a < b:
					saves_database[msg.from_user.id]=0
					bot.restrict_chat_member(msg.chat.id, msg.from_user.id, until_date=time.time()+300)
					bot.delete_message(msg.chat.id, msg.message_id)
					bot.send_message(msg.chat.id,f'😶 <b>{msg.from_user.first_name}</b> Ограничен(а) на 5 минут за нарушения в Крокодиле.', parse_mode="HTML")
					change_karma(msg.from_user, msg.chat, -10)
				else:
					saves_database[msg.from_user.id]=0
				return
			if seves_id == msg.from_user.id:
				bot.reply_to(msg,f"Мухлевать не красиво: -10 кармы 💩", parse_mode="HTML")
				bot.delete_message(msg.chat.id, msg.message_id)
				change_karma(msg.from_user, msg.chat, -10)
				return
	
			saves_database[database] = "crocodila"
			saves_database[database_id]=0
			saves_database[msg.from_user.id]=1
			saves_database[msg.from_user.id+1]=datetime.datetime.today()
			try:
				bot.delete_message(msg.chat.id, saves_database.get(message_id_del2))
			except:
				print("error")
			msg_id = bot.reply_to(msg,f"🎉 Правильный ответ: <b>{seves}</b> +10 кармы\n Запустить игру /croco", parse_mode="HTML").message_id
			saves_database[message_id_del2] =msg_id
			change_karma(msg.from_user, msg.chat, 10)
			try:
				bot.delete_message(msg.chat.id, saves_database.get(message_id_del))
			except:
				print("error")
			return

		if saves_database.get(database_vopros)=="mine":
			saves_database[database_vopros] = "victorina"
			try:
				bot.delete_message(msg.chat.id, saves_database.get(message_id_del2))
			except:
				print("error")
			msg_id = bot.reply_to(msg,f"💰 Заработал: +20 кармы\n Запустить Майнер /mine", parse_mode="HTML").message_id
			saves_database[message_id_del2] =msg_id
			change_karma(msg.from_user, msg.chat, 20)
			try:
				bot.delete_message(msg.chat.id, saves_database.get(message_id_del))
			except:
				print("error")
			return

@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
	

		
	if  call.data == "Слово":
		bot.answer_callback_query(callback_query_id=call.id, show_alert=True,  text=f"Нужно угадать слово перемешанное из этих букв.")
		
	change_croco = saves_database.get(change_croco_2)
	seves_time = saves_database.get(database_time)
	idmy =seves_time+call.from_user.id
	idmy2=idmy+1
	idmy3=idmy+3
	
		
	if  f"{idmy}" == f"{call.data}":
		bot.answer_callback_query(callback_query_id=call.id, show_alert=True,  text=f"Задуманное слово: {saves_database[database]}")
		
	if  call.data == "Справка":
		bot.answer_callback_query(callback_query_id=call.id, show_alert=True,  text="Правила: 👀 - посмотреть слово 🔁 - сменить слово 🐊 - загадать эмодзи. Если отгадал и не запустил игру - ограничен на 5 минут.")

	if f"{idmy3}" == f"{call.data}":
		if change_croco<1:
			bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="🐊 Менять слово можно не более 2-ух раз 🚫")
			return
		
		saves_database[change_croco_2]=change_croco-1
		saves_database[database] = random.choice(config.kroko_emoji)
		bot.answer_callback_query(callback_query_id=call.id, show_alert=True,  text=f"Задуманное Эмодзи: {saves_database[database]}")
		bot.send_message(call.message.chat.id, f"🐊 {call.from_user.first_name} загадал <b>Эмодзи</b>", parse_mode="HTML")
		
	if f"{idmy2}" == f"{call.data}":
		if change_croco<1:
			bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="🐊 Менять слово можно не более 2-ух раз 🚫")
			return
		saves_database[change_croco_2]=change_croco-1
		saves_database[database] = random.choice(config.kroko_words)
		bot.answer_callback_query(callback_query_id=call.id, show_alert=True,  text=f"Задуманное слово: {saves_database[database]}")
		bot.send_message(call.message.chat.id, f"🐊 {call.from_user.first_name} сменил слово -5 кармы", parse_mode="HTML")
		change_karma(call.from_user, call.message.chat, -5)
		
	if  f"{idmy2}" != f"{call.data}":
		bot.answer_callback_query(callback_query_id=call.id, show_alert=True,  text=f"Слово знает только тот кто стартовал игру.")

	if  call.data == 1:
		bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, text="💥", reply_markup=keyboard)
		bot.send_message(call.message.chat.id, f"💥 {call.from_user.first_name} подорвался -5, перезапустить /bomb", parse_mode="HTML")
		change_karma(call.from_user, call.message.chat, -5)
	if  call.data == 2:
		bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, text="💣", reply_markup=keyboard)
		bot.send_message(call.message.chat.id, f"🎉 {call.from_user.first_name} обезвредил бомбу +5, перезапустить /bomb", parse_mode="HTML")
		change_karma(call.from_user, call.message.chat, 5)
	else:
		bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, text=" ", reply_markup=keyboard)
		
		
@bot.message_handler(commands=["croco", "крокодил"], func=is_my_message)
def croco(msg):
	saves_database[database_vopros] = "croco"
	if saves_database.get(database_id) ==  msg.from_user.id:
		bot.send_message(msg.chat.id,f'🐊 {msg.from_user.first_name} уже загадал слово.', parse_mode="HTML")
		bot.delete_message(msg.chat.id, msg.message_id)
		return
	else:
		try:
			bot.delete_message(msg.chat.id, saves_database.get(message_id_del))
		except:
			print("error")
		
	if saves_database.get(msg.from_user.id) ==  1:
		saves_database[msg.from_user.id]=0
	a=random.randint(1,1000)
	idmy =a+msg.from_user.id
	idmy2 =idmy+1
	idmy3=idmy+3
	saves_database[database_time] =a
	saves_database[change_croco_2] =2
	saves_database[database_id] =msg.from_user.id
	
	saves_database[database] = random.choice(config.kroko_words)
	
	markup = telebot.types.InlineKeyboardMarkup()
	button = telebot.types.InlineKeyboardButton(text='👀', callback_data=idmy)
	button3 = telebot.types.InlineKeyboardButton(text='🐊', callback_data=idmy3)
	button2 = telebot.types.InlineKeyboardButton(text='🔄', callback_data=idmy2)
	button4 = telebot.types.InlineKeyboardButton(text='Справка', callback_data="Справка")
	markup.add(button,button2,button3,button4)
	msg_id = bot.send_message(chat_id=msg.chat.id, text=f'🐊 {msg.from_user.first_name} загадал(а) слово в игре Крокодил.', reply_markup=markup).message_id
	saves_database[message_id_del] =msg_id
	bot.delete_message(msg.chat.id, msg.message_id)
	try:
		bot.delete_message(msg.chat.id, saves_database.get(message_id_del2))
	except:
		print("error")
		
		
@bot.message_handler(commands=["slovo"], func=is_my_message)
def slovo(msg):
	try:
		bot.delete_message(msg.chat.id, saves_database.get(message_id_del))
	except:
		print("error")
	if len(msg.text.split()) == 1:
		n=1
	else:
		n = int(msg.text.split()[1])
	word = random.choice(config.kroko_words)
	saves_database[database] = word
	
	word=[word[i:i+n] for i in range(0, len(word), n)]

	str_var = list(word)
	random.shuffle(str_var)
	abrakadabra= '  '.join(str_var)
	
	saves_database[database_vopros] = "slovo"
	saves_database[database_id]=0
	markup = telebot.types.InlineKeyboardMarkup()
	button = telebot.types.InlineKeyboardButton(text=f'Справка', callback_data="Слово")
	markup.add(button)
	msg_id = bot.send_message(chat_id=msg.chat.id, text=f'⁉️ Составь правильное слово из букв:\n\n{abrakadabra}', reply_markup=markup).message_id
	saves_database[message_id_del] =msg_id
	bot.delete_message(msg.chat.id, msg.message_id)
	try:
		bot.delete_message(msg.chat.id, saves_database.get(message_id_del2))
	except:
		print("error")
		

@bot.message_handler(commands=["bomb"], func=is_my_message)
def bomb(msg):
	try:
		bot.delete_message(msg.chat.id, saves_database.get(message_id_del))
	except:
		print("error")

	if len(msg.text.split()) == 1:
		n=9
	else:
		n = int(msg.text.split()[1])
	miner=random.sample(range(n), n)
	
	keyboard = telebot.types.InlineKeyboardMarkup()
	keyboard.row_width = 3

	for i in n:
		keyboard.add(telebot.types.InlineKeyboardButton(text=f'•', callback_data=miner[i]))
	msg_id = bot.send_message(chat_id=msg.chat.id, text=f'Разминируйте минное поле', reply_markup=keyboard).message_id
	saves_database[message_id_del] =msg_id
	bot.delete_message(msg.chat.id, msg.message_id)
	try:
		bot.delete_message(msg.chat.id, saves_database.get(message_id_del2))
	except:
		print("error")
		
		
@bot.message_handler(commands=["mine"], func=is_my_message)
def mine(msg):
	if is_game_abuse(msg):
		return
	user = select_user(msg.from_user, msg.chat)

	if user.is_freezed!=None:
		zamorozka(msg)
		
	if user.is_freezed:
		bot.reply_to(msg, f"Разморозьте карму чтобы играть!", parse_mode="HTML")
		return
		
	try:
		bot.delete_message(msg.chat.id, saves_database.get(message_id_del))
	except:
		print("error")
		


	x=random.choice(string.ascii_lowercase)
	word=ord(x)
	saves_database[database] = f"{word}"
	saves_database[database_vopros] = "mine"
	saves_database[database_id]=0
	msg_id = bot.send_photo(msg.chat.id, f"https://telegra.ph/file/5c67b8eb309098ca0514f.jpg", caption = f"Перейдите <a href='https://khabara.ru/tg/{x}-karma.html'>💰 По ссылке</a> и введите полученный секретный код в чат.", parse_mode="HTML").message_id
	

	
	saves_database[message_id_del] =msg_id
	bot.delete_message(msg.chat.id, msg.message_id)
	try:
		bot.delete_message(msg.chat.id, saves_database.get(message_id_del2))
	except:
		print("error")
		
	
	
def getanekdot():
	z=''
	s=requests.get('http://anekdotme.ru/random')
	b=bs4.BeautifulSoup(s.text, "html.parser")
	p=b.select('.anekdot_text')
	for x in p:        
		s=(x.getText().strip())
		z=z+s+'\n\n'
	return s
	
@bot.message_handler(commands=["save","сохранить"], func=is_my_message)
def save(msg):
		
	bot.forward_message(-1001338159710, msg.chat.id, msg.reply_to_message.message_id)
	bot.reply_to(msg.reply_to_message,f"⁉️ Сообщение сохранено в <a href='https://t.me/joinchat/T8KyXgxSk1o4s7Hk'>Цитатник ХабЧата</a>.", parse_mode="HTML")
	
@bot.message_handler(commands=["вопрос"], func=is_my_message)
def khvtrip(msg):
	user = bot.get_chat_member(msg.chat.id, msg.from_user.id)
	if user.status == 'creator':
		bot.send_message(-1001310162579,f'⁉️ {msg.reply_to_message.text}', parse_mode="HTML")
		bot.reply_to(msg.reply_to_message,f"⁉️ Вопрос отправлен <a href='https://t.me/khvtrip'>Знатокам Хабаровска</a>", parse_mode="HTML")
	else:
		bot.reply_to(msg.reply_to_message,f"<a href='tg://user?id=55910350'>️⁉</a> Вопросы про Хабаровск: @khvtrip", parse_mode="HTML")
	
@bot.message_handler(commands=["?"], func=is_my_message)
def q(msg):
	if len(msg.text.split()) == 1:
		bot.delete_message(msg.chat.id, msg.message_id)
		return
	random_karma = ("Абсолютно точно!","Да.","Нет.","Скорее да, чем нет.","Не уверен...","Однозначно нет!","Если ты не фанат аниме, у тебя все получится!","Можешь быть уверен в этом.","Перспективы не очень хорошие.","А как же иначе?.","Да, но если только ты не смотришь аниме.","Знаки говорят - да.","Не знаю.","Мой ответ - нет.","Весьма сомнительно.","Не могу дать точный ответ.")
	bot.reply_to(msg, f"🔮 {random.choice(random_karma)}", parse_mode="HTML")
	  
def reputation(msg, text):
	""" TODO """

	# Если сообщение большое, то прервать выполнение функции
		
	if len(text) > 100:
		return

	if set(['🔫','🔪','🪓','🧨','💣','⚔️','🗡','🥊','🏹','🦾','✊','👊','🤛','🤜','💪','☠']) & set(text):
		duel(msg)
		return
		
	if set(['🎁','🌹','❤']) & set(text):
		gift_karma(msg)
		return

	# Если карму не пытаются изменить, то прервать выполнение функции
	how_much_changed = is_karma_changing(text)
	if not how_much_changed:
		return

	# При попытке поднять карму самому себе прервать выполнение функции
	if msg.from_user.id == msg.reply_to_message.from_user.id:
		bot.send_message(msg.chat.id, "Нельзя изменять карму самому себе.")
		return

	# Ограничение на изменение кармы для пользователя во временной промежуток
	if is_karma_abuse(msg):
		return

	if is_karma_freezed(msg):
		return
	if msg.reply_to_message.from_user.is_bot:
		return
	# Если значение кармы все же можно изменить: изменяем
	result = sum(how_much_changed)
	if result != 0:
		zamorozka(msg)
		change_karma(msg.reply_to_message.from_user, msg.chat, result)

	if result > 0:
		res = "повышена ⬆️"
	elif result < 0:
		res = "понижена ⬇️"
	else:
		res = "не изменена"

	user = KarmaUser.select().where(
		(KarmaUser.userid == msg.reply_to_message.from_user.id) &
		(KarmaUser.chatid == msg.chat.id)).get()

	if not user.user_name.isspace():
		name = user.user_name.strip()
	else:
		name = user.user_nick.strip()
		

	now_karma = f"Карма {res}\n{name}: <b>{user.karma}</b>"
	bot.send_message(msg.chat.id, now_karma, parse_mode="HTML")

def reputation_mat(msg, text):
	""" TODO понижение репутации за маты"""
	
	how_much_changed = is_karma_changing_mat(text)
	if not how_much_changed:
		return
	user = select_user(msg.from_user, msg.chat)
	if user.is_freezed==None:
		change_karma(msg.from_user, msg.chat, 0)
		return
	# Если значение кармы все же можно изменить: изменяем
	result = sum(how_much_changed)
	change_karma(msg.from_user, msg.chat, result)
		

@bot.message_handler(content_types=["text"], func=reply_exist)
def handler_karma_text(msg):
	if msg.chat.type == "private":
		return
	reputation(msg, msg.text)
	reputation_mat(msg, msg.text)
	commands(msg, msg.text)
	
@bot.message_handler(content_types=['text'])	
def handler_karma(msg):
	if msg.chat.type == "private":
		return
	reputation_mat(msg, msg.text)
	commands(msg, msg.text)

@bot.message_handler(content_types=["sticker"], func=reply_exist)
def handler_karma_sticker(msg):
	if msg.chat.type == "private":
		return
	reputation(msg, msg.sticker.emoji)
	
@bot.channel_post_handler(content_types=["text",'photo','video'])
def channel_post(msg):
	if msg.caption !=None:
		if '✉️' in msg.caption or '➡️' in msg.caption:
			bot.forward_message(-1001110839896, msg.chat.id, msg.message_id)
			return
	else:
		if '✉️' in msg.text or '➡️' in msg.text:
			bot.forward_message(-1001110839896, msg.chat.id, msg.message_id)
				
@bot.message_handler(content_types=['dice'])
def send_dice(msg):
	if msg.chat.type == "private":
		return
	if msg.forward_from :
		bot.delete_message(msg.chat.id, msg.message_id)
	else:
		try:
			user = select_user(msg.from_user, msg.chat)
			if not user:
				insert_user(msg.from_user, msg.chat)
				bot.delete_message(msg.chat.id, msg.message_id)
		except Exception:
			insert_user(msg.from_user, msg.chat)
			bot.delete_message(msg.chat.id, msg.message_id)
			
		user = select_user(msg.from_user, msg.chat)
		if is_game_abuse(msg):
			return
		if user.is_freezed!=None:
			zamorozka(msg)
			
		if user.is_freezed:
			bot.reply_to(msg, "Разморозьте карму чтобы играть!")
			return

		else:
			if user.karma > msg.dice.value:
				
				random_karma = random.choice(["-","+"])
				bot.reply_to(msg, f"Сыграл в карму {random_karma}{msg.dice.value}", parse_mode="HTML")
				user = bot.get_chat_member(msg.chat.id, msg.from_user.id)
				if user.status == 'creator':
					change_karma(msg.from_user, msg.chat, f"+{msg.dice.value}")
				else:
					change_karma(msg.from_user, msg.chat, f"{random_karma}{msg.dice.value}")
			else:
				bot.delete_message(msg.chat.id, msg.message_id)
				

# bot.polling(none_stop=True)


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
