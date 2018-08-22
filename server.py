import os
import json
import requests
import urllib
import hashlib
import base64

from flask import Flask, render_template, session, request, abort
from flask import redirect, escape, Response, flash
from flask import jsonify

from flask_login import LoginManager, UserMixin, login_required, login_user
from flask_login import logout_user, current_user

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
login_manager.login_view = "/user"


def base64encode(s):
    return (base64.b64encode(str.encode(s))).decode("utf-8").replace("=", "")


def base64decode(s):
    while len(s) % 3 != 2:
        s += "="
    return base64.b64decode(str.encode(s)).decode("utf-8")


def encPass(p):
    hash = hashlib.sha512()
    hash.update(('%s' % p).encode('utf-8'))
    return hash.hexdigest()


class User(UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    if email is None or email == "":
        return
    # cursor.execute("insert into people values (?, ?)", (who, age))
    c = db.query_db("select * from zx_users where email =(?)", ([email]))
    if not len(c) == 1:
        return
    user = User()
    user.id = c[0][1]    # email
    user.role = c[0][3]  # role
    return user
#
#
# @login_manager.request_loader
# def request_loader(request):
#     email = request.form.get('email')
#     if email is None or email == "":
#         return
#     quary = "select * from zx_users where email ='" + email + "'"
#     print(quary)
#     c = db.query_db(quary)
#     print("request_loader")
#     for row in c:
#         print(row)
#     if email not in users:
#         return
#
#     user = User()
#     user.id = email
#
#     # DO NOT ever store passwords in plaintext and always compare password
#     # hashes using constant-time comparison!
#     user.is_authenticated = request.form['password'] == users[email]['password']
#
#     return user


@app.route("/")
@login_required
def main():
    return render_template('index.html')


@app.route("/domain", methods=["GET", "POST"])
@login_required
def domain():
    email = current_user.id
    c = db.query_db("select * from zx_users where email =(?)", ([email]))
    d = db.query_db("select * from domains where userid =(?)", ([c[0][0]]))

    if request.method == 'POST':
        domain = request.form['domain']
        notify_email = request.form['notify_email']
        q = "select 1 from domains where userid=(?) and domain=(?)"
        e = db.query_db(q, (c[0][0], domain))
        if len(e) >= 1:
            return jsonify({"error": "Duplicated domain"})
        db.query_db("insert into domains (userid,domain,notify_email) "
                    "values (?, ?, ?)",
                    (c[0][0], domain, notify_email))
        return jsonify({"error": ""})

    if len(d) == 0:
        return jsonify({})
    data = {}
    data['domains'] = []
    for row in d:
        data['domains'].append(row[1])
    return jsonify(data)


@app.route("/user", methods=['GET', 'POST'])
def user():
    if request.method == 'POST':
        email = request.form['email']
        c = db.query_db("select * from zx_users where email =(?)", ([email]))
        if len(c) == 1:
            h = encPass(request.form['password'])
            if h == c[0][2]:
                user = User()
                user.id = email
                login_user(user)
                return redirect('/')
        return render_template('user.html', notLoggedin='true',
                               error='Wrong email or password')
    elif request.method == 'GET':
        return render_template('user.html', notLoggedin='true')
    else:
        abort(400)


@app.route("/user/logout", methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect('/user')


@app.route("/user/management", methods=['GET', 'POST'])
@login_required
def management():
    if current_user.role != 'admin':
        return redirect('/')
    if request.method == 'POST':
        email = base64encode(request.form['email'])
        return render_template('userManagement.html',
                               invite=(email))
    return render_template('userManagement.html')


@app.route("/user/invite/<id>", methods=['GET', 'POST'])
def invite(id):
    email = base64decode(id)
    c = db.query_db("select * from zx_users where email =(?)", ([email]))
    if len(c) == 1:
        return render_template('user.html', error='Error.\n' +
                               'If you have an acount try to login\n' +
                               'If not ask for another invitaion link')
    if request.method == 'POST':
        password = request.form['password']
        db.query_db("insert into zx_users (EMAIL,PASSWORD,ROLE) "
                    "values (?, ?, ?)",
                    (email, encPass(password), 'user'))
        user = User()
        user.id = email
        login_user(user)
        return redirect('/')
    return render_template('newUser.html', email=email)


@app.teardown_appcontext
def close_connection(exception):
    db.close_connection
