# Internal libraries
import os
import requests
from pip._vendor import cachecontrol

# Custom libraries
from assistant import Assistant

# External libraries
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, abort
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2 import id_token
import google.auth.transport.requests


app = Flask(__name__, template_folder="../site/templates/", static_folder="../site/static/")

load_dotenv()
id = os.getenv("ASSISTANT_ID")
eve = Assistant(id)


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
        eve.processNewMessage(sender_number, message)


# -----------------------------------------
# Static Website
# -----------------------------------------
        
@app.route('/', methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET"])
def register():
    return render_template("register.html")

@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


# -----------------------------------------
# Goole login / Oauth
# -----------------------------------------

app.secret_key = os.getenv("CLIENT_SECRET")

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1" # to allow Http traffic for local dev

# Configure OAuth
flow = InstalledAppFlow.from_client_secrets_file(
    "client_secret.json",
    scopes=["https://www.googleapis.com/auth/gmail.modify", "https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://localhost:5000/login/callback"
)

@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route("/login/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=os.environ["CLIENT_ID"]
    )

    name = id_info.get("name")
    email = id_info.get("email")
    eve.register(name=name, email=email, GmailToken=credentials.to_json())

    return redirect('/')

@app.route("/logout")
def logout():
    session.clear()
    return redirect('/')