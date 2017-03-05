#!/usr/bin/env python3

import telebot
import datetime
from enum import Enum


# Commands
# create_event - Create an event
# delete_event - Delete an event

def printDebug(message):
    print(str(message.chat.id) + ": " + message.text)


def readDate(message):
    # assume input is correct
    day = int(message.text[0:2])
    month = int(message.text[3:5])
    year = int(message.text[6:10])
    hour = int(message.text[11:13])
    minute = int(message.text[14:16])
    # print(day + " " +  month + " " + year + " " + hour + " " + minute)
    return datetime.datetime(year, month, day, hour, minute)


TOKEN = '276486690:AAHVjZ369ib_Ms52vnEfY8s8D9Il0FxHyQA'
bot = telebot.TeleBot(TOKEN)
stateEnum = Enum('state', 'none create_event delete_event')
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
                     "Fine! Now send me the starting time and the ending time in "
                     "the following format:\n`dd/MM/yyyy HH:mm`",
                     parse_mode="Markdown")


@bot.message_handler(commands=['delete_event'])
def delete_event(message):
    printDebug(message)
    states[message.chat.id] = stateEnum.delete_event
    bot.send_message(message.chat.id,
                     "Fine! Now send me the starting time and the ending time in "
                     "the following format:\n`dd/MM/yyyy HH:mm`",
                     parse_mode="Markdown")


@bot.message_handler(func=lambda message: True)
def default(message):
    printDebug(message)
    if states[message.chat.id] == stateEnum.create_event:
        d = readDate(message)
        #print(d.strftime("%A"))
        ########### CODE TO CREATE THE EVENT
        bot.send_message(message.chat.id, "Event created")
        states[message.chat.id] = stateEnum.none
    elif states[message.chat.id] == stateEnum.delete_event:
        d = readDate(message)
        ########### CODE TO DELETE THE EVENT
        bot.send_message(message.chat.id, "Event deleted")
        states[message.chat.id] = stateEnum.none
    else:
        bot.send_message(message.chat.id, "Can't understand")

bot.polling()
