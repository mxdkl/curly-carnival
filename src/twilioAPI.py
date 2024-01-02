import os
from dotenv import load_dotenv
from twilio.rest import Client


class TwilioApiWrapper:
    def __init__(self):
        load_dotenv()
        self.twilio_client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
        self.twilio_number = os.getenv('TWILIO_NUMBER')
        self.chat_history = []

    def sendMessage(self, to_number, body_text):
        try:
            message = self.twilio_client.messages.create(
                from_=f"whatsapp:{self.twilio_number}",
                body=body_text,
                to=f"whatsapp:{to_number}"
                )
            print(f"Message sent to {to_number}: {message.body}")
        except Exception as e:
            print(f"Error sending message to {to_number}: {e}")