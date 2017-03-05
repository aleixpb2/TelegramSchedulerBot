#from __future__ import print_function
import httplib2
import os
import sys
import bot
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from google_credentials import GoogleCredentials
import datetime
from bot import get_data
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Calendar Syncronization'

global PAX_COUNT
L = []

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if True:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES, redirect_uri="http://localhost")
        flow.user_agent = APPLICATION_NAME
        print("Url:", flow.step1_get_authorize_url())
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


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
            bot.showSlots(usr_credential, tini, slots)
    return None


def main():
    global PAX_COUNT
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    PAX_COUNT = 0
    print("Starting")
    #credentials = get_credentials()


if __name__ == '__main__':
    main()
