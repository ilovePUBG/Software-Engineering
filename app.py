from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from werkzeug.datastructures import RequestCacheControl

app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///members.db'

#initialize the database
db = SQLAlchemy(app)

#create database table
class Members(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Name %r>' % self.id


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        resp = Members.query.filter((Members.email == email)).all()

        if len(resp) == 0:
            new_member = Members(email=email, password=password)

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
        #     resp = Members.query.filter((Members.email == email) and (Members.password == password))
        # except:
        #     return "no matched account"

    members_list = Members.query.order_by(Members.date_created)
    return render_template('main.html', members_list=members_list)

@app.route('/diary')
def diary():
    return render_template('diary.html')

if __name__ == '__main__':
    app.run(debug=True)