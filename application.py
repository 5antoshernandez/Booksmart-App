import os

from flask import Flask, session, render_template, request, url_for, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
app.secret_key = b'2\xf8r.\x10\xc7\x0e0a\xec\xa9\x05\xdav\xde\xa4'

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    message = "You are not logged in."
    if 'email' in session:
        message = 'Hello %s' % session['name']
        return render_template("index.html", message=message)
    return render_template("index.html", message=message)

@app.route("/account-setup")
def account_setup():
    return render_template("register.html")

@app.route("/success", methods=["POST"])
def register():
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    try:
        db.execute("INSERT INTO users (name, email, password) VALUES (:name, :email, :password)",
                {"name": name, "email": email, "password": password})
        db.commit()
        message = "You have successfully registered your account. Yay!"
        return render_template("success.html", message=message)
    except:
        message = "Couldn't register account, account already exists."
        return render_template("error.html", message=message)

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/checklogin", methods=["POST"])
def checklogin():
    email = request.form.get("email")
    password = request.form.get("password")
    email_check = db.execute('''SELECT email FROM users WHERE (email = :email) ''',
            {"email": email}).fetchone()
    password_check = db.execute('''SELECT password FROM users WHERE (password = :password)''',
    {"password": password}).fetchone()
    get_name = db.execute("SELECT name FROM users WHERE (email = :email)", {"email": email}).fetchone()[0]
    try:
        if email == email_check[0] and password == password_check[0]:
            session['email'] = request.form['email']
            session['name'] = get_name
            message = f"Success!!!! {get_name}"
            return render_template("success.html", message=message)
    except:
        message = "You entered an incorrect username or password. Please reattempt to login"
        return render_template("login.html", message=message)

@app.route('/<email>/')
def show_user(email):
    render_template("success.html", "Hello.")

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('email', None)
    return redirect(url_for('index'))
