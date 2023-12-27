from flask import Flask, render_template

app = Flask(__name__)
# app = Flask:

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def login():
    return render_template('register.html')


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404