from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.orm import backref
from werkzeug.security import generate_password_hash, check_password_hash

import os

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


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'GET': # New diary button from home.html
        return render_template('new.html') 
    else: # add another past entry to Post table
        image = request.files['image']

        new_post = Post(title=request.form['title'],
                        content=request.form['content'])

@app.route('/post/<int:id>')
def post(id):
    try:
        post = Post.query.filter_by(id=id).first()
        user = User.query.filter_by(id=post.user_id).first()
    except:
        pass
    else:
        user_path = 'static/' + user.img_path
        return render_template('post.html', post=post, user=user, files=[file for file in os.listdir(user_path)])

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if request.method == 'GET': # Edit already loaded diary
        try:
            post = Post.query.filter_by(id=id).first()
            user = User.query.filter_by(id=post.user_id).first()
        except:
            pass
        else:
            user_path = 'static/' + user.img_path
            return render_template('edit.html', post=post, user=user, files=[file for file in os.listdir(user_path)])
    else: # update post entry after edit task
        pass

@app.route('/delete/<int:id>')
def delete(id):
    pass

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    else:
        email = request.form['email']
        password = request.form['password']

        try:
            data = User.query.filter_by(email=email).first()
        except:
            pass
        else:
            if data is None:
                pass
            elif data.check_password(password):
                session['logged_in'] = data.id #logged_in user's id
                return render_template('home.html', 
                                        username=data.username, 
                                        posts=Post.query.filter_by(user_id=data.id).all())
            else:
                pass


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')

    else:
        new_user = User(username=request.form['username'],
                        email=request.form['email'],
                        password=request.form['password'])

        try:
            db.session.add(new_user)
            db.session.commit()
        except:
            return "You are already our member~"
        else:
            if not os.path.exists(new_user.img_path):
                os.makedirs('static/' + new_user.img_path)

            return render_template('login.html')

@app.route('/logout')
def logout():
    session['logged_in'] = None
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.secret_key = '123123123'
    app.run(debug=True)