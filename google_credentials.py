#!/usr/bin/env python3

import os
import sys
import httplib2
import bot
from apiclient import discovery
import datetime
from bot import get_data
from oauth2client import client
from oauth2client.file import Storage
from flask import Flask
from flask.views import View
from flask import request
app = Flask(__name__)

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'TelegramSchedulerBot'


class GoogleCredentials(View):

    def __init__(self, callback):
        self.callback = callback

    @staticmethod
    def get_credential_path(user):
        user = str(user)
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        return os.path.join(credential_dir, '%s-calendar.json' % user)

    @staticmethod
    def has_credentials(user):
        credential_path = GoogleCredentials.get_credential_path(str(user))
        if os.path.exists(credential_path):
            credentials = Storage(credential_path).get()
            return credentials and not credentials.invalid
        return False

    @staticmethod
    def get_credentials_url():
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES,
                                              redirect_uri="https://jormaig.siliconpeople.net:8443/"
                                                           "login_successful")
        flow.user_agent = APPLICATION_NAME
        url = flow.step1_get_authorize_url()
        print("Url:", url)
        return url

    @staticmethod
    def get_credentials(user):
        print("Getting credentials")
        credentials_path = GoogleCredentials.get_credential_path(user)
        if not os.path.exists(credentials_path):
            print("Path not found")
            return None
        return Storage(credentials_path).get()

    def dispatch_request(self):
        print("Request received")
        print(request.url)
        print(request.query_string)
        self.callback()
        return "Login successful"


app.add_url_rule('/login_successful', view_func=GoogleCredentials.as_view('google_credentials'))


