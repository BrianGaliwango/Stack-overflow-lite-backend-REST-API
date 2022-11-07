import os
from app import app as flask_app
import pytest
import psycopg2
from .sql.user_sql import user_sql


DB_HOST = "localhost"
DB_NAME = "stack_over_flow_psycopg2"
# DB_USER = os.environ["DB_USERNAME"]
# DB_PASS = os.environ["DB_PASSWORD"]


@pytest.fixture
def app(scope="class"):
    yield flask_app
    
        
@pytest.fixture 
def client(app):
  
  return app.test_client()


@pytest.fixture
def cursor():
  conn = psycopg2.connect("host=localhost dbname=stack_over_flow_psycopg2 user=postgres password=57726630")
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
   
      
  

  

  
  
  
  
  





  