from flask import Flask, render_template, request, redirect, session, url_for
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, validators, PasswordField
from passlib.hash import sha256_crypt

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

# # Register form
# class RegisterForm(Form):
#   first_name = StringField("Name", [validators.Length(min=1, max=50)])
#   last_name = StringField("LastName", [validators.Length(min=1, max=50)])
#   email = StringField("Email", [validators.Length(min=6, max=50)])
#   password = PasswordField("Password", [validators.DataRequired(), validators.EqualTo("Confirm", message="Password do not match")])
#   confirm = PasswordField("Confirm Password")
  
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

if __name__ == "__main__":
  app.run(debug=True)