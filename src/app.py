import os
from dotenv import load_dotenv
from assistant import Assistant
from flask import Flask, render_template, request
# from twilioAPI import TwilioApiWrapper

app = Flask(__name__, template_folder='../site/templates/', static_folder='../site/static/')


load_dotenv()
id = os.getenv("ASSISTANT_ID")
# t = TwilioApiWrapper()
eve = Assistant(id)

@app.route('/webhook', methods=['POST'])
def reply_whatsapp():
    form_data = request.form
    if form_data:
        sender_name = form_data['ProfileName']
        sender_number = form_data['From'].split(':')[1]
        message = form_data['Body']
        eve.processNewMessage(sender_number, message)
        # t.sendMessage(sender_number, message)


# Website things
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def login():
    return render_template('register.html')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404