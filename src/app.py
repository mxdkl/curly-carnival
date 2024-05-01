# Internal libraries
import os
import requests
import json
from pip._vendor import cachecontrol

# Custom libraries
from assistant import Assistant

# External libraries
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, abort
import jwt

# Google Oauth v2
from google.oauth2 import id_token
import google.oauth2.credentials
import google_auth_oauthlib.flow


# Create the Flask app
app = Flask(__name__, template_folder="../site/templates/",
            static_folder="../site/static/")

# Load the environment variables
load_dotenv()
URI = os.getenv("URI")
id = os.getenv("ASSISTANT_ID")
eve = Assistant(id=id)


# Routes

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
        return "OK"
    else:
        return "No form data found"


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

# uncomment to allow Http traffic, needed for gunicorn to work. its behind nginx so its fine
# to allow Http traffic for local dev
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

app.secret_key = "??89tnuv2v89tvu29084tun0298utnv0298ty2n?>W<@E<@:LE"

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid"
]


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "credentials" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        session['email'] = email
        return redirect('/mailbox')
    else:
        return render_template('app_login.html')


@app.route("/login/<token>")
def login_user(token):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        "client_secret.json",
        scopes=SCOPES,
        redirect_uri=URI + "/oauth2callback"
    )

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true"
    )
    session["state"] = state
    session["token"] = token
    return redirect(authorization_url)


@app.route("/oauth2callback")
def callback():
    state = session["state"]

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        "client_secret.json",
        scopes=SCOPES,
        redirect_uri=URI + "/oauth2callback"
    )
    flow.state = state

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials

    session["credentials"] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

    decoded_id_token = jwt.decode(credentials._id_token, algorithms=["ES256"], options={"verify_signature": False})
    email = decoded_id_token["email"]
    name = decoded_id_token["name"]

    eve.registerEmail(str(session["token"]), name, email, str(json.dumps(session["credentials"])))

    return redirect('/mailbox')


@app.route("/mailbox")
@login_is_required
def mailbox():
    return f"Hello {session}! <br/> <a href='/logout'><button>Logout</button></a>"


@app.route("/logout")
def logout():
    session.clear()
    return redirect('/login')
