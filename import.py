import os, csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Import books from books.csv file to the PostgreSQL Adminer books table database
def main():
    f = open("books.csv")
    # using delimeter to split the values by comma in books.csv to be added to database
    reader = csv.reader(f, delimiter=',')
    # This skips the first row of the CSV file.
    next(reader)

    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                        {"isbn": isbn, "title": title, "author": author, "year": year})
    print(f"Added book {title} by {author}, {year} to database.")

    db.commit()

if __name__ == "__main__":
    main()