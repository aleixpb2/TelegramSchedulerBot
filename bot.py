#!/usr/bin/env python3

import telebot
from enum import Enum

# Commands
# create_event - Create an event
# delete_event - Delete an event

def printDebug(message):
    print(str(message.chat.id) + ": " + message.text)

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
    print(states)
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
    if(states[message.chat.id] == stateEnum.create_event):
        print("CREATING")
    #bot.reply_to(message, message.text)

bot.polling()
