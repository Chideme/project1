import csv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
#set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))



rows = 0
with open('books.csv') as csv_reader: #open books.csv
    next(csv_reader)# skip first line
    books = csv.reader(csv_reader) 
    for book in books:
        isbn = book[0]
        title = book[1]
        author =book[2]
        year= book[3]
        db.execute("INSERT INTO books (isbn,title,author,year) VALUES (:isbn, :title, :author, :year)",{"isbn":isbn, "title":title, "author":author, "year":year})
        db.commit()
        print("Inserted {}".format(title,))
        rows += rows
print("Inserted {} rows into books".format(rows))