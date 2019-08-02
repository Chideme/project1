import os
import requests

from flask import Flask, session, render_template,flash,request,redirect,url_for,jsonify
from flask_session import Session
from flask_json import FlaskJSON, JsonError, json_response, as_json
from sqlalchemy import create_engine,text
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required

app = Flask(__name__,template_folder = "templates")

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

#Goodreads API key
KEY = "bbZTsm9VLVD8f8BzWemGA"




@app.route("/",methods=["GET","POST"])
@login_required
def index():
    """ Index"""
    return render_template("index.html")

@app.route("/login",methods=["GET","POST"])
def login():
    """Log In User"""
    session.clear()

    #check login crenditials

    if request.method == "POST":

        if not request.form.get("username") or not request.form.get("password"):
            message = "Please Provide Username/Password"
            return render_template("error.html",message=message)
        # get user details
        else:
            username = request.form.get("username")
            password = request.form.get("password")

            # query to check if user is in database
            row = db.execute("SELECT user_id,username,hash FROM users WHERE username = :username",{"username":username}).fetchone()
            if username != row[1] or not check_password_hash(row[2],password):
                message = "Username/Password Not Correct !!"
                return render_template("error.html",message=message)
            else:
                session["user_id"] = row[0]
                return redirect(url_for('index'))
    else:
        return render_template("login.html")

@app.route("/register",methods = ["GET","POST"])
def register():
    """Register New User"""
    if request.method == "POST":
        # check if user has filled the forms
        if not request.form.get("username") or not request.form.get("password") or not request.form.get("password1"):
            message = "Please Provide Username/Password"
            return render_template("error.html",message=message)
        else:
            username = request.form.get("username")
            password = request.form.get("password")
            password1 = request.form.get("password1")
            # check password match
            if password != password1:
                message = "Passwords do not match !"
                return render_template("error.html",message=message)
            else:
                db.execute("INSERT INTO users  (username,hash) VALUES (:username, :hash)",{"username":username,"hash":generate_password_hash(password)})
                db.commit()
                return redirect(url_for('index'))
    else:
        return render_template("register.html")
    
@app.route("/logout",methods =["GET","POST"])
@login_required
def logout():
    """Log Out User"""
    session.clear()
    return redirect(url_for('index'))


@app.route("/books",methods=["POST"])
@login_required
def books():
    """Helps User Search for Book"""
  
    query = request.form.get("search")
    books = db.execute("SELECT * FROM books WHERE isbn LIKE :query OR title LIKE :query OR author LIKE :query",{"query":f"%{query}%"}).fetchall()

    return render_template("books.html", books=books)
    
@app.route("/books/<isbn>",methods=["GET","POST"])
@login_required
def book(isbn):
    """Details for a single book"""
    isbn = isbn
    reviews = db.execute("SELECT * FROM reviews WHERE isbn =:isbn",{"isbn":isbn}).fetchall()
    book = db.execute("SELECT * FROM books WHERE isbn =:isbn",{"isbn":isbn}).fetchone()
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": KEY, "isbns": isbn})
    if request.method =="GET":
        return render_template("book.html", book=book,res=res,reviews=reviews)
        
    else:
        # check if user had previously submitted reviews
        user_id= session["user_id"]
        user_review = db.execute("SELECT * FROM reviews WHERE isbn =:isbn AND user_id =:user_id",{"isbn":isbn,"user_id":session["user_id"]}).fetchone()
        if user_review == None:
            review_submit = request.form.get("review")
            review = db.execute("INSERT INTO reviews (isbn,review,user_id) VALUES (:isbn, :user_review,:user_id)",{"isbn":isbn,"user_review":review_submit,"user_id":user_id})
            db.commit()
            return render_template("book.html", book=book,res=res,reviews=reviews)
        else:
            message ="Sorry you have already submitted a review for this one"
            return render_template("error.html",message=message)
        
        
    

@app.route("/api/<isbn>",methods=["GET"])
@login_required

def api(isbn):
    """Helps User Search for Book"""
  
    isbn = isbn
    book = db.execute("SELECT * FROM books WHERE isbn =:isbn",{"isbn":isbn}).fetchone()
   

    return jsonify(book)