import os

from flask import Flask, session, render_template, request
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

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")

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
    form_email = request.form.get("email")
    form_password = request.form.get("password")
    db_info = db.execute("SELECT * FROM users WHERE (email = :email) AND (password = :password)  VALUES (:email)",
            {"email": form_email, "password": form_password}).fetchone
    message = db_info
    return render_template("success.html", message=message)
