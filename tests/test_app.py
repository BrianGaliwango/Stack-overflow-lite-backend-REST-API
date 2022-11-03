import pytest

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
    

# Testing  
def test_get_single_question(app, client):
    result = client.get("/question/3/")
    assert result.status_code == 200
    # assert b"Cascading stye sheets" in result.data
    assert b"Computer memory we can access and change data" in result.data
    

