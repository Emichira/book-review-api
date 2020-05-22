# Project 1: Books

## Web Programming with Python and JavaScript

This is a book review web application. Users will be able to register and then log in using their username and password. Once they log in, they will be able to search for books, leave reviews for individual books, and see the reviews made by other people. Using a third-party API by Goodreads, another book review website, users will also be able to view ratings from a broader audience. Finally, users will be able to query for book details and book reviews programmatically via this website’s API through ISBN number.

## Getting Started
```
### Installing

$ git clone https://github.com/Emichira/book-review-api.git

# Navigate into working folder
$ cd project1

# Create and Activate virtual enviroment
$ pipenv shell

# Install all dependencies
$ pip install -r requirements.txt

# ENV Variables
$ export PATH = Your path to working project

$ export FLASK_APP = application.py

$ export FLASK_DEBUG = 1

$ export DATABASE_URL = Your Heroku Postgres DB URI

$ export GOODREADS_API_KEY = Your Goodreads Developer API Key# See: https://www.goodreads.com/api
```

## Usage
```
1. Register for an account
2. Login
3. Search for the book by its ISBN, author name, or title
4. Get individual book review information and write your own reviews
5. Logout

```

## Built With
```
* [Flask Python](https://flask.palletsprojects.com/en/1.1.x/) - The web framework used
* [SQL] - Raw SQL querying used
* [Good Reads API](https://www.goodreads.com/api) - Popular book review website, used to get access to their review data for individual books.
```
## Authors
```
* **Emmanuel Michira** - [Software Developer](https://emichira.github.io/Portfolio/)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.
```
## License
```
- **[MIT license](http://opensource.org/licenses/mit-license.php)**
- Copyright 2020 © <a href="https://emichira.github.io/Portfolio/" target="_blank">Emmanuel Michira</a>.

```