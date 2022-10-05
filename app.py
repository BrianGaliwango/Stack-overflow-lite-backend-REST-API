from unittest import result
from flask import Flask, render_template, request, redirect, session, url_for
from flask_mysqldb import MySQL
from flask_login import login_manager ,current_user
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

@app.route("/questions")
def questions():
  # Create cursor
  cur = mysql.connection.cursor()
  
  # Execute get questions query
  result = cur.execute("SELECT * FROM questions")
  
  # Init questions from db
  questions = cur.fetchall()
  
  if result > 0:
    return render_template("questions.html", questions=questions) 
  else:
    return render_template("questions.html")
  cur.close()
  
# Get single question
@app.route("/question/<string:id>/")
def get_question(id):
    # Create cursor
    cur = mysql.connection.cursor()
    
    # Execute query
    result = cur.execute("SELECT * FROM questions WHERE id  = %s", [id])
    
    #Fetch question 
    question = cur.fetchone()
       
    result = cur.execute("SELECT * FROM answers WHERE question_id = %s", [id])
    # Fetch answers
    answers = cur.fetchall()
    
    cur.close()
    
    # answers = cur.fetchall()
    return render_template("question.html", question=question, answers=answers)

    
#Register route 
@app.route("/register", methods=["GET", "POST"])
def register():
  if request.method == "POST":
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    username = request.form.get("username")
    email = request.form.get("email")
    password = sha256_crypt.encrypt(str(request.form.get("password")))
    
    # Validate form
    if not first_name or not last_name or not username or not email or not password or not first_name or not last_name:
      print("Please valid inputs")
      return render_template("register.html")
    
    # Create cursor
    cur = mysql.connection.cursor()
      
    # Execute query
    cur.execute("INSERT INTO users(first_name, last_name, username, email, password) VALUES (%s, %s, %s, %s, %s)", (first_name, last_name, username, email, password))
    
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
    username = request.form["username"]
    password_candidate = request.form["password"]
    
    # Validate username and password_candidate
    if not username or not password_candidate:
      print(username, password_candidate, "invalid inputs")   
      return render_template("login.html")
    
    # Create cursor
    cur = mysql.connection.cursor()
    
    # Get user by email
    result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

    # Verify result
    if result > 0:
      # Get stored hash
      data = cur.fetchone()
      password = data["password"]
      
      # Compare passwords
      if sha256_crypt.verify(password_candidate, password):
        # When passed login
        session["logged_in"] = True
        session["username"] = username
        # session["id"] = id

        return redirect(url_for("dashboard"))
      else:
        return render_template("login.html")
      # Close connection
    cur.close()
  else:
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

# Profile route
@app.route("/profile", methods=["GET", "POST"])
@is_logged_in
def profile():
  # Create cursor
  cur = mysql.connection.cursor()
  
  # Execute questions query
  result = cur.execute("SELECT * FROM questions WHERE username = %s", [session["username"]])
  
  questions = cur.fetchall()
  
  # Execute  answers query
  result = cur.execute("SELECT * FROM answers WHERE answer_username = %s", [session["username"]])
  
  # Get answers
  answers = cur.fetchall()
  
  return render_template("profile.html", questions=questions, answers=answers)

# Dashboard
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
  
# Get single question
@app.route("/user_question/<string:id>/", methods=["GET", "POST"])
@is_logged_in
def user_get_question(id):
    
    # Create cursor
    cur = mysql.connection.cursor()
    
    # Execute query
    result = cur.execute("SELECT * FROM questions WHERE id  = %s", [id])
    
    question = cur.fetchone()
       
    result = cur.execute("SELECT * FROM answers WHERE question_id = %s", [id])
    
    answers = cur.fetchall()
    
     # Get comments
    cur = mysql.connection.cursor()
        
    # Close cursor
    cur.close()
    
    context = {"question":question,"answers":answers}
    
    return render_template("user_question.html", **context)

#Get profile question 
@app.route("/profile_question/<string:id>/")
@is_logged_in
def profile_get_question(id):
    # Create cursor
    cur = mysql.connection.cursor()
    
    # Execute query
    result = cur.execute("SELECT * FROM questions WHERE id  = %s", [id])
    
    question = cur.fetchone()
       
    result = cur.execute("SELECT * FROM answers WHERE question_id = %s", [id])
    
    answers = cur.fetchall()
    # Close cursor
    cur.close()
    
    return render_template("profile_question.html", question=question, answers=answers)    
    
# Post question 
@app.route("/post_question", methods=["GET", "POST"])
@is_logged_in
def post_question():
  if request.method == "POST":
    title = request.form.get("title")
    body = request.form.get("body")
    
    if not title or not body:
      print("Please fill fields")
      return render_template("post_question.html")
    
    # Create cursor connection
    cur = mysql.connection.cursor()
    
    # Execute query
    cur.execute("INSERT INTO questions(username, title, body) VALUES (%s, %s, %s)", (session["username"], title, body))
    
    # Commit to db
    mysql.connection.commit()
    
    # Close connection
    cur.close()
    
    return redirect(url_for("dashboard"))  
  return render_template("post_question.html")

# Answer question
@app.route("/answer_question/<string:id>/", methods=["GET", "POST"])
# @is_logged_in()
def post_answer(id): 
  # create cursor 
  cur = mysql.connection.cursor()
  
  # Execute query
  result = cur.execute("SELECT * FROM questions WHERE id = %s", [id])
  
  question = cur.fetchone()
  
  # Send request
  if request.method == "POST":
    question_answer = request.form.get("answer")
    
    # Validate answer input
    if not question_answer:
      print("Please fill field")
      # return redirect(url_for("dashboard"))
      return render_template("answer_question.html", answer=question_answer, question=question)

    #  create cursor
    cur = mysql.connection.cursor()
    
    # Execute query
    cur.execute("INSERT INTO answers (question_id, answer_username, answer_body) VALUES (%s, %s, %s)", [id, session["username"], question_answer])
    
    # Commit to db   
    mysql.connection.commit()
    
    # Close cursor
    cur.close()
    return redirect(url_for("dashboard"))
  return render_template("answer_question.html", question=question)

# Mark answer
@app.route("/mark_answer/<string:answer_id>", methods=["GET", "PUT"])
@is_logged_in
def mark_answer(answer_id):
  # Create cursor
  cur = mysql.connection.cursor()
  
  # Execute query
  result = cur.execute("SELECT marked_answer FROM answers WHERE marked_answer = %s", [answer_id])
  
  # Get marked_answer
  marked_answer = cur.fetchone()
  
  cur.execute("UPDATE answers SET marked_answer = '1' WHERE id = %s", [answer_id])
  
  # Commit to db
  cur.connection.commit()
  
  # Close cursor
  cur.close()
  
  return redirect(url_for("profile"))
  
#Edit my question
@app.route("/edit_question/<string:id>", methods=["GET", "POST"])
@is_logged_in
def edit_question(id):
  # Create cursor
  cur = mysql.connection.cursor()
  
  # Get query
  result = cur.execute("SELECT * FROM questions WHERE id = %s", [id])
  
  # Get question
  question = cur.fetchone()
  
  # Get request form
  if request.method == "POST":
    question = request.form["question"]
    
    # Validate
    if not question:
      print("please enter a questions")
      return render_template("edit_question.html", question=question)
    # Create cursor
    cur = mysql.connection.cursor()
    
    # Execute query
    cur.execute("UPDATE questions SET body = %s WHERE id = %s", [question, id])
  
    # Commit to db
    mysql.connection.commit()
    
    # Close cursor
    cur.close()
    return redirect(url_for("profile"))  
  return render_template("edit_question.html", question=question)

#Edit my answer
@app.route("/edit_answer/<string:id>", methods=["GET", "POST"])
def edit_answer(id):
  #Create cursor
  cur = mysql.connection.cursor()
  
  # Get query
  result = cur.execute("SELECT * FROM answers WHERE id = %s", [id])
  
  # Get result
  answer = cur.fetchone()
  
  # Get request
  if request.method == "POST":
    answer = request.form["answer"]
    
    # Validate answer
    if not answer:
      print("Please fill in answer")
      return render_template("edit_answer.html", answer=answer)
  
    # Create cursor
    cur = mysql.connection.cursor()
    
    # Execute query
    cur.execute("UPDATE answers SET answer_body = %s WHERE id = %s", [answer, id])
    
    # Commit to db
    mysql.connection.commit()
    
    # Close cursor
    cur.close()
    return redirect(url_for("dashboard"))
    
  return render_template("edit_answer.html", answer=answer)

# Delete question
@app.route("/delete_question/<string:id>", methods=["POST"])
@is_logged_in
def delete_question(id):
  # Create cursor
  cur = mysql.connection.cursor()
  
  # Execute query
  cur.execute("DELETE FROM questions WHERE id = %s", [id])
  
  # Commit to db
  cur.connection.commit()
  
  # Close cursor
  cur.close()
  
  return redirect(url_for("profile"))

# Delete answer 
@app.route("/delete_answer/<string:id>", methods=["POST"])
@is_logged_in
def delete_answer(id):
  # Create cursor
  cur = mysql.connection.cursor()
  
  # Execute query
  cur.execute("DELETE FROM answers WHERE id = %s", [id])
  
  # Commit to db
  cur.connection.commit()
  
  # Close cursor
  cur.close()
  
  return redirect(url_for("profile"))

if __name__ == "__main__":
  app.run(debug=True)