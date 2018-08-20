import os
import json
import requests
import urllib

from flask import Flask, render_template, session, request, abort
from flask import redirect, escape, Response
from flask_login import LoginManager, UserMixin, login_required

from modules import *

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_STATIC = os.path.join(APP_ROOT, 'static')

app = Flask(__name__,
            template_folder='template',
            static_url_path="/static",
            static_folder="static")

app.secret_key = '[PUT_HERE_LONG_AND_RANDOM_STRING___HOW_LONG_?___REALLY]'

login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin):
    # proxy for a database of users
    user_database = {"JohnDoe": ("JohnDoe", "John"),
                     "JaneDoe": ("JaneDoe", "Jane")}

    def __init__(self, username, password):
        self.id = username
        self.password = password

    @classmethod
    def get(cls, id):
        return cls.user_database.get(id)


@login_manager.request_loader
def load_user(request):
    token = request.headers.get('Authorization')
    if token is None:
        token = request.args.get('token')

    if token is not None:
        username, password = token.split(":")  # naive token
        user_entry = User.get(username)
        if (user_entry is not None):
            user = User(user_entry[0], user_entry[1])
            if (user.password == password):
                return user
    return None


@app.route("/")
def main():
    if 'loggedin' not in session:
        return redirect('/user')
    else:
        return render_template('index.html')


@app.route("/user", methods=['GET', 'POST'])
def user():
    if 'loggedin' in session:
        return redirect('/')
    if request.method == 'POST':
        # the login process
        return 'True', 200
    elif request.method == 'GET':
        return render_template('user.html', notLoggedin='true')
    else:
        abort(400)
