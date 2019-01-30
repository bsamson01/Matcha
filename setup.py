from flask import Flask, flash, session, redirect, url_for, escape, request, render_template, jsonify
import subprocess
import os
from flask_sqlalchemy import SQLAlchemy
from bottle import route, run
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
import string
import random
import socket
import json
import IP2Location
import requests
import re

app = Flask(__name__, static_folder='static')
app.secret_key = 'any random string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'matchaapp6@gmail.com'
app.config['MAIL_PASSWORD'] = 'brandon912680'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail=Mail(app)
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

class users(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    firstname = db.Column(db.String, nullable=False)
    lastname = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    confirmed = db.Column(db.Boolean, default=False)
    confirm_key = db.Column(db.String, nullable=False)
    prof_created = db.Column(db.Boolean, default=False)
    

    def __init__(self, fname, lname, usrname, email, password, key):
        self.firstname = fname
        self.lastname = lname
        self.username = usrname
        self.email = email
        self.password = bcrypt.generate_password_hash(password)
        self.confirm_key = key

class userprofiles(db.Model):
    __tablename__ = 'userprofiles'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    firstname = db.Column(db.String, nullable=False)
    lastname = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String, nullable=False)
    active = db.Column(db.Boolean, default=False)
    img1 = db.Column(db.Text)
    img2 = db.Column(db.Text)
    img3 = db.Column(db.Text)
    img4 = db.Column(db.Text)
    img4 = db.Column(db.Text)
    profile_pic = db.Column(db.Text)
    address = db.Column(db.String)
    city = db.Column(db.String)
    country = db.Column(db.String)
    lastseen = db.Column(db.String)
    famerating = db.Column(db.Integer, default=0)
    visitors = db.Column(db.String)
    new_visitors = db.Column(db.String)
    num_likes = db.Column(db.Integer, default=0)
    num_liked = db.Column(db.Integer, default=0)
    likes = db.Column(db.String)
    new_likes = db.Column(db.String)
    liked = db.Column(db.String)
    blocked = db.Column(db.String)
    blocks = db.Column(db.String)
    new_blockes = db.Column(db.String)
    chats = db.Column(db.String)
    chatable = db.Column(db.String)
    new_chats = db.Column(db.String)
    updatedip = db.Column(db.String)

    def __init__(self, mid, usrname, fname, lname, mail, age, gender, address, city, country, updatedip):
        self.user_id = mid
        self.username = usrname
        self.firstname = fname
        self.lastname = lname
        self.email = mail
        self.age = age
        self.gender = gender
        self.address = address
        self.city = city
        self.country = country
        self.updatedip = updatedip


@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('home'))
    return render_template('index.html')

@app.route('/logout')
def logout():
    s = users.query.filter_by(username=session['username']).first()
    if s.prof_created is True:
        userprofiles.query.filter_by(user_id=s.id).update(dict(active=False))
        db.session.commit()
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/create_profile', methods=['GET', 'POST'])
def create_profile():
    if request.method == "POST":
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        # send_url = "http://api.ipstack.com/"+ip+"?access_key=24c6e9555a9d7c36a057b4cd815df530"
        # geo_req = requests.get(send_url)
        # geo_json = json.loads(geo_req.text)
        user = users.query.filter_by(username=session['username']).first()
        user_add = userprofiles(user.id, session['username'], user.firstname, user.lastname, user.email, request.form['age'], request.form['gender'], request.form['address'], request.form['city'], request.form['country'], ip)
        users.query.filter_by(username=session['username']).update(dict(prof_created=True))
        db.session.add(user_add)
        db.session.commit()
        flash('User details successfully updated', 'success')
        s = users.query.filter_by(username=session['username']).first()
        userprofiles.query.filter_by(user_id=s.id).update(dict(active=True))
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create_profile.html')

@app.route('/profile_pic', methods=['GET', 'POST'])
def profile_pic():
    if request.method == "POST":
        s = users.query.filter_by(username=session['username']).first()
        userprofiles.query.filter_by(user_id=s.id).update(dict(profile_pic=request.form['profile_picture']))
        db.session.commit()
        flash('Profile picture successfully addedd', 'success')
    return render_template('home')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        if request.method == "POST":
            POST_USERNAME = str(request.form['username'])
            POST_EMAIL = str(request.form['email'])
            POST_PASSWORD = str(request.form['password'])
            res = users.query.filter_by(username=POST_USERNAME, email=POST_EMAIL).first()
            if res:
                ny = users.query.filter_by(username=POST_USERNAME, confirmed=True).first()
                if ny:
                    if bcrypt.check_password_hash(res.password, POST_PASSWORD):
                        session['username'] = POST_USERNAME
                        flash('User ' + res.username + ' successfully logged in', 'success')
                        s = users.query.filter_by(username=session['username']).first()
                        if s.prof_created is True:
                            userprofiles.query.filter_by(user_id=s.id).update(dict(active=True))
                            db.session.commit()
                        return redirect(url_for('index'))
                    else:
                        flash('Incorrect Password', 'danger')
                else:
                    flash('Account not verified', 'warning')
            else:
                flash('Username or Email not found', 'danger')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        POST_USERNAME = str(request.form['username'])
        POST_EMAIL = str(request.form['email'])
        query1 = users.query.filter_by(username=POST_USERNAME).first()
        query2 = users.query.filter_by(username=POST_USERNAME).first()
        if query1:
            flash('Username already exists', 'danger')
        if query2:
            flash('Email already exists', 'danger')
        elif not query1 and not query2:
            rnd = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(20))
            user = users(request.form['firstname'], request.form['lastname'], request.form['username'], request.form['email'], request.form['password'], rnd)
            db.session.add(user)
            db.session.commit()
            msg = Message('Matcha_ Registration', sender = 'matchaapp6@gmail.com', recipients = [POST_EMAIL])
            msg.body = "Your verification link is  http://matcha-flask.herokuapp.com/verify/" + rnd + "/" + request.form['username']
            mail.send(msg)
            flash('User '+ request.form['firstname'] +' '+request.form['lastname'] +' successfully added. Check your email for verification', 'success')
            return redirect(url_for('index'))
    return render_template('signup.html')

@app.route('/verify/<string:code>/<string:user>', methods=['GET', 'POST'])
def verify(code=None,user=None):
    qry = users.query.filter_by(username=user, confirm_key=code).first()
    if qry:
        if users.query.filter_by(username=user,confirmed=False).first():
            users.query.filter_by(username=user).update(dict(confirmed=True))
            db.session.commit()
            flash('Account successfully verified.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Account already verified', 'warning')
    else:
        flash('Verification link is invalid userid='+user+' code='+code, 'danger')
    return redirect(url_for('index'))

@app.route('/updatebtn')
def updatebtn():
    usr = users.query.filter_by(username=session['username']).first()
    usr2 = userprofiles.query.filter_by(user_id=usr.id).first()
    return render_template('update_profile.html', username=usr.username, firstname=usr.firstname, lastname=usr.lastname, email=usr.email, age=usr2.age, address=usr2.address, city=usr2.city, country=usr2.country)

@app.route('/updatebasic', methods=['GET', 'POST'])
def updatebasic():
    if request.method == "POST":
        rnd = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(20))
        s = users.query.filter_by(username=session['username']).first()
        m = s.id
        if request.form['username'] != session['username'] and users.query.filter_by(username=request.form['username']).first():
            flash('Username already exists', 'danger')
        else:
            users.query.filter_by(id=m).update(dict(username=request.form['username']))
            db.session.commit()
        if request.form['email'] != s.email and users.query.filter_by(email=request.form['email']):
            flash('Email already exists', 'danger')
        else:
            users.query.filter_by(id=m).update(dict(email=request.form['email']))
            userprofiles.query.filter_by(user_id=m).update(dict(email=request.form['email']))
            db.session.commit()
        #firstname
        users.query.filter_by(id=m).update(dict(firstname=request.form['firstname']))
        userprofiles.query.filter_by(user_id=m).update(dict(firstname=request.form['firstname']))
        db.session.commit()
        #lastname
        users.query.filter_by(id=m).update(dict(lastname=request.form['lastname']))
        userprofiles.query.filter_by(user_id=m).update(dict(lastname=request.form['lastname']))
        db.session.commit()
        users.query.filter_by(id=m).update(dict(confirmed=False))
        users.query.filter_by(id=m).update(dict(confirm_key=rnd))
        db.session.commit()
        s = users.query.filter_by(id=m).first()
        msg = Message('Matcha_ Registration', sender = 'matchaapp6@gmail.com', recipients = [s.email])
        msg.body = "Your verification link is  http://matcha-flask.herokuapp.com/verify/" + rnd + "/" + s.username
        mail.send(msg)
        flash('Account updated. Confimation link sent to your email', 'success')
        return redirect(url_for('logout'))
    return render_template('update_profile.html')

@app.route('/view_profile/<int:userid>', methods=['GET', 'POST'])
def view_profile(userid=None):
    like = False
    liked = False
    block = False
    blocked = False

    query1 = users.query.filter_by(id=userid).first()
    query2 = userprofiles.query.filter_by(user_id=query1.id).first()
    query3 = users.query.filter_by(username=session['username']).first()
    query4 = userprofiles.query.filter_by(user_id=query3.id).first()

    if query4.liked:
        arr = query4.liked.split(',')
        if str(query1.id) in arr:
            liked = True
    if query4.likes:
        arr = query4.likes.split(',')
        if str(query1.id) in arr:
            like = True
    if query4.blocked:
        arr = query4.blocked.split(',')
        if str(query1.id) in arr:
            blocked = True
    if query4.blocks:
        arr = query4.blocks.split(',')
        if str(query1.id) in arr:
            block = True
    thats_me = False
    if query3.id == userid:
        thats_me = True
    return render_template('view_profile.html', me=thats_me, user=query1.username, firstname=query1.firstname, lastname=query1.lastname, gender=query2.gender, address=query2.address, city=query2.city, country=query2.country, likes_me=like, like_them=liked)
        

@app.route('/loginbtn')
def loginbtn():
    if 'username' in session:
        flash('User ' + session['username'] + ' currently logged in', 'warning')
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/signupbtn', methods=['GET', 'POST'])
def signupbtn():
    if 'username' in session:
        flash('User ' + session['username'] + ' currently logged in', 'warning')
        return redirect(url_for('index'))
    return render_template('signup.html')

@app.route('/pictures')
def pictures():
    s = users.query.filter_by(username=session['username']).first()
    usr = userprofiles.query.filter_by(user_id=s.id).first()
    return render_template('pictures.html', user=usr)

@app.route('/home')
def home():
    if 'username' in session:
        s = users.query.filter_by(username=session['username']).first()
        if s.prof_created is False:
            flash('Please update user profile', 'warning')
            return redirect(url_for('create_profile'))
        return render_template('home.html', usrs=userprofiles.query.all(), usr=session['username'])
    else:
        flash('You must login first', 'warning')
        return redirect(url_for('index'))

if __name__ == '__main__':
    db.create_all()
    # Get required port, default to 5000.
    port = os.environ.get('PORT', 5000)
    # Run the app.
    app.run(host='0.0.0.0', port=port,debug=True)
