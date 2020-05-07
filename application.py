import os

from flask import Flask, session, render_template, url_for, request, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask.ext.bcrypt import Bcrypt

app = Flask(__name__, template_folder="template")
bcrypt = Bcrypt(app)

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
    return render_template("index.html");

@app.route("/")
def login():
    return render_template("home.html");

@app.route("/register", methods=["GET", "POST"])
def register():
    """ Handles registration of users """
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirmPassword")

        # Check if email already exists
        exist = db.execute("SELECT * FROM users WHERE email = :email",
                                {"email": email}).fetchone()
        if exist:
            return render_template("index.html", message="Email already exists. Please Sign In")

        # Check if password and confirm password  match
        elif password != confirm_password:
            return render_template("index.html", message="Passwords do not match.")

        # Hash the password so plaintext version isn't saved.
        pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        # Insert new user to the database
        db.execute("INSERT INTO users (email, username, password) VALUES (:email, :username, :password)",
                    {"email": email, "username": username, "password": pw_hash})

        # Commit change to users database
        db.commit()

        return redirect(url_for("login"))

    else:
        return render_template("index.html")

@app.route("/home")
def home():
    return render_template("homepage.html")

@app.route("/book")
def book():
    return render_template("book.html")