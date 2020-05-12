import os

from flask import Flask, session, render_template, url_for, request, redirect, session, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_bcrypt import Bcrypt

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
    """ Index page """
    return render_template("index.html");

@app.route("/login", methods=["GET", "POST"])
def login():
    """ Handles signing in of users """
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # check if username exists in database
        data = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
        if data is None:
            return render_template("index.html", message="Invalid username.")

        # Check if hashed password matches one in database
        if bcrypt.check_password_hash(data.password.encode('utf-8'), password.encode('utf-8')):
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session["id"] = data['id']
            session["username"] = data['username']
            flash('Log In successfull')
            return redirect(url_for("home"))

        else:
            return render_template("index.html", message="Invalid password")

    else:
        return render_template("index.html", message="Please Sign In")

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
            return render_template("index.html", info="Email already exists.")

        # Check if password and confirm password  match
        elif password != confirm_password:
            return render_template("index.html", info="Passwords do not match.")

        # Hash the password so plaintext version isn't saved.
        pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        # Insert new user to the database
        db.execute("INSERT INTO users (email, username, password) VALUES (:email, :username, :password)",
                    {"email": email, "username": username, "password": pw_hash})

        # Commit change to users database
        db.commit()
        flash('You were registered successfully')

        return redirect(url_for("login"))

    else:
        return render_template("index.html")

@app.route("/home")
def home():
    # Check if user is logged in
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('homepage.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route("/book")
def book():
    # Check if user is logged in
    if 'loggedin' in session:
        # User is loggedin show them the book page
        return render_template('book.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    """ Handles logging out of users """
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    flash('Log Out successfull')
    # Redirect to login page
    return redirect(url_for('login'))