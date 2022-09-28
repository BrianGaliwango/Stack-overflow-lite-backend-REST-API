from email.quoprimime import body_check
from flask import Flask, render_template, request, redirect, session, url_for
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, validators, PasswordField
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)

# config MYSQL
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "galice"
app.config["MYSQL_PASSWORD"] = "12345678"
app.config["MYSQL_DB"] = "stackoverflow"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

# Init mysql
mysql = MySQL(app)
app.secret_key = "secret123456"

@app.route("/")
def index():
  return render_template("index.html")
  
@app.route("/register", methods=["GET", "POST"])
def register():
  if request.method == "POST":
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    password = sha256_crypt.encrypt(str(request.form.get("password")))
    
    # Create cursor
    cur = mysql.connection.cursor()
      
    # Execute query
    cur.execute("INSERT INTO users(first_name, last_name, email, password) VALUES (%s, %s, %s, %s)", (first_name, last_name, email, password))
    
    # commit to db
    mysql.connection.commit()
    
    # Close connection
    cur.close() 
    return redirect(url_for("index"))
  return render_template("register.html")

# User login
@app.route("/login", methods=["GET", "POST"])
def login():
  if request.method == "POST":
    # Get Form fields data
    email = request.form["email"]
    password_candidate = request.form["password"]
    
    # Create cursor
    cur = mysql.connection.cursor()
    
    # Get user by email
    result = cur.execute("SELECT * FROM users WHERE email = %s", [email])

    # Verify result
    if result > 0:
      # Get stored hash
      data = cur.fetchone()
      password = data["password"]
      
      # Compare passwords
      if sha256_crypt.verify(password_candidate, password):
        # When passed login
        session["logged_in"] = True
        session["email"] = email

        return redirect(url_for("dashboard"))
      else:
        return render_template("login.html")
      # Close connection
    cur.close()
  else:
      return render_template("login.html")    
  return render_template("login.html")

# Check if the user is logged in decorator
def is_logged_in(f):
  @wraps(f)
  def wrap(*args, **kwargs):
   if "logged_in" in session:
     return f(*args, **kwargs)
   else:
     return redirect(url_for("login")) 
  return wrap 

# Logout
@app.route("/logout")
@is_logged_in
def logout():
  session.clear()
  return redirect(url_for("login"))

@app.route("/dashboard", methods=["GET", "POST"])
@is_logged_in
def dashboard():
  # Create cursor
  cur = mysql.connection.cursor()
  
  # Execute get questions query
  result = cur.execute("SELECT * FROM questions")
  
  # Init questions from db
  questions = cur.fetchall()
  
  if result > 0:
    return render_template("dashboard.html", questions=questions) 
  else:
    return render_template("dashboard.html")
  cur.close()
  
# Post question 
@app.route("/post_question", methods=["GET", "POST"])
@is_logged_in
def post_question():
  if request.method == "POST":
    title = request.form.get("title")
    body = request.form.get("body")
    
    # Create cursor connection
    cur = mysql.connection.cursor()
    
    # Execute query
    cur.execute("INSERT INTO questions(title, body, asked_by) VALUES (%s, %s, %s)", (title, body, session["email"]))
    
    # Commit to db
    mysql.connection.commit()
    
    # Close connection
    cur.close()
    
    return redirect(url_for("dashboard"))
  
  return render_template("post_question.html")

if __name__ == "__main__":
  app.run(debug=True)