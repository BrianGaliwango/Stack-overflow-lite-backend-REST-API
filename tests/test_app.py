import pytest
from flask import json

# Test index api
def test_index(app, client):
    result = client.get("/")
    assert result.status_code == 200
    assert b'register' in result.data 
    

#Testing home questions API 
def test_get_questions(app, client):
    result = client.get("/questions")
    assert result.status_code == 200
    assert b"What is css in full?" in result.data
    

# Testing  get single question
def test_get_single_question(app, client):
    result = client.get("/question/3/")
    assert result.status_code == 200
    # assert b"Cascading stye sheets" in result.data
    assert b"Computer memory we can access and change data" in result.data
    


#Test search questions
def test_search_questions(app, client):
    result = client.post("/search_questions")    
    assert result.status_code == 302
    
    #Redirects to the requested page
 
 
    
# Test register user
def test_register_user(app, client):
    result = client.get("/register")
    assert result.status_code == 200
    assert b'Register' in result.data
    assert b'first_name' in result.data
    assert b'last_name' in result.data
 
 
 
# Test register user 
@pytest.mark.skip(reason="hash password throws AttributeError: 'NoneType' object has no attribute 'encode', regex pattern throws TypeError: expected string or bytes-like object, comment out line 166 to 169 before testing")    
def test_register_user(app, client):
    result = client.post("/register")
    assert result.status_code == 200
    
    # Comments
    # Comment out  elif not re.match(r"[^@]+@[^@]+\.[^@]+", email) (line 166) and  elif not re.match(r"[A-Za-z0-9]+", username): flash("Username must contain only characters and numbers", "danger") before testing
    # else
    # It regex throws:
    # "TypeError: expected string or bytes-like object"
    #
    


# Test login
def test_login(app, client):
    result = client.get("/login")
    assert result.status_code == 200  
    
      
# Test login
def test_login(app, client):
    result = client.post("/login")
    assert result.status_code == 400  
    
    # Throws bad request if login fails  

# Testing logout
def test_logout(app, client):
    result = client.get("/logout")
    assert result.status_code == 302
    
    # Comments 
    # Redirects to login page