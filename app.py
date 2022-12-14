import os
import re

from functools import wraps
import psycopg2
import psycopg2.extras
from flask_swagger_ui import get_swaggerui_blueprint

from werkzeug.security import generate_password_hash, check_password_hash
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    flash,
    session,
    url_for,
)
import jwt
import datetime

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "prod")
app.config["JWT_HEADER_TYPE"] = "JWT"

SWAGGER_URL = "/swagger"
API_URL = "/static/swagger.json"
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "stack-overflow-lite-backend-REST-API"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Connect to db

DATABASE_URL = os.environ["DATABASE_URL"]

# Connect to database
conn = psycopg2.connect(DATABASE_URL)


# Check if user logged_in decorator
def is_logged_in(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if "logged_in" in session:
            # Ensure token is passed
            token = None
            if "x-access-token" in request.headers:
                token = request.headers["x-access-token"]
                
                if not token:  # throw error if no token provided
                    flash("Please login to access this page", "danger")
                    return redirect(url_for("login"))

                    # decode token to obtain user public_id
                jwt.decode(token, app.config["SECRET_KEY"], ["HS256"])

                flash("Please login to access this page", "danger")
                return redirect(url_for("login"))

            return f(*args, **kwargs)
        else:
            flash("Please login to access this page", "danger")
            return redirect(url_for("login"))

    return decorator


@app.route("/")
def index():
    return render_template("index.html")


## Home questions routes
@app.route("/questions", methods=["GET"])
def get_questions():
    # Create cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Execute get questions query
    cur.execute("SELECT * FROM questions ORDER BY date_asked DESC")

    # Init questions from db
    questions = cur.fetchall()

    conn.commit()

    cur.close()
    return render_template("questions.html", questions=questions)


## Get single question
@app.route("/question/<string:question_id>/", methods=["GET"])
def get_question(question_id):
    # Create cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Execute query
    cur.execute("SELECT * FROM questions WHERE id  = %s", [question_id])

    # Fetch question
    question = cur.fetchone()

    cur.execute(
        "SELECT * FROM answers WHERE question_id = %s ORDER BY answered_date DESC",
        [question_id],
    )
    # Fetch answers
    answers = cur.fetchall()

    # Close cursor
    cur.close()
    context = {"question": question, "answers": answers}

    return render_template("question.html", **context)


## Search Route
@app.route("/search_questions", methods=["GET", "POST"])
def search_questions():
    # Create cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Send request
    if request.method == "POST":
        searched_questions = request.form.get("q")

        # Validate form
        if not searched_questions:
            flash("Please fill in field", "danger")
            return redirect(url_for("get_questions"))

        # Execute query
        cur.execute(
            "SELECT * FROM questions WHERE title LIKE %s ORDER BY date_asked ASC ",
            [searched_questions],
        )

        questions = cur.fetchall()

        if not questions:
            flash("No questions found", "success")
            return redirect(url_for("get_questions"))

        # Commit to db
        conn.commit()

        # Close cursor
        cur.close()

    return render_template("search_questions.html", questions=questions)


## Register route
@app.route("/register", methods=["GET", "POST"])
def register():
    # Create cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Validate request
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # Hash password
        _hashed_password = generate_password_hash(password)

        # Check if account exists
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))

        # Fetch account
        account = cur.fetchone()

        # If account exists show error and validation
        if account:
            flash("Account already exists", "danger")
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email address", "danger")
        elif not re.match(r"[A-Za-z0-9]+", username):
            flash("Username must contain only characters and numbers", "danger")
        elif (
            not first_name or not last_name or not username or not password or not email
        ):
            flash("Please fill all fields", "danger")
        else:
            # Create account
            cur.execute(
                "INSERT INTO users (first_name, last_name, username, email, password) VALUES(%s, %s, %s, %s, %s)",
                (first_name, last_name, username, email, _hashed_password),
            )
            conn.commit()

            flash("You have registered successfully", "success")
            return redirect(url_for("login"))
    elif request.method == "POST":
        # Form is empty..
        flash("Please fill out form!")

    return render_template("register.html")


# User login
@app.route("/login", methods=["GET", "POST"])
def login():
    # Create cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Validate request
    if request.method == "POST":
        # Get Form fields data
        username = request.form["username"]
        password = request.form["password"]

        # Check if account exists
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))

        # Fetch result
        account = cur.fetchone()

        # confirm account
        if account:
            password_rs = account["password"]

            # Compare passwords if account exists
            if check_password_hash(password_rs, password):
                session["logged_in"] = True
                session["id"] = account["id"]
                session["username"] = account["username"]

                jwt.encode(
                    {
                        "user": account["username"],
                        "exp": str(
                            datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
                        ),
                    },
                    app.config["SECRET_KEY"],
                    "HS256",
                )

                flash("You have logged in successfully", "success")
                return redirect(url_for("dashboard"))
            else:
                # Account doesn't exist
                flash("Account does not exist", "error")
                return render_template("login.html")
        else:
            # Account doesn't exist
            flash("Incorrect username/password", "danger")
    return render_template("login.html")


## Logout
@app.route("/logout")
@is_logged_in
def logout():
    session.clear()
    flash("Logged out successfully", "success")
    return redirect(url_for("login"))


## Dashboard
@app.route("/dashboard", methods=["GET", "POST"])
@is_logged_in
def dashboard():
    # Create cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Execute get questions query
    cur.execute("SELECT * FROM questions ORDER BY date_asked DESC")

    # Init questions from db
    questions = cur.fetchall()

    return render_template("dashboard.html", questions=questions)


## Post question
@app.route("/post_question", methods=["GET", "POST"])
@is_logged_in
def post_question():
    # Create cursor connection
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # Validate request
    if request.method == "POST":
        title = request.form.get("title")
        body = request.form.get("body")

        # Validate form
        if not title or not body:
            flash("Please fill field", "danger")
            return render_template("post_question.html")

        # Execute query
        cur.execute(
            "INSERT INTO questions(username, title, body) VALUES (%s, %s, %s)",
            (session["username"], title, body),
        )

        # Commit to db
        conn.commit()

        # Close connection
        cur.close()

        flash("Question created successfully", "success")
        return redirect(url_for("dashboard"))
    return render_template("post_question.html")


## Get single question
@app.route("/user_question/<string:question_id>/", methods=["GET", "POST"])
@is_logged_in
def user_get_question(question_id):

    # Create cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Execute query
    cur.execute("SELECT * FROM questions WHERE id  = %s", [question_id])

    question = cur.fetchone()

    # Execute answers query
    cur.execute(
        "SELECT * FROM answers WHERE question_id = %s ORDER BY answered_date DESC",
        [question_id],
    )

    # Fetch answers
    answers = cur.fetchall()

    # Commit to db
    conn.commit()

    # Close cursor
    cur.close()

    context = {"question": question, "answers": answers}

    return render_template("user_question.html", **context)


#     # Answer question
@app.route("/answer_question/<string:question_id>/", methods=["GET", "POST"])
@is_logged_in
def post_answer(question_id):
    # create cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Execute query
    cur.execute("SELECT * FROM questions WHERE id = %s", [question_id])

    # Fetch question
    question = cur.fetchone()

    # Send request
    if request.method == "POST":
        answer = request.form.get("answer")

        # Validate answer input
        if not answer:
            flash("Please fill field", "danger")
            return render_template("answer_question.html", question=question)

        # Execute query
        cur.execute(
            "INSERT INTO answers (question_id, answer_username, answer_body) VALUES (%s, %s, %s)",
            [question_id, session["username"], answer],
        )

        # Commit to db
        conn.commit()

        # Close cursor
        cur.close()

        flash("Answer posted successfully", "success")
        return redirect(url_for("dashboard"))
    return render_template("answer_question.html", question=question)


## Profile route
@app.route("/profile", methods=["GET", "POST"])
@is_logged_in
def profile():
    # Create cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Execute questions query
    cur.execute(
        "SELECT * FROM questions WHERE username = %s ORDER BY date_asked DESC",
        [session["username"]],
    )

    # Fetch all questions
    questions = cur.fetchall()

    # Close cursor
    cur.close()

    return render_template("profile.html", questions=questions)


## Get profile question
@app.route("/profile_question/<string:question_id>/")
@is_logged_in
def profile_get_question(question_id):
    # Create cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Execute query
    cur.execute("SELECT * FROM questions WHERE id  = %s", [question_id])

    # Fetch questions
    question = cur.fetchone()

    # Get answers query
    cur.execute(
        "SELECT * FROM answers WHERE question_id = %s ORDER BY answered_date",
        [question_id],
    )

    # Fetch all answers
    answers = cur.fetchall()

    # Close cursor
    cur.close()

    return render_template("profile_question.html", question=question, answers=answers)


# Edit my question
@app.route("/edit_question/<string:question_id>/", methods=["GET", "POST"])
@is_logged_in
def edit_question(question_id):
    # Create cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Get query
    cur.execute("SELECT * FROM questions WHERE id = %s", [question_id])

    # Get question
    question = cur.fetchone()
    title = question["title"]

    # Get request form
    if request.method == "POST":
        title = request.form["title"]
        question = request.form["body"]

        # Validate
        if not question or not title:
            flash("Please fill all fields", "danger")
            return redirect(url_for("profile"))

        # Execute query
        # Update title
        cur.execute(
            "UPDATE questions SET title = %s WHERE id = %s", [title, question_id]
        )

        # Update body
        cur.execute(
            "UPDATE questions SET body = %s WHERE id = %s", [question, question_id]
        )

        # Commit to db
        conn.commit()

        # Close cursor
        cur.close()

        flash("Question edited successfully", "success")
        return redirect(url_for("profile"))
    return render_template("edit_question.html", question=question)


## Get myPro profile answers
@app.route("/myPro_answers", methods=["GET", "POST"])
@is_logged_in
def get_myPro_answers():
    # Create cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Execute  answers query
    cur.execute(
        "SELECT * FROM answers WHERE answer_username = %s ORDER BY answered_date DESC",
        [session["username"]],
    )

    # Get answers
    answers = cur.fetchall()

    # close cursor
    cur.close()

    return render_template("myPro_answers.html", answers=answers)


## Edit my answer
@app.route("/edit_answer/<string:answer_id>/", methods=["GET", "POST"])
@is_logged_in
def edit_answer(answer_id):
    # Create cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Get query
    cur.execute("SELECT * FROM answers WHERE id = %s", [answer_id])

    # Get answer
    answer = cur.fetchone()

    # Get request
    if request.method == "POST":
        answer = request.form["answer"]

        # Validate answer
        if not answer:
            flash("Please fill in answer field", "danger")
            return render_template("edit_answer.html", answer=answer)

        # Execute query
        cur.execute(
            "UPDATE answers SET answer_body = %s WHERE id = %s", [answer, answer_id]
        )

        # Commit to db
        conn.commit()

        flash("Answer edited successfully", "success")
        return redirect(url_for("profile"))

    return render_template("edit_answer.html", answer=answer)


## Upvote answer
@app.route("/upvote_answer/<answer_id>/", methods=["POST"])
@is_logged_in
def upvote_answer(answer_id):

    # Create cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("SELECT * FROM answers WHERE id = %s", [answer_id])

    answer = cur.fetchone()
    answer_username = answer["answer_username"]

    # Check if not user
    if session["username"] != answer_username:
        # Execute query
        cur.execute("UPDATE answers SET votes = votes +1 WHERE id = %s", [answer_id])
    else:
        flash("You can't vote your answer", "success")
        return redirect(url_for("dashboard"))

    # Commit to db
    conn.commit()

    # Close cursor
    cur.close()

    flash("Voted successfully", "success")
    return redirect(url_for("dashboard"))


## DownVote answer
@app.route("/downvote_answer/<answer_id>/", methods=["POST"])
@is_logged_in
def downvote_answer(answer_id):
    # Create cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Fetch answer
    cur.execute("SELECT * FROM answers WHERE id = %s", [answer_id])
    #
    answer = cur.fetchone()
    answer_username = answer["answer_username"]

    # Check if its users answer
    if session["username"] != answer_username:
        # Execute query
        cur.execute("UPDATE answers SET votes = votes -1 WHERE id = %s", [answer_id])
    else:

        flash("You can't vote your answer", "success")
        return redirect(url_for("dashboard"))

    # Commit to db
    conn.commit()

    # Close cursor
    cur.close()

    flash("Voted successfully", "success")
    return redirect(url_for("dashboard"))


## Add comment
@app.route("/post_comment/<string:answer_id>/", methods=["GET", "POST"])
@is_logged_in
def post_comment(answer_id):
    # Create cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Execute question query
    cur.execute("SELECT * FROM answers WHERE id = %s", [answer_id])

    # Fetch question
    answer = cur.fetchone()

    # send request
    if request.method == "POST":
        comment = request.form.get("comment")

        # Validate comment
        if not comment:
            flash("Please fill in the comment field", "danger")
            return render_template("post_comment.html", answer=answer)

        # Execute query
        cur.execute(
            "INSERT INTO comments (comment_answer_id, comment_author, comment_body) VALUES (%s, %s, %s)",
            [answer_id, session["username"], comment],
        )

        # Commit to db
        conn.commit()

        # Close cursor
        cur.close()

        flash("Comment created successfully", "success")
        return redirect(url_for("dashboard"))
    return render_template("post_comment.html", answer=answer)


## View comments
@app.route("/view_comments/<string:comment_id>/", methods=["GET", "POST"])
@is_logged_in
def view_comments(comment_id):
    # create cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Execute get answer query
    cur.execute("SELECT * FROM answers WHERE id = %s", [comment_id])

    # Fetch answer
    answer = cur.fetchone()

    # Get comments query
    cur.execute(
        "SELECT * FROM comments WHERE comment_answer_id = %s ORDER BY comment_date DESC",
        [comment_id],
    )
    # Fetch comments
    comments = cur.fetchall()

    # Check if comments are available
    if not comments:
        flash("No comments found", "success")
        return redirect(url_for("dashboard"))

    # Commit to db
    conn.commit()

    # Close connection
    cur.close()

    return render_template("view_comments.html", answer=answer, comments=comments)


## Edit comment
@app.route("/edit_comment/<string:comment_id>/", methods=["GET", "POST"])
@is_logged_in
def edit_comment(comment_id):
    # Create cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Get query
    cur.execute("SELECT * FROM comments WHERE id = %s", [comment_id])

    # fetch question
    comment = cur.fetchone()

    # Get request form
    if request.method == "POST":
        comment = request.form["comment"]

        # Validate
        if not comment:
            flash("Please fill comment field", "danger")
            return render_template("edit_comment.html", comment=comment)

        # Execute query
        cur.execute(
            "UPDATE comments SET comment_body = %s WHERE id = %s", [comment, comment_id]
        )

        # Commit to db
        conn.commit()

        # Close cursor
        cur.close()
        flash("Comment edited successfully", "success")
        return redirect(url_for("dashboard"))
    return render_template("edit_comment.html", comment=comment)


## Mark answer
@app.route("/mark_answer/<string:answer_id>/", methods=["GET", "PUT"])
@is_logged_in
def mark_answer(answer_id):
    # Create cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Get marked_answer
    cur.execute("UPDATE answers SET marked_answer = 'True' WHERE id = %s", [answer_id])

    # Commit to db
    conn.commit()

    # Close cursor
    cur.close()

    flash("Marked answer successfully", "success")
    return redirect(url_for("profile"))


## UnMark answer
@app.route("/unmark_answer/<string:answer_id>/", methods=["GET", "PUT"])
@is_logged_in
def unmark_answer(answer_id):
    # Create cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Get marked_answer
    cur.execute("UPDATE answers SET marked_answer = 'False' WHERE id = %s", [answer_id])

    # Commit to db
    conn.commit()

    # Close cursor
    cur.close()

    flash("Un-marked answer successfully", "success")
    return redirect(url_for("profile"))


## Profile Delete question
@app.route("/delete_question/<string:question_id>/", methods=["POST"])
@is_logged_in
def delete_question(question_id):
    # Create cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Execute query
    cur.execute("DELETE FROM questions WHERE id = %s", [question_id])

    # Commit to db
    conn.commit()

    # Close cursor
    cur.close()
    flash("Question deleted successfully", "danger")
    return redirect(url_for("profile"))


## Profile Delete answer
@app.route("/profile_delete_answer/<string:answer_id>/", methods=["POST"])
@is_logged_in
def delete_answer(answer_id):
    # Create cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Execute query
    cur.execute("DELETE FROM answers WHERE id = %s", [answer_id])

    # Commit to db
    conn.commit()

    # Close cursor
    cur.close()

    flash("Answer deleted successfully", "danger")
    return redirect(url_for("profile"))


## Dashboard Delete answer
@app.route("/dashboard_delete_answer/<string:answer_id>/", methods=["POST"])
@is_logged_in
def dashboard_delete_answer(answer_id):
    # Create cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Execute query
    cur.execute("DELETE FROM answers WHERE id = %s", [answer_id])

    # Commit to db
    conn.commit()

    # Close cursor
    cur.close()

    flash("Answer deleted successfully", "danger")
    return redirect(url_for("dashboard"))


## Delete comment
@app.route("/delete_comment/<string:comment_id>/", methods=["POST"])
@is_logged_in
def delete_comment(comment_id):
    # Create cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Execute query
    cur.execute("DELETE FROM comments WHERE id = %s", [comment_id])

    # Commit to db
    conn.commit()

    # Close cursor
    cur.close()
    flash("Comment deleted successfully", "danger")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run()
