import os.path
import json
from email.mime.text import MIMEText
from base64 import urlsafe_b64encode

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GmailWrapper:
    def __init__(self, client_secret_file='client_secret.json'):
        self.client_secret_file = client_secret_file
        self.scopes = [
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.compose",
            "https://www.googleapis.com/auth/userinfo.email"
        ]
        
    # Public Methods

    def send_email(self, to, subject, message, credentials_json):
        service = self._authenticate(credentials_json)

        if service is None:
            return None

        message = MIMEText(message)
        message['to'] = to
        message['subject'] = subject
        message = urlsafe_b64encode(message.as_bytes()).decode()
        body = {'raw': message}

        try:
            message = service.users().messages().send(userId='me', body=body).execute()
            return message
        except HttpError as error:
            print(f'An error occurred: {error}')


    # Private Methods

    def _authenticate(self, credentials_json):
        # take credentials from google oauth2 and create a service object
        creds = Credentials.from_authorized_user_info(credentials_json)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                print('Credentials are invalid or missing')
                return None
    
        
        service = build('gmail', 'v1', credentials=creds)
        return service