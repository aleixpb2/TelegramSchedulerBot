#!/usr/bin/env python3

import telebot
from telebot import types
import datetime
from enum import Enum
from google_credentials import GoogleCredentials

from google_credentials import *

# Commands
# create_event - Create an event
# delete_event - Delete an event
# from - Starting time
# to - Ending time
# duration - Duration of the event


def printDebug(message):
    print(str(message.chat.id) + ": " + message.text)

def myfun():
    return None

def readDate(message, offset): # offset is to ignore commands /from and /to
    # assume input is correct...
    day = int(message.text[offset:(offset+2)])
    month = int(message.text[(offset+3):(offset+5)])
    year = int(message.text[(offset+6):(offset+10)])
    hour = int(message.text[(offset+11):(offset+13)])
    minute = int(message.text[(offset+14):(offset+16)])
    print("Date is " + str(day) + " " +  str(month) + " " + str(year) + " " + str(hour) + " " + str(minute))
    return datetime.datetime(year, month, day, hour, minute)


def sendKeyboardButton(bot, id):
    markup = types.InlineKeyboardMarkup()
    itembtna = types.InlineKeyboardButton('Participate', callback_data="Participate")
    markup.add(itembtna)
    bot.send_message(id, "Click to participate in this event:", reply_markup=markup)


TOKEN = '276486690:AAHVjZ369ib_Ms52vnEfY8s8D9Il0FxHyQA'
bot = telebot.TeleBot(TOKEN)
stateEnum = Enum('state', 'none create_event delete_event from_create to_create dur_create from_delete to_delete dur_delete')
states = dict()
data = dict()
gc = GoogleCredentials(myfun)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    printDebug(message)
    states[message.chat.id] = stateEnum.none
    bot.send_message(message.chat.id, "Hi! Welcome to the Telegram Scheduler Bot")


@bot.message_handler(commands=['create_event'])
def create_event(message):
    printDebug(message)
    states[message.chat.id] = stateEnum.create_event
    data[message.chat.id] = []
    bot.send_message(message.chat.id,
                     "Fine! Now send me the starting time (/from ) and the ending time (/to) in "
                     "the following format:\n`dd/MM/yyyy HH:mm`, and the duration (/duration) in minutes",
                     parse_mode="Markdown")


@bot.message_handler(commands=['delete_event'])
def delete_event(message):
    printDebug(message)
    states[message.chat.id] = stateEnum.delete_event
    data[message.chat.id] = []
    bot.send_message(message.chat.id,
                     "Fine! Now send me the starting time (/from ) and the ending time (/to) in "
                     "the following format:\n`dd/MM/yyyy HH:mm`, and the duration (/duration) in minutes",
                     parse_mode="Markdown")

@bot.message_handler(commands=['from'])
def from_inp(message):
    printDebug(message)
    if states[message.chat.id] == stateEnum.create_event:
        states[message.chat.id] = stateEnum.from_create
        d = readDate(message, len("/from ")) # print(d.strftime("%A"))
        data[message.chat.id].append(d)
    elif states[message.chat.id] == stateEnum.delete_event:
        states[message.chat.id] = stateEnum.from_delete
        d = readDate(message, len("/from "))
        data[message.chat.id].append(d)
    else:
        bot.send_message(message.chat.id, "Unexpected command")

@bot.message_handler(commands=['to'])
def to_inp(message):
    printDebug(message)
    if states[message.chat.id] == stateEnum.from_create:
        states[message.chat.id] = stateEnum.to_create
        d = readDate(message, len("/to "))
        data[message.chat.id].append(d)
    elif states[message.chat.id] == stateEnum.from_delete:
        states[message.chat.id] = stateEnum.to_delete
        d = readDate(message, len("/to "))
        data[message.chat.id].append(d)
    else:
        bot.send_message(message.chat.id, "Unexpected command")

@bot.message_handler(commands=['duration'])
def dur_inp(message):
    printDebug(message)
    if states[message.chat.id] == stateEnum.to_create:
        dur = int(message.text[len("/duration "):])
        print("Duration is " + str(dur))
        data[message.chat.id].append(dur)
        print("Data: " + str(data[message.chat.id]))
        ############# SEND data
        # Event created
        bot.send_message(message.chat.id, "Event created")
        #url = gc.get_credentials_url()
        #bot.send_message(message.chat.id, url)
        states[message.chat.id] = stateEnum.none
        sendKeyboardButton(bot, message.chat.id)
    elif states[message.chat.id] == stateEnum.to_delete:
        dur = int(message.text[len("/duration "):])
        print("Duration is " + str(dur))
        data[message.chat.id].append(dur)
        print("Data: " + str(data[message.chat.id]))
        ############# SEND data
        # Delete event
        bot.send_message(message.chat.id, "Event deleted")
        states[message.chat.id] = stateEnum.none
    else:
        bot.send_message(message.chat.id, "Unexpected command")

@bot.message_handler(func=lambda message: True)
def default(message):
    printDebug(message)

@bot.callback_query_handler(func=lambda call: True)
def  test_callback(call):
    print(call)
    print("User: " + str(call.from_user) + " User id: " + str(call.from_user.id))
    if gc.has_credentials(str(call.from_user.id)):
        credentials = gc.get_credentials(str(call.from_user.id))
        
    else:
        bot.send_message(call.from_user.id, "Click this link to accept Google Calendar integration: " + gc.get_credentials_url())


# @bot.callback_query_handler(func=lambda call: True)
# def callback_inline(call):
#     if call.inline_message_id:
#         if call.data == "1":
#             keyboard = types.InlineKeyboardMarkup(row_width=3)
#             a = types.InlineKeyboardButton(text=" ", callback_data="2")
#             b = types.InlineKeyboardButton(text=" ", callback_data="2")
#             c = types.InlineKeyboardButton(text=" ", callback_data="2")
#             d = types.InlineKeyboardButton(text=" ", callback_data="2")
#             e = types.InlineKeyboardButton(text=" ", callback_data="2")
#             f = types.InlineKeyboardButton(text=" ", callback_data="2")
#             g = types.InlineKeyboardButton(text=" ", callback_data="2")
#             h = types.InlineKeyboardButton(text=" ", callback_data="2")
#             i = types.InlineKeyboardButton(text=" ", callback_data="2")
#             keyboard.add(a, b, c, d, e, f, g, h, i)
#             bot.edit_message_text(inline_message_id = call.inline_message_id, text = "X", reply_markup=keyboard)


bot.polling()
print("Hello world")
app.run()

# Call example
# {'message': {'left_chat_member': None, 'audio': None, 'new_chat_title': None, 'venue': None,
#              'new_chat_photo': None, 'forward_from': None, 'migrate_from_chat_id': None,
#              'content_type': 'text', 'caption': None, 'group_chat_created': None,
#              'supergroup_chat_created': None, 'pinned_message': None,
#              'from_user': <telebot.types.User object at 0x00000225D50422E8>, 'video': None,
#              'voice': None, 'channel_chat_created': None, 'photo': None, 'date': 1488680389,
#             'document': None, 'edit_date': None, 'message_id': 329, 'entities': None, 'new_chat_member': None,
#             'sticker': None, 'reply_to_message': None, 'forward_date': None, 'delete_chat_photo': None,
#             'chat': <telebot.types.Chat object at 0x00000225D504F6D8>, 'contact': None, 'migrate_to_chat_id': None,
#             'forward_from_chat': None, 'text': 'Click to participate in this event:', 'location': None},
#
# 'data': 'Participate', 'id': '53080350164034740', 'from_user': {'username': 'Aleixpb2', 'id': 12358732,
#                                                                 'first_name': 'Aleix', 'last_name': None},
# 'game_short_name': None, 'chat_instance': '8816884457208723824', 'inline_message_id': None}
