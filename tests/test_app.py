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
    assert b'What is css in full' in result.data
    

# Testing  
