# This is a sample Python script.
# import fileinput

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from flask import Flask, flash, redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
import json
import os
import math

# from dotenv import load_dotenv


local_server = True
with open('config.json', 'r') as c:
    params = json.load(c)["params"]

# load_dotenv()
app = Flask(__name__)
app.secret_key = "Kumar@FLASK"
app.config['UPLOAD_FOLDER'] = params['upload_location']

if (local_server):
    app.config["SQLALCHEMY_DATABASE_URI"] = params['Local_url']
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = params['prod_url']

db = SQLAlchemy(app)


class Contact(db.Model):
    '''srno name email phone msg date'''
    srno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(12), nullable=False)
    mes = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=False)


class posts(db.Model):
    '''srno name email phone msg date'''
    srno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), unique=False, nullable=False)
    subtitle = db.Column(db.String(30), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    img_file = db.Column(db.String(12), nullable=False)
    date = db.Column(db.String(12), nullable=False)


@app.route("/")
def home():
    post = posts.query.filter_by().all()
    last = math.ceil(len(post)/int(params['no_of_post']))

    page = request.args.get('page')

    if(not str(page).isnumeric()):
        page = 1
    page = int(page)
    post = post[(page-1)*int(params['no_of_post']):(page-1)*int(params['no_of_post'])+int(params['no_of_post'])]
    #pagination logic
    #first
    if(page==1):
        prev = "#"
        next = "/?page="+str(page+1)
    elif(page==last):
        prev = "/?page=" + str(page - 1)
        next = "#"
    else:
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)

    # post = posts.query.filter_by().all()[0:int(params['no_of_post'])]
    return render_template('index.html', posts=post, prev=prev, next=next)


@app.route("/post/<string:post_slug>", methods=['GET'])
def POST(post_slug):
    post = posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, posts=post, )


@app.route("/about")
def about():
    return render_template('about.html', params=params)


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if 'user' in session and session['user'] == params['admin_user']:
        return render_template('dashboard.html')
    # return render_template('login.html', params=params)

    if request.method == 'POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if username == params['admin_user'] and userpass == params['admin_pass']:
            session['user'] = username
            post = posts.query.all()
            # print(post)
            return render_template('dashboard.html', params=params, posts=post)
    return render_template('login.html', params=params)


@app.route("/edit/<string:srno>", methods=['GET', 'POST'])
def edit(srno):
    if ('user' in session and session['user'] == params['admin_user']):
        if request.method == 'POST':
            box_title = request.form.get('Title')
            tline = request.form.get('Subtitle')
            slug = request.form.get('Slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            date = datetime.now()

            if srno == '0':
                post = posts(title=box_title, subtitle=tline, slug=slug, content=content, img_file=img_file, date=date)
                db.session.add(post)
                db.session.commit()
            else:
                post = posts.query.filter_by(srno=srno).first()
                post.title = box_title
                post.subtitle = tline
                post.slug = slug
                post.content = content
                post.img_file = img_file
                post.date = date
                db.session.commit()
                return redirect('/edit/' + srno)
        post = posts.query.filter_by(srno=srno).first()
        return render_template('edit.html', params=params, post=post, srno=srno)


@app.route("/uploader", methods=['GET', 'POST'])
def uploader():
    if ('user' in session and session['user'] == params['admin_user']):
        if (request.method == 'POST'):
            f = request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            return "uploaded successfully"


@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')


@app.route("/delete/<string:srno>")
def delete(srno):
    if ('user' in session and session['user'] == params['admin_user']):
        post = posts.query.filter_by(srno=srno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        '''add entry to database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        mes = request.form.get('message')
        '''srno name email phone msg date'''
        entry = Contact(name=name, email=email, phone=phone, mes=mes, date=datetime.now())
        db.session.add(entry)
        db.session.commit()
        flash('Form submitted successfully!')
        return redirect('/contact')
    return render_template('contact.html')


app.run(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
