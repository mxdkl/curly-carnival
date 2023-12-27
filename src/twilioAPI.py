import os
from dotenv import load_dotenv
from twilio.rest import Client

class TwilioApiWrapper:
    def __init__(self):
        load_dotenv()
        self.client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
        self.twilio_number = os.getenv('TWILIO_NUMBER')
        self.chat_history = []

def send_message(self, to_number, body_text):
    try:
        message = self.client.messages.create(
            from_=f"whatsapp:{self.twilio_number}",
            body=body_text,
            to=f"whatsapp:{to_number}"
            )
        print(f"Message sent to {to_number}: {message.body}")
    except Exception as e:
        print(f"Error sending message to {to_number}: {e}")

def webhook_handler(request):
    # This function is triggered by an HTTP request to the endpoint

    if request.method == 'POST':
        if request.path == '/message':
            # Access form data
            form_data = request.form
            print(form_data)

            if form_data:
                # Process each form field
                Income_message = f"{form_data['ProfileName']}: {form_data['Body']}"
                reply_message = get_reply(Income_message)
                whatsapp_number = form_data['From'].split("whatsapp:")[-1]
                send_message(whatsapp_number, reply_message)
            return 'Form processed', 200
        else:
            # Handle invalid or missing data
            return 'Invalid request', 400
    else:
        # If not a POST request, indicate the method is not allowed
        return 'Method not allowed', 405