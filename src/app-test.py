# Internal libraries
import os
import requests
import json
from pip._vendor import cachecontrol
import uuid

# Custom libraries
# from assistant import Assistant

# External libraries
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, abort
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2 import id_token
import google.auth.transport.requests


app = Flask(__name__, template_folder="../site/templates/", static_folder="../site/static/")

load_dotenv()
id = os.getenv("ASSISTANT_ID")
# eve = Assistant(id=id)


# -----------------------------------------
# WhatApp
# -----------------------------------------

@app.route("/webhook", methods=["POST"])
def reply_whatsapp():
    form_data = request.form
    if form_data:
        sender_name = form_data["ProfileName"]
        sender_number = form_data["From"].split(":")[1]
        message = form_data["Body"]
        # eve.processNewMessage(sender_number, message)


# -----------------------------------------
# Static Website
# -----------------------------------------
        
@app.route('/', methods=["GET"])
def index():
    return render_template("index.html")

@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


# -----------------------------------------
# Goole login / Oauth
# -----------------------------------------

# uncomment to allow Http traffic, needed for gunicorn to work. its behind nginx so its fine
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1" # to allow Http traffic for local dev

app.secret_key = os.getenv("CLIENT_SECRET")

# Configure OAuth
flow = InstalledAppFlow.from_client_secrets_file(
    "D:\Projects\curly-carnival\curly-carnival\src\client_secret.json",
    scopes=["https://www.googleapis.com/auth/gmail.modify", "https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
    # redirect_uri="https://personacorps.com/login/callback"
)

def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "email" not in session:
            return abort(401)  # Authorization required
        else:
            return function()
    return wrapper

def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


@app.route('/login', methods=["GET", "POST"])
def login():
    # if request.method == "POST":
    #     email = request.form['email']
    #     session['email'] = email
    #     return redirect('/mailbox')
    
    return render_template('app_login.html')

@app.route("/login/<token>")
def login_user(token):
    if is_valid_uuid(token):
        authorization_url, state = flow.authorization_url()
        session["state"] = state
        session["token"] = token
        return render_template('app_login.html', authorization_url=authorization_url)
    else:
        return redirect('/login')

 
#   redirect(authorization_url)

@app.route("/login/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]: abort(500)

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=os.environ["CLIENT_ID"]
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["email"] = id_info.get("email")
    creds = json.dumps(credentials._id_token)
    # eve.registerEmail(session["token"], session["name"], session["email"], creds)

    return redirect('/mailbox')

@app.route("/mailbox")
# @login_is_required
def mailbox():
    return render_template('app_mailbox.html')

@app.route("/mailbox/<token>")
def draft(token):
    if is_valid_uuid(token):
        return render_template('app_draft.html', token=token)
    else:
        return abort(401)

@app.route("/logout")
def logout():
    session.clear()
    return redirect('/login')