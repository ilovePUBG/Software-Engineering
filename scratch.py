from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.orm import backref
from werkzeug.security import generate_password_hash, check_password_hash

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
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def __init__(self, email, password, **kwargs):
        self.email = email
        self.set_password(password)

    def __repr__(self):
        return f"<User('{self.id}', '{self.email}')>"

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
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        resp = User.query.filter((User.email == email)).all()

        if len(resp) == 0:
            new_member = User(email=email, password=password)

            # pusht to db
            try:
                db.session.add(new_member)
                db.session.commit()
                return redirect('/login')
            except:
                return "There was an error"

        else:
            return "duplicated member info"
    else:
        return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/main', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        resp = None

        # try:
        #     resp = User.query.filter((User.email == email) and (User.password == password))
        # except:
        #     return "no matched account"

    members_list = User.query.order_by(User.date_created)
    return render_template('main.html', members_list=members_list)

@app.route('/diary')
def diary():
    return render_template('diary.html')

if __name__ == '__main__':
    app.run(debug=True)