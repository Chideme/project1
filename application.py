import os

from flask import Flask, session, render_template,flash,request,redirect,url_for
from flask_session import Session
from sqlalchemy import create_engine
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
    
    @app.route("/search",methods=["GET","POST"])
    @login_required
    def search():
        """Helps User Search for Book"""
        if request.method == "POST":
            return render_template("search.html")
        else:
            return render_template("search.html")


