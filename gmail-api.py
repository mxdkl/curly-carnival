from base64 import urlsafe_b64encode
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GmailWrapper:
    def __init__(self, credentials_file):
        self.credentials_file = credentials_file
        self.service = self._create_gmail_service()

    def _create_gmail_service(self):
        SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']
        creds = None

        if os.path.exists(self.credentials_file):
            creds = Credentials.from_authorized_user_file(self.credentials_file, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('creds.json', SCOPES)
                creds = flow.run_local_server(port=0)

            with open(self.credentials_file, 'w') as token:
                token.write(creds.to_json())

        return build('gmail', 'v1', credentials=creds)

    def send_email(self, to, subject, message_body):
        message = self._create_message(to, subject, message_body)
        try:
            self.service.users().messages().send(userId='me', body=message).execute()
            print("Email sent successfully.")
        except HttpError as e:
            print(f"An error occurred: {str(e)}")

    def _create_message(self, to, subject, message_body):
        from email.mime.text import MIMEText
        from base64 import urlsafe_b64encode

        message = MIMEText(message_body)
        message['to'] = to
        message['subject'] = subject

        raw_message = urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return {'raw': raw_message}

    def list_unread_emails(self):
        try:
            results = self.service.users().messages().list(userId='me', q='is:unread').execute()
            messages = results.get('messages', [])

            if not messages:
                print('No unread emails found.')
            else:
                for message in messages:
                    msg = self.service.users().messages().get(userId='me', id=message['id']).execute()
                    message_data = msg['payload']['headers']
                    sender, subject = None, None
                    for data in message_data:
                        if data['name'] == 'From':
                            sender = data['value']
                        if data['name'] == 'Subject':
                            subject = data['value']
                    if sender and subject:
                        print(f'From: {sender}\nSubject: {subject}\n')

        except HttpError as e:
            print(f"An error occurred: {str(e)}")

def main():
    credentials_file = 'token.json'
    gmail_wrapper = GmailWrapper(credentials_file)

    # Sending an email
    to = 'dingjee7@gmail.com'
    subject = 'Test Email'
    message_body = 'This is a test email sent from the Gmail API.'
    #gmail_wrapper.send_email(to, subject, message_body)

    # List unread emails
    gmail_wrapper.list_unread_emails()

if __name__ == '__main__':
    main()