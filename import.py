import csv

with open('books.csv') as csv_reader:
    books = csv.reader(csv_reader) 
    