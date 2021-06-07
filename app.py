from typing import Type
from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.orm import backref
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

import os
import shutil

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'this is secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# initialize the database
db = SQLAlchemy(app)

# create user table
class User(db.Model):
    __table_name__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    img_path = db.Column(db.String(100), unique=True, nullable=False) # directory path to posted images
    posts = db.relationship('Post', backref='author', lazy=True)

    def __init__(self, username, email, password, **kwargs):
        self.username = username
        self.email = email
        self.set_password(password)
        self.img_path = 'image/' + self.username + '/'

    def __repr__(self):
        return f"<User('{self.id}', '{self.username}', '{self.email}', '{self.img_path}')>"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

# create post table
class Post(db.Model):
    __table_name__ = 'post'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True, nullable=False)
    content = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"<Post('{self.id}', '{self.title}')>"


@app.route('/')
def index():
    return redirect('/login')

@app.route('/home')
def home():
    user = User.query.filter_by(id=session['logged_in']).first()
    posts = Post.query.filter_by(user_id=session['logged_in']).all()

    return render_template('home.html', user=user, posts=posts)

@app.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'GET': # New diary button from home.html
        return render_template('new.html') 
    else: # add another post entry to Post table
        new_post = Post(title=request.form['title'],
                        content=request.form['content'],
                        user_id=session['logged_in'])

        db.session.add(new_post)
        db.session.commit()

        user = User.query.filter_by(id=new_post.user_id).first()
        post_dir = 'static/' + user.img_path + str(new_post.id) + '/'

        if not os.path.exists(post_dir):
            os.makedirs(post_dir)

        for img in request.files.getlist('image'):
            if img.filename != '':
                img.save(post_dir + secure_filename(img.filename))

        return redirect(url_for('home'))

@app.route('/post/<int:id>')
def post(id):
    try: 
        post = Post.query.filter_by(id=id).first()
        user = User.query.filter_by(id=post.user_id).first()
    except:
        pass
    else:
        path = user.img_path + str(id) + '/'
        return render_template('post.html', path=path, 
                                            post=post, 
                                            files=[file for file in os.listdir('static/' + path)])

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if request.method == 'GET': # Edit already loaded diary
        try:
            post = Post.query.filter_by(id=id).first()
            user = User.query.filter_by(id=post.user_id).first()
        except:
            pass
        else:
            path = user.img_path + str(id) + '/'
            return render_template('edit.html', path=path, 
                                                post=post, 
                                                files=[file for file in os.listdir('static/' + path)])

    else: # update post entry after edit task
        post_to_update = Post.query.filter_by(id=id).first()
        user = User.query.filter_by(id=session['logged_in']).first()

        post_to_update.title = request.form['title']
        post_to_update.content = request.form['content']
        post_to_update.user_id = session['logged_in']
        db.session.commit()

        post_dir = 'static/' + user.img_path + str(id) + '/'

        for img in request.files.getlist('image'):
            if img.filename != '':
                img.save(post_dir + secure_filename(img.filename))

        return redirect(url_for('home'))

@app.route('/delete/<int:id>')
def delete(id):
    post = Post.query.filter_by(id=id).first()
    user = User.query.filter_by(id=session['logged_in']).first()

    shutil.rmtree('static/' + user.img_path + str(post.id))

    db.session.delete(post)
    db.session.commit()

    posts = Post.query.filter_by(user_id=session['logged_in']).all()

    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if session['logged_in'] != None:
            return redirect(request.referrer)
        else :
            return render_template('login.html')

    else:
        email = request.form['email']
        password = request.form['password']

        try:
            user = User.query.filter_by(email=email).first()
        except:
                pass
        else:
            if user is None:
                flash("Invalid email or password", category="alert alert-danger alert-dismissible fade show")
                return redirect('/login')
            elif user.check_password(password):
                session['logged_in'] = user.id #logged_in user's id
                return redirect('/home')
            else:
                pass


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        if session['logged_in'] != None:
            return redirect(request.referrer)
        else :
            return render_template('signup.html')

    else:
        new_user = User(username=request.form['username'],
                        email=request.form['email'],
                        password=request.form['password'])

        try:
            db.session.add(new_user)
            db.session.commit()
        except:
            flash("Username or email is duplicated. Try another one ~", category="alert alert-warning alert-dismissible fade show")
            return redirect('/signup')
        else:
            if not os.path.exists(new_user.img_path):
                os.makedirs('static/' + new_user.img_path)

            return redirect('/login')

@app.route('/logout')
def logout():
    session['logged_in'] = None
    return redirect('/')


if __name__ == '__main__':
    app.secret_key = '123123123'
    app.run(debug=True)