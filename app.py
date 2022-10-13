from flask import Flask, render_template, request, redirect, flash, session, url_for
from flask_mysqldb import MySQL
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
    
    # Close cursor
    cur.close()
    
    return render_template("question.html", question=question, answers=answers)
  
#Search Route
@app.route("/search_questions", methods=["GET", "POST"])
def search_questions():
  # Send request
  if request.method == "POST":
    search_questions = request.form.get("q")
    
    if not search_questions:
      flash("Please fill in field", "danger")
      return redirect(url_for("questions"))
    
    # Create cursor 
    cur = mysql.connection.cursor()
    
    # Execute query
    result = cur.execute("SELECT * FROM questions WHERE title LIKE %s", [search_questions])

    if result > 0:
      questions = cur.fetchall()
    else:
      flash("No questions found", "success")
      return redirect(url_for("questions"))  
       
    # Commit to db
    mysql.connection.commit()
    
    # Close cursor
    cur.close()
    
  return render_template("search_questions.html", questions=questions) 
   
#Register route 
@app.route("/register", methods=["GET", "POST"])
def register():
  if request.method == "POST":
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    username = request.form.get("username")
    email = request.form.get("email")
    # password = sha256_crypt.encrypt(str(request.form.get("password")))
    password = request.form.get("password")
    
    # Validate form
    if not first_name or not last_name or not username or not email or not first_name or not last_name:
      flash("Please fill in all fields", "danger")    
      return render_template("register.html") 
    
    if len(password) < 5:
      flash("Password too short", "danger")
      return render_template("register.html")
    
    # Encrypt password
    password = sha256_crypt.encrypt(str(("password")))
     
    # Create cursor
    cur = mysql.connection.cursor()
    
    # Execute  check  existing users query  
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    existing_username = cur.fetchone()
    if existing_username is not None:
      flash("Username already exists", "danger")     
      return render_template("register.html")
    
    # Check for existing email
    cur.execute("SELECT * FROM users WHERE email = %s", (email,)) 
    existing_email = cur.fetchone()
    if existing_email is not None:
      flash("Email already exists", "danger")
      return render_template("register.html")
        
    # Insert users query
    cur.execute("INSERT INTO users(first_name, last_name, username, email, password) VALUES (%s, %s, %s, %s, %s)", (first_name, last_name, username, email, password))
      
    # commit to db
    mysql.connection.commit()
    
    # Close connection
    cur.close()   
    
    flash("You are now registered", "success")  
    print(password)  
    return redirect(url_for("login"))      
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
      flash("Please fill all fields", "danger")   
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
        session.permanent = False
        session["logged_in"] = True
        session["username"] = username

        flash("You are now logged in", "success")
        return redirect(url_for("dashboard"))
      else:
        error = "Invalid inputs"
        return render_template("login.html", error=error)
      # Close connection
      cur.close()
    else:
      error = "Username not found"
      return render_template("login.html", error=error)
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
  flash("Logged out successfully", "success")
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
  
  return render_template("profile.html", questions=questions)

#Get myPro profile answers
@app.route("/myPro_answers", methods=["GET", "POST"])
@is_logged_in
def get_myPro_answers():
  # Create cursor
  cur = mysql.connection.cursor()
  # Execute  answers query
  result = cur.execute("SELECT * FROM answers WHERE answer_username = %s", [session["username"]])
  
  # Get answers
  answers = cur.fetchall()
  
  # Get answered questions
  # create cursor
  cur = mysql.connection.cursor()
  
  # close cursor
  cur.close()
  
  return render_template("myPro_answers.html", answers=answers, questions=questions)

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
      
    #Execute answers query  
    result = cur.execute("SELECT * FROM answers WHERE question_id = %s", [id])
    
    answers = cur.fetchall()
    
    # Commit to db
    mysql.connection.commit()
    
    # Close cursor
    cur.close()
    
    context = {"question":question, "answers":answers}
    
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
    
    #Get answers query 
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
      flash("Please fill field", "danger")
      return render_template("post_question.html")
    
    # Create cursor connection
    cur = mysql.connection.cursor()
    
    # Execute query
    cur.execute("INSERT INTO questions(username, title, body) VALUES (%s, %s, %s)", (session["username"], title, body))
    
    # Commit to db
    mysql.connection.commit()
    
    # Close connection
    cur.close()
    
    flash("Question created successfully", "success")
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
      flash("Please fill field", "danger")
      return render_template("answer_question.html", answer=question_answer, question=question)

    #  create cursor
    cur = mysql.connection.cursor()
    
    # Execute query
    cur.execute("INSERT INTO answers (question_id, answer_username, answer_body) VALUES (%s, %s, %s)", [id, session["username"], question_answer])
    
    # Commit to db   
    mysql.connection.commit()
       
    # Close cursor
    cur.close()
    
    flash("Answer posted successfully", "success")
    return redirect(url_for("dashboard"))
  return render_template("answer_question.html", question=question)

# Upvote answer
@app.route("/upvote_answer/<answer_id>", methods=["POST"])
@is_logged_in
def upvote_answer(answer_id):

    # Create cursor
    cur = mysql.connection.cursor()
    
    # Execute query
    cur.execute("UPDATE answers SET votes = votes + 1 WHERE id = %s", [answer_id])
    
    # Commit to db
    mysql.connection.commit()
              
    # Close cursor
    cur.close()
    flash("Voted successfully", "success")
    return redirect(url_for("dashboard"))

# DownVote answer
@app.route("/downvote_answer/<answer_id>", methods=["POST"])
@is_logged_in
def downvote_answer(answer_id):
    # Create cursor
    cur = mysql.connection.cursor()
    
    # Execute query
    cur.execute("UPDATE answers SET votes = votes - 1 WHERE id = %s", [answer_id])
    
    # Commit to db
    mysql.connection.commit()
              
    # Close cursor
    cur.close()

    flash("Voted successfully", "success")
    return redirect(url_for("dashboard"))

# Mark answer
@app.route("/mark_answer/<string:answer_id>", methods=["GET", "PUT"])
@is_logged_in
def mark_answer(answer_id):
  # Create cursor
  cur = mysql.connection.cursor()
  
  # Execute query
  result = cur.execute("SELECT marked_answer FROM answers WHERE marked_answer = %s", [answer_id])
  
  # Get marked_answer 
  cur.execute("UPDATE answers SET marked_answer = '1' WHERE id = %s", [answer_id])
  
  # Commit to db
  cur.connection.commit()
  
  question = cur.fetchone()
  
  # Close cursor
  cur.close()
  
  flash("Marked answer successfully", "success")
  return redirect(url_for("profile"))

# UnMark answer
@app.route("/unmark_answer/<string:answer_id>", methods=["GET", "PUT"])
@is_logged_in
def unmark_answer(answer_id):
  # Create cursor
  cur = mysql.connection.cursor()
  
  # Execute query
  result = cur.execute("SELECT marked_answer FROM answers WHERE marked_answer = %s", [answer_id])
  
  # Get marked_answer  
  cur.execute("UPDATE answers SET marked_answer = '0' WHERE id = %s", [answer_id])
  
  # Commit to db
  cur.connection.commit()
  
  question = cur.fetchone()

  # Close cursor
  cur.close()
  flash("Un-marked answer successfully", "success")
  return redirect(url_for("profile"))
 
# Add comment
@app.route("/post_comment/<string:id>", methods=["GET", "POST"]) 
@is_logged_in
def post_comment(id):
  # Create cursor
  cur = mysql.connection.cursor()
  
  # Execute question query
  result = cur.execute("SELECT * FROM answers WHERE id = %s", [id])
  
  # Fetch question
  answer = cur.fetchone()
  
  # Commit to db
  mysql.connection.commit()
  
  # send request
  if request.method == "POST":
    comment = request.form.get("comment")
    
    if not comment:
      flash("Please fill in the comment field", "danger")
      return render_template("post_comment.html", answer=answer)
      
      # Create cursor
    cur = mysql.connection.cursor()
    
    # Execute query
    cur.execute("INSERT INTO comments (comment_answer_id, comment_author, comment_body) VALUES (%s, %s, %s)", [id, session["username"], comment])
    
    #Commit to db
    mysql.connection.commit()
    
    # Close cursor
    cur.close()
    
    flash("Comment created successfully", "success")
    return redirect(url_for("dashboard"))  
  return render_template("post_comment.html", answer=answer)

# View comments
@app.route("/view_comments/<string:id>", methods=["GET", "POST"])
@is_logged_in
def view_comments(id):
  # create cursor
  cur = mysql.connection.cursor()
  
  # Execute get answer query
  cur.execute("SELECT * FROM answers WHERE id = %s", [id])
  
  answer = cur.fetchone()
  
  # Commit to db
  mysql.connection.commit()
  
  # Get comments query
  result =cur.execute("SELECT * FROM comments WHERE comment_answer_id = %s", [id])
  
  if not result  > 0:
    flash("No comments found", "success")
    return redirect(url_for("dashboard"))
  
  comments = cur.fetchall()
  
  # Commit to db
  mysql.connection.commit()
  
  # Close connection
  cur.close()
   
  return render_template("view_comments.html", answer=answer, comments=comments)

# Edit comment 
@app.route("/edit_comment/<string:id>", methods=["GET", "POST"])
@is_logged_in
def edit_comment(id):
  # Create cursor
  cur = mysql.connection.cursor()
  
  # Get query
  result = cur.execute("SELECT * FROM comments WHERE id = %s", [id])
  
  # Get question
  comment = cur.fetchone()
  
  # Get request form
  if request.method == "POST":
    comment = request.form["comment"]
    
    # Validate
    if not comment:
      flash("Please fill comment field", "danger")
      return render_template("edit_comment.html", comment=comment)
    # Create cursor
    cur = mysql.connection.cursor()
    
    # Execute query
    cur.execute("UPDATE comments SET comment_body = %s WHERE id = %s", [comment, id])
  
    # Commit to db
    mysql.connection.commit()
    
    # Close cursor
    cur.close()
    flash("Comment edited successfully", "success")
    return redirect(url_for("dashboard"))  
  return render_template("edit_comment.html", comment=comment)
  
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
      flash("Please fill question field", "danger")
      return render_template("edit_question.html", question=question)
    # Create cursor
    cur = mysql.connection.cursor()
    
    # Execute query
    cur.execute("UPDATE questions SET body = %s WHERE id = %s", [question, id])
  
    # Commit to db
    mysql.connection.commit()
    
    # Close cursor
    cur.close()
    flash("Question edited successfully", "success")
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
      flash("Please fill in answer field", "danger")
      return render_template("edit_answer.html", answer=answer)
  
    # Create cursor
    cur = mysql.connection.cursor()
    
    # Execute query
    cur.execute("UPDATE answers SET answer_body = %s WHERE id = %s", [answer, id])
    
    # Commit to db
    mysql.connection.commit()
    
    # Get answers 
    # Create cursor
    cur = mysql.connection.cursor()
    
    # Execute query
    result = cur.execute("SELECT * FROM answers WHERE answer_username = %s", [session["username"]])
    
    answers = cur.fetchall()
    
    # Close cursor
    cur.close()
    
    flash("Answer edited successfully", "success")
    # return redirect(url_for("profile"))
    return render_template("myPro_answers.html", answers=answers)
    
  return render_template("edit_answer.html", answer=answer)

# Profile Delete question
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
  flash("Question deleted successfully", "danger")
  return redirect(url_for("profile"))

# Profile Delete answer 
@app.route("/delete_answer/<string:id>", methods=["POST"])
@is_logged_in
def delete_answer(id):
  # Create cursor
  cur = mysql.connection.cursor()
  
  # Execute query
  cur.execute("DELETE FROM answers WHERE id = %s", [id])
  
  # Commit to db
  cur.connection.commit()
  
  # Create get answers cursor 
  cur = mysql.connection.cursor()
  
  # Execute query
  result = cur.execute("SELECT * FROM answers WHERE answer_username = %s", [session["username"]])
  
  answers = cur.fetchall()
  
  # Close cursor
  cur.close()
  
  flash("Answer deleted successfully", "danger")
  # return redirect(url_for("myPro_answers"))
  return render_template("myPro_answers.html", answers=answers)

# Dashboard Delete answer 
@app.route("/dashboard_delete_answer/<string:id>", methods=["POST"])
@is_logged_in
def dashboard_delete_answer(id):
  # Create cursor
  cur = mysql.connection.cursor()
  
  # Execute query
  cur.execute("DELETE FROM answers WHERE id = %s", [id])
  
  # Commit to db
  cur.connection.commit()
  
  # Close cursor
  cur.close()
  
  flash("Answer deleted successfully", "danger")
  return redirect(url_for("dashboard"))

#Delete comment
@app.route("/delete_comment/<string:id>", methods=["POST"])
@is_logged_in
def delete_comment(id):
  # Create cursor
  cur = mysql.connection.cursor()
  
  # Execute query
  cur.execute("DELETE FROM comments WHERE id = %s", [id])
  
  # Commit to db
  cur.connection.commit()
  
  # Close cursor
  cur.close()
  flash("Comment deleted successfully", "danger")
  return redirect(url_for("dashboard"))
  
if __name__ == "__main__":
  app.run(debug=True)