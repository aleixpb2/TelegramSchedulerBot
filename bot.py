#!/usr/bin/env python3
import httplib2
from apiclient import discovery
import time
import telebot
from telebot import types
import datetime
from enum import Enum

import CalendarSyncr
from google_credentials import app
from google_credentials import GoogleCredentials
import getopt
import sys
import flask
import logging

# Commands
# create_event - Create an event
# from - Starting time
# to - Ending time
# duration - Duration of the event

def printDebug(message):
    print(str(message.chat.id) + ": " + message.text)

def myfun():
    return None

def read_date(message, offset): # offset is to ignore commands /from and /to
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

def get_data(id):
    return data[id]

def showSlots(id, tini, slots): # slots: initialValue endValue
    bot.send_message(id, "Dates available to everyone:")
    for elem in slots:
        tinitial = CalendarSyncr.get_timedate_from_minutes(tini, elem[0])
        tend = CalendarSyncr.get_timedate_from_minutes(tini, elem[1])
        bot.send_message(id, "From " + tinitial + " to " + tend)


TOKEN = '276486690:AAHVjZ369ib_Ms52vnEfY8s8D9Il0FxHyQA'
bot = telebot.TeleBot(TOKEN)
stateEnum = Enum('state', 'none create_event delete_event from_create to_create dur_create from_delete to_delete dur_delete')
states = dict()
data = dict()
gc = GoogleCredentials(myfun)

WEBHOOK_HOST = "jormaig.siliconpeople.net"
WEBHOOK_PORT = 8443
WEBHOOK_LISTEN = "0.0.0.0"
#WEBHOOK_LISTEN = "172.31.25.192"

WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Path to the ssl private key

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/telegram_update/"


logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

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
        d = read_date(message, len("/from ")) # print(d.strftime("%A"))
        data[message.chat.id].append(d)
    elif states[message.chat.id] == stateEnum.delete_event:
        states[message.chat.id] = stateEnum.from_delete
        d = read_date(message, len("/from "))
        data[message.chat.id].append(d)
    else:
        bot.send_message(message.chat.id, "Unexpected command")

@bot.message_handler(commands=['to'])
def to_inp(message):
    printDebug(message)
    if states[message.chat.id] == stateEnum.from_create:
        states[message.chat.id] = stateEnum.to_create
        d = read_date(message, len("/to "))
        data[message.chat.id].append(d)
    elif states[message.chat.id] == stateEnum.from_delete:
        states[message.chat.id] = stateEnum.to_delete
        d = read_date(message, len("/to "))
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
        data[message.chat.id].append(bot.get_chat_members_count(message.chat.id))
        print("Data: " + str(data[message.chat.id]))
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
        data[message.chat.id].append(bot.get_chat_members_count(message.chat.id))
        print("Data: " + str(data[message.chat.id]))
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
        CalendarSyncr.send_credentials(credentials)

    else:
        bot.send_message(call.from_user.id, "Click this link to accept Google Calendar integration: " + gc.get_credentials_url())


# Process webhook calls
@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    logger.debug("Webhook received")
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


@app.route("/test_route")
def test_route():
    logger.debug("The test route is working properly")
    return "Hello world"


############# PART LAIA


global PAX_COUNT
L = []


def get_events(init_t,end_t, sv,calend):
    now = init_t.isoformat() + 'Z'  # 'Z' indicates UTC time

    t = end_t.isoformat() + 'Z'
    eventsResult = sv.events().list(
            calendarId=calend, timeMax=t, timeMin=now, singleEvents=True,
            orderBy='startTime').execute()
    events = eventsResult.get('items', [])
    return events
def get_timedate_from_minutes (timedate_ini, minutes_passed):

    newtime = timedate_ini + datetime.timedelta(minutes=minutes_passed)
    return newtime

def get_minutes_between_dates (time_0,time_1):

    #roundedA = time_0.replace(second=0, microsecond=0)
    #roundedB = time_1.replace(second=0, microsecond=0)
    time_elapsed =time_1 - time_0
    minutes = (time_elapsed.seconds/60) + time_elapsed.days*1440
    return minutes
def add_occupied_slots (init_time,end_time,cal,l,duration=60):

    strformat = "%Y-%m-%dT%H:%M:%S"
    for event in cal:
        # many stuff to show event in datetime instead of string
        event_start = event['start'].get('dateTime',event['start'].get('date')) # type string
        event_start= event_start[:19]
        event_start_dt = datetime.datetime.strptime(event_start, strformat)
        event_end = event['end'].get('dateTime',event['end'].get('date')) #type string
        event_end = event_end[:19]
        event_end_dt = datetime.datetime.strptime(event_end,strformat)

        start_time = get_minutes_between_dates(init_time,event_start_dt)
        end_time = get_minutes_between_dates(init_time,event_end_dt)
        if start_time>0 and end_time>0:
            l.append([start_time,end_time])
    return sorted(l)

def get_available_slots (init_time,end_time,l,duration=60):
    #init_time and end_time should be DATETIME !!!
    accepted_times = []
    if l[0][0]>0:
        accepted_times.append([0,l[0][0]])
    for i in range (len (l)-1):
        if l[i][1]<l[i+1][0] and l[i+1][0]-l[i][1]>duration:
            accepted_times.append([l[i][1],l[i+1][0]])
    return accepted_times
"""def SincronizeCalendars(init_time,end_time,duration,calendars):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    calendars = []
    events = get_events (init_time,end_time,service,calendars)
    q = get_available_slots([events], init_time, end_time,duration=duration)
    for i in q:

        print("from")
        print (get_timedate_from_minutes(init_time, i[0]))
        print ("to ")
        print (get_timedate_from_minutes(init_time, i[1]))
        print ("---------------------------------------------------------------")
"""

def callbackfunction():
    print ("Person accepted")
    return None
def get_calendars (usr,sv):
    calendar_list = sv.calendarList().list(pageToken=usr).execute()
    return calendar_list

def send_credentials (usr_credential):
    global PAX_COUNT
    tini, tfi, duration, people = get_data()
    PAX_COUNT = PAX_COUNT + 1
    http = usr_credential.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    cal_list = get_calendars (usr_credential,service)
    for calend in cal_list:
        L=sorted(L)
        if PAX_COUNT==people:
            slots = get_available_slots(tini,tfi,L,duration)
            showSlots(usr_credential, tini, slots)
    return None

if __name__ == "__main__":
    print("test")
    options, args = getopt.gnu_getopt(sys.argv, 'r', ['remote'])
    remote = False
    for o, a in options:
        if o in ("-r", "--remote"):
            remote = True

    if remote:
        logger.debug("Removing webhook")
        bot.remove_webhook()
        time.sleep(2)
        logger.debug("Setting new webhook")
        bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                        certificate=open(WEBHOOK_SSL_CERT, 'r'))
        app.run(host=WEBHOOK_LISTEN,
                port=WEBHOOK_PORT,
                ssl_context=(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV),
                debug=True,
                threaded=True)
    else:
        bot.polling()

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

