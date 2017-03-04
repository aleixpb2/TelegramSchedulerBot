#!/usr/bin/env python3

import telebot

# Commands
# create_event - Create an event
# delete_event - Delete an event

TOKEN = '276486690:AAHVjZ369ib_Ms52vnEfY8s8D9Il0FxHyQA'
bot = telebot.TeleBot(TOKEN)
#bot.get_me()


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    print(message.text)
    bot.send_message(message.chat.id, "Hi! Welcome to the Telegram Scheduler Bot")


@bot.message_handler(commands=['create_event'])
def create_event(message):
    bot.send_message(message.chat.id,
                     "Fine! Now send me the starting time and the ending time in "
                     "the following format:\n`dd/MM/yyyy HH:mm`",
                     parse_mode="Markdown")

@bot.message_handler(commands=['delete_event'])
def create_event(message):
    bot.send_message(message.chat.id,
                     "Fine! Now send me the starting time and the ending time in "
                     "the following format:\n`dd/MM/yyyy HH:mm`",
                     parse_mode="Markdown")


@bot.message_handler(func=lambda message: True)
def echo_all(message):

    print("Message: ", message.text)
    bot.reply_to(message, message.text)

bot.polling()
