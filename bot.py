#!/usr/bin/env python3

import telebot
from telebot import types
import datetime
from enum import Enum


# Commands
# create_event - Create an event
# delete_event - Delete an event
# from - Starting time
# to - Ending time
# duration - Duration of the event

def printDebug(message):
    print(str(message.chat.id) + ": " + message.text)


def readDate(message, offset): # offset is to ignore commands /from and /to
    # assume input is correct
    day = int(message.text[offset:2])
    month = int(message.text[(offset+3):5])
    year = int(message.text[(offset+6):10])
    hour = int(message.text[(offset+11):13])
    minute = int(message.text[(offset+14):16])
    # print(day + " " +  month + " " + year + " " + hour + " " + minute)
    return datetime.datetime(year, month, day, hour, minute)


def sendKeyboardButton(bot, id):
    markup = types.InlineKeyboardMarkup()
    itembtna = types.InlineKeyboardButton('Participate', callback_data="Participate")
    markup.add(itembtna)
    bot.send_message(id, "Click to participate in this event:", reply_markup=markup)


TOKEN = '276486690:AAHVjZ369ib_Ms52vnEfY8s8D9Il0FxHyQA'
bot = telebot.TeleBot(TOKEN)
stateEnum = Enum('state', 'none create_event delete_event from_inp to_inp dur_inp')
states = dict()


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    printDebug(message)
    states[message.chat.id] = stateEnum.none
    bot.send_message(message.chat.id, "Hi! Welcome to the Telegram Scheduler Bot")


@bot.message_handler(commands=['create_event'])
def create_event(message):
    printDebug(message)
    states[message.chat.id] = stateEnum.create_event
    bot.send_message(message.chat.id,
                     "Fine! Now send me the starting time (/from )and the ending time (/to) in "
                     "the following format:\n`dd/MM/yyyy HH:mm`, and the duration (/duration) in minutes",
                     parse_mode="Markdown")


#######################     TODO ANALOGOUS OF CREATE_EVENT
@bot.message_handler(commands=['delete_event'])
def delete_event(message):
    printDebug(message)
    states[message.chat.id] = stateEnum.delete_event
    bot.send_message(message.chat.id,
                     "Fine! Now send me the starting time (/from )and the ending time (/to) in "
                     "the following format:\n`dd/MM/yyyy HH:mm`, and the duration (/duration) in minutes",
                     parse_mode="Markdown")

@bot.message_handler(commands=['from'])
def from_inp(message):
    printDebug(message)
    if states[message.chat.id] == stateEnum.create_event:
        states[message.chat.id] = stateEnum.from_inp
        d = readDate(message, 6)
        # print(d.strftime("%A"))
    else:
        bot.send_message(message.chat.id, "Unexpected command")

@bot.message_handler(commands=['to'])
def to_inp(message):
    printDebug(message)
    if states[message.chat.id] == stateEnum.from_inp:
        states[message.chat.id] = stateEnum.to_inp
        d = readDate(message, 4)
    else:
        bot.send_message(message.chat.id, "Unexpected command")

@bot.message_handler(commands=['duration'])
def dur_inp(message):
    printDebug(message)
    if states[message.chat.id] == stateEnum.to_inp:
        dur = int(message.text)

        # Event created
        bot.send_message(message.chat.id, "Event created")
        states[message.chat.id] = stateEnum.none
        sendKeyboardButton(bot, message.chat.id)
    else:
        bot.send_message(message.chat.id, "Unexpected command")

@bot.message_handler(func=lambda message: True)
def default(message):
    printDebug(message)

@bot.callback_query_handler(func=lambda call: True)
def  test_callback(call):
    print(call)
    # Do stuff

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
