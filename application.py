import os, json, requests

from flask import Flask, session, render_template, url_for, request, redirect, session, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_bcrypt import Bcrypt
from flask_jsonpify import jsonify

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
            # flash('Log In successfull')
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
        exist = db.execute("SELECT * FROM users WHERE email = :email OR username = :username",
                                {"email": email, "username": username}).fetchone()
        if exist:
            return render_template("index.html", info=f"{email} or {username} already exists.")

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
        # flash('You were registered successfully')

        return redirect(url_for("login"))

    else:
        return render_template("index.html")

@app.route("/home", methods=["GET", "POST"])
def home():
    """ Handles searching of books in database """
    # Check if user is logged in
    if 'loggedin' in session:
        if request.method == "POST":
            query = request.form.get("query")
            # raw sql to retrieve all books that match the {query} provided by user
            data = db.execute("SELECT isbn, title, author, year \
                                FROM books WHERE isbn iLIKE :query OR title iLIKE :query \
                                    OR author iLIKE :query LIMIT 10", {'query': f'%{query}%'}).fetchall()
            # create an empty dictionary to hold all retrived books details
            session["books"] = []
            # loop the retrieved books and store a books details as values set to respective dict key names
            for row in data:
                book = dict()
                book["isbn"] = row[0]
                book["title"] = row[1]
                book["author"] = row[2]
                book["year"] = row[3]
                session["books"].append(book)
            return render_template("homepage.html", username=session['username'], query=query, books=session["books"])
        return render_template("homepage.html", username=session['username'])
    # If user is not logged in redirect to login page
    return redirect(url_for('login'))

@app.route("/book/<isbn>", methods=["GET", "POST"])
def book(isbn):
    """Return details about a single book"""
    # Check if user is logged in
    if 'loggedin' in session:
        """ Fetch GoodReads reviews """
        # get goodreads api key enviroment variable
        api_key = os.getenv("GOODREADS_API_KEY")
        # Query goodreads api with  api key and books ISBN as parameters
        api_query = requests.get("https://www.goodreads.com/book/review_counts.json",
            params={"key": api_key, "isbns": isbn})
        if api_query.status_code != 200:
            return render_template("book.html", warning="404 Error")
        # convert to json format
        response = api_query.json()
        rating = response['books'][0]['average_rating']
        ratings = response['books'][0]['work_ratings_count']
        # fetch book using isbn and parse details to page
        book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
        # fetch all reviews in database
        reviews = db.execute("SELECT * FROM reviews WHERE book_id = :isbn", {"isbn": isbn}).fetchall()
        if request.method == "POST":
            # fetch form data
            review = request.form.get("review")
            ratings = request.form.get("ratings")
            user = session['username']
            # fetch book using isbn and parse details to page
            # check if user's review already exists
            if db.execute("SELECT * FROM reviews WHERE user_id = :username AND book_id = :isbn", {"username": user, "isbn": isbn}).rowcount > 0:
                    return render_template("book.html", username=session['username'], reviews=reviews, book=book, message="You have already posted a Review.", isbn=isbn, rating=rating, ratings=ratings)
            else:
                db.execute("INSERT INTO reviews (user_id, book_id, review, rating) VALUES (:user_id, :book_id, :review, :ratings)", {"user_id": user, "book_id": isbn, "review": review, "ratings": ratings})
                db.commit()
                return render_template('book.html', username=session['username'], reviews=reviews, book=book, info="Review successfully added", rating=rating, ratings=ratings)
        else:
            return render_template('book.html', username=session['username'], reviews=reviews, book=book, rating=rating, ratings=ratings)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route("/api/<isbn>", methods=["GET"])
def api(isbn):
    # fetch book details in books table using isbn and parse details to page
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    # fetch all reviews in database
    reviews = db.execute("SELECT COUNT(user_id), AVG(rating) FROM reviews WHERE book_id = :isbn", {"isbn": isbn}).fetchone()
    # check if result from db query is empty and catch error
    if book is None:
        return jsonify({"error":"Something went wrong"}), 404
    if reviews is None:
        return jsonify({"error":"Something went wrong"}), 404
    # store book details in a dictionary called response
    resp = {}
    resp['title'] = book.title
    resp['author'] = book.author
    resp['year'] = book.year
    resp['isbn'] = book.isbn
    resp['review_count'] = str(reviews[0])
    resp['average_score'] = float(reviews[1])
    # convert response dictionary to api readable json format
    return jsonify(resp), 200

@app.route('/logout')
def logout():
    """ Handles logging out of users """
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # flash('Log Out successfull')
    # Redirect to login page
    return redirect(url_for('login'))