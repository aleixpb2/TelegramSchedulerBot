#from __future__ import print_function
import httplib2
import os
import sys
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from google_credentials import GoogleCredentials
import datetime

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


def get_events(init_t,end_t, sv):
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    print('Getting the upcoming month')
    week = datetime.timedelta(days=10)
    t = (datetime.datetime.utcnow() + week).isoformat() + 'Z'


    # DO THIS FOR ALL CALENDARS !!! :I
    eventsResult = sv.events().list(
        calendarId='primary', timeMax=t, timeMin=now, singleEvents=True,
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
def get_available_slots (calendars,init_time,end_time, duration=60):
    #init_time and end_time should be DATETIME !!!
    l = []
    strformat = "%Y-%m-%dT%H:%M:%S"
    for cal in calendars:
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
    l=sorted(l)
    accepted_times = []
    if l[0][0]>0:
        accepted_times.append([0,l[0][0]])
    for i in range (len (l)-1):
        if l[i][1]<l[i+1][0] and l[i+1][0]-l[i][1]>duration:
            accepted_times.append([l[i][1],l[i+1][0]])
    return accepted_times

def SincronizeCalendars(init_time,end_time,duration):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    events = get_events (init_time,end_time,service)
    q = get_available_slots([events], init_time, end_time,duration=duration)
    for i in q:

        print("from")
        print (get_timedate_from_minutes(init_time, i[0]))
        print ("to ")
        print (get_timedate_from_minutes(init_time, i[1]))
        print ("---------------------------------------------------------------")

def callbackfunction():
    print ("Person accepted")
    return None
def main(future_days):
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    print("Starting")
    credentials = get_credentials()

    #gc = GoogleCredentials(callbackfunction)
    #new_url = gc.get_credentials_url()


    #if gc.has_credentials():
     #   user_url = gc.get_credentials_url()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    get_time_now = datetime.datetime.utcnow()
    get_time_then = datetime.datetime(2017, 2, 10, 11, 19, 55)
    SincronizeCalendars(get_time_now,get_time_then,60)

    """
    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])
    """

if __name__ == '__main__':
    days = 10
    if len(sys.argv) > 1:
        days = int(sys.argv[1])
    main(days)
