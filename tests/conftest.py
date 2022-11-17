import os
from app import app as flask_app
import pytest
import psycopg2
from .sql.user_sql import user_sql

DATABASE_URL = os.environ["DATABASE_URL"]

@pytest.fixture
def app():
    yield flask_app
    
        
@pytest.fixture 
def client(app):
  
  return app.test_client()


@pytest.fixture
def cursor():
  conn = psycopg2.connect(DATABASE_URL)
  
  cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
  yield cur
  # cur.close()
  

@pytest.fixture
def galice(cursor):
    cursor.execute(user_sql, {"first_name": "Sweetie", 
                              "last_name": "Mufasa",
                              "username": "gully",
                              "email": "galice@gmail.com",
                              "password": "12345"
                              })  
   
      
  

  

  
  
  
  
  





  