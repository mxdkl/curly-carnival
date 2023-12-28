import os
from dotenv import load_dotenv
from assistant import Assistant
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)


load_dotenv()
id = os.getenv("ASSISTANT_ID")
eve = Assistant(id)

@app.route('/webhook')
def reply_whatsapp():
    form_data = request.form
    if form_data:
        sender_name = form_data['ProfileName']
        sender_number = form_data['From'.split(':')[1]]
        message = form_data['Body']
        eve.processNewMessage(sender_number, message)