from app import app as flask_app
import pytest
from flask import json
from app import questions

@pytest.fixture
def app():
  yield flask_app
  
@pytest.fixture
def client(app):
  return app.test_client() 

# Test for success
def test_index(app, client):
  result = client.get("/")
  assert result.status_code == 200
  assert {"Hello": "Galice"} == json.loads(result.get_data(as_text=True))
 
#Test home get questions route
def test_questions(app, client):
  result = client.get("/questions") 
  assert result.status_code == 200
  assert {'questions': [[4, 'doe', 'Javascript', 'What year was js launched?', 'Wed, 26 Oct 2022 10:57:24 GMT'], [3, 'doe', 'Heap', 'What is a heap?\r\n', 'Wed, 26 Oct 2022 10:55:11 GMT'], [1, 'galice', 'CSS', 'What is css in full?\r\n', 'Wed, 26 Oct 2022 10:50:37 GMT']]} == json.loads(result.get_data(as_text=True))
  
#Test failure foe questions
def test_questions(app, client):
  result = client.get("/questions") 
  assert result.status_code == 200
  assert {'questions': [[4, 'doe', 'Javascript', 'What year was js launched?', 'Wed, 26 Oct 2022 10:57:24 GMT'], [3, 'doe', 'Heap', 'What is a heap?\r\n', 'Wed, 26 Oct 2022 10:55:11 GMT']]} == json.loads(result.get_data(as_text=True))
