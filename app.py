from flask import Flask, render_template, request

app = Flask(__name__, static_url_path='/static')

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/main', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        # check whther input id and password is valid w/ database
        return render_template('main.html')

@app.route('/diary')
def diary():
    return render_template('diary.html')

if __name__ == '__main__':
    app.run(debug=True)