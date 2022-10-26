import psycopg2

DATABASE_URL = 'postgres://gchmnzgwfhctbv:62856072bcce8f993d376678297c70b498fa614ad771021dde792517b6741f85@ec2-23-20-140-229.compute-1.amazonaws.com:5432/d2barv9p59v20e'
    
conn = psycopg2.connect(DATABASE_URL)

cur = conn.cursor()

# Create tables 

def create_tables():
  # Users table
  cur.execute("CREATE TABLE users(id SERIAL PRIMARY KEY,first_name VARCHAR(255) NOT NULL, last_name VARCHAR(255) NOT NULL, username VARCHAR(255) UNIQUE, email VARCHAR(100) NOT NULL, password VARCHAR(255) NOT NULL, register_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")
    
    # Questions table
  cur.execute("CREATE TABLE questions(id SERIAL PRIMARY KEY, username VARCHAR(255), title VARCHAR(300) NOT NULL, body TEXT NOT NULL,date_asked TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(username) REFERENCES users(username) ON DELETE CASCADE);")

  # Answers table 
  cur.execute("CREATE TABLE answers(id SERIAL PRIMARY KEY, question_id INT, answer_username VARCHAR(255), answer_body TEXT NOT NULL,marked_answer BOOLEAN, votes INTEGER DEFAULT 0,answered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(question_id) REFERENCES questions(id) ON DELETE CASCADE,FOREIGN KEY(answer_username) REFERENCES users(username) ON DELETE CASCADE);")

  # Comments table 
  cur.execute("CREATE TABLE comments(id SERIAL PRIMARY KEY, comment_answer_id INT, comment_author VARCHAR(255), comment_body TEXT,comment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(comment_author) REFERENCES users(username)ON DELETE CASCADE, FOREIGN KEY(comment_answer_id) REFERENCES answers(id) ON DELETE CASCADE);")

  # Commit to db
  conn.commit()

  # Close cursor
  cur.close()

  conn.close()         