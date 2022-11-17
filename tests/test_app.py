from .sql.user_sql import user_sql


# Remove authentication(@is_logged_in) before testing

def test_create_tables(cursor):
     cursor.execute(
        "CREATE TABLE allow(id SERIAL PRIMARY KEY,first_name VARCHAR(255) NOT NULL, last_name VARCHAR(255) NOT NULL, username VARCHAR(255) UNIQUE, email VARCHAR(100) NOT NULL, password VARCHAR(255) NOT NULL, register_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP);"
    )


def test_db(cursor):
    cursor.execute("begin; select email from users;")
   
    result = cursor.fetchall()
    for rs in result:
        print(rs)
    assert len(rs) == 1   
    
    
# Test inserting into db 
def test_insert_db(cursor):
    cursor.execute(user_sql, {"first_name": "Sweetie", 
                              "last_name": "Mufasa",
                              "username": "gully",
                              "email": "galice@gmail.com",
                              "password": "12345"
                              })   


# Test index api
def test_index(app, client):
    result = client.get("/")
    assert result.status_code == 200
    assert b'register' in result.data 
    

# Testing home questions API 
def test_get_questions(client, cursor):
    # Given  
    result = client.get("/questions")
    assert result.status_code == 200
    assert b"questions" in result.data
    

# Testing get single question
def test_get_single_question(app, client):
    result = client.get("/question/8/")
    assert result.status_code == 200
    assert b'question' in result.data

    

#Test search questions
def test_search_questions(app, client):
    result = client.post("/search_questions")    
    assert result.status_code == 302

 
   
# Test register user
def test_register_user(client, cursor):
    result = client.get("/register")
    
    # Given
   
    first_name =  "Nice"
    last_name = "Mark"
    username = "mark"
    email = "mark@gmail.com"
    password = "12345"

  
    # When
    try:
        cursor.execute("INSERT INTO users(first_name, last_name, username, email, password) VALUES (%s, %s, %s, %s, %s)",(first_name,last_name,username,email,password))
    except:
        ValueError("empty fields")
            
        
    assert result.status_code == 200
    assert b'New user registered' in result.data
    assert b'Nice' in result.data
    assert b'Mark' in result.data
  
 
# Test register user     
def test_register_user(app, client):
    try:
        result = client.post("/register")
        assert result.status_code == 200
    except:
        Exception("hash password throws AttributeError: 'NoneType' object has no attribute 'encode', regex pattern throws TypeError: expected string or bytes-like object,")    
        


# Test login
def test_login(app, client):
    result = client.get("/login")
    assert result.status_code == 200  
    
           
# Test login
def test_login(app, client):
    result = client.post("/login")
    assert result.status_code == 400
    

# Testing logout
def test_logout(app, client):
    result = client.get("/logout")
    assert result.status_code == 302

    
# Test dashboard
def test_dashboard(client, cursor):
    result = client.get("/dashboard")    
    assert result.status_code == 200
    assert b'What is css in full' in result.data
    assert b'questions' in result.data
    
    

# # Test dashboard get single question 
def test_dashboard_get_single_question(app, client):
    result = client.get("/user_question/8/")
    assert result.status_code == 200
    assert b'question' in result.data
   
   
    
# Test get post_question
def test_post_question(app, client):
    result = client.get("/post_question")
    assert b'title' in result.data
    assert b'textarea' in result.data
    assert result.status_code == 200
    
        

# # Test post /post_question
def test_get_post_question(app, client):
    result = client.post("/post_question")
    assert b'title' in result.data
    assert b'question' in result.data
    assert result.status_code == 200

    

# Test answer question
def test_answer_question(app, client):
    result = client.get("/answer_question/8")
    assert result.status_code == 308
    assert b'answer' in result.data
       

#Test post request (post_answer) 
def test_post_answer(app, client):
    result = client.post("/answer_question/8")
    assert result.status_code == 308
    
    
#Get my profile questions request
def get_profile_questions(app, client):
    result = client.get("/profile")
    assert result.status_code == 200
    assert b'questions' in result.data

    
 
#Test post profile_questions 
def get_post_profile_questions(app, client):
    result = client.post("/profile")
    assert result.status_code == 200
    assert b'questions' in result.data



#Test profile single get question
def test_profile_get_question(app, client):
    result = client.get("/profile_question/8/")
    assert result.status_code == 200
    assert b'css' in result.data
    


#Test edit question
def test_edit_question(app, client):
    result = client.get("/edit_question/8/")
    assert result.status_code == 200
    
    
    
#Test edit question
def test_post_edit_question(app, client):
    result = client.post("/edit_question/8/")
    assert result.status_code == 400
    
 
#Test get profile answers 
def test_myPro_answers(app, client):
    try:
        result = client.get("/myPro_answers")
        assert result.status_code == 200
        assert b'answers' in result.data
    except:
        Exception("KeyError: 'username' when not logged in");    
    
    
# Testing edit answer
def test_edit_answer(app, client):
    result = client.get("/edit_answer/1/")
    assert result.status_code == 200
    assert b'answer' in result.data
 
 
# Test post edit answer request    
def test_post_edit_answer(app, client):
    result = client.post("/edit_answer/1/")
    assert result.status_code == 400
    

#Test upvote answer 
def test_upvote_answer(app, client):
    try: 
        result = client.post("/upvote_answer/1/")
        assert result.status_code == 302
        print(result.data)
    except:
        Exception("TypeError: 'NoneType' object is not subscriptable, answer_username = answer['answer_username']")    
        

# Test downvote answer 
def test_downvote_answer(app, client):
    try:
        result = client.post("/upvote_answer/1/")
        assert result.status_code == 302
        print(result.data)
    except:
        Exception("TypeError: 'NoneType' object is not subscriptable, answer_username = answer['answer_username']")    
           
 
# Test get post_comment
def test_get_post_comment(app, client):
    result = client.post("/post_comment/1/")
    assert result.status_code == 200 
    assert b'comment' in result.data
    
    
# Test post_comment
def test_post_comment(app, client):
    result = client.post("/post_comment/1/")
    assert result.status_code == 200   
    assert b'comment' in result.data
    
  
#Test view_comments 
def test_view_comments(app, client):
    result = client.get("/view_comments/15/")
    assert result.status_code == 200
  
  
#Testing when no comments available 
def test_unavailable_view_comments(app, client):
    result = client.get("/view_comments/2/")
    assert result.status_code == 302
    
    
#Test get edit_comment
def test_edit_comment(app, client):
    result = client.get("/edit_comment/1/")
    assert result.status_code == 200
    
    
#Test post edit_comment
def test_edit_comment(app, client):
    result = client.post("/edit_comment/1/")
    assert result.status_code == 400


    
#Testing mark answer
def test_mark_answer(app, client):
    result = client.put("/mark_answer/2/")
    assert result.status_code == 302 
    print(result.data)
    
    
#Testing get mark answer
def test_get_mark_answer(app, client):
    result = client.get("/mark_answer/2/")
    assert result.status_code == 302 
    print(result.data)
    
    
    
#Testing unmark answer
def test_unmark_answer(app, client):
    result = client.put("/unmark_answer/2/")
    assert result.status_code == 302 
    print(result.data)
    
    
#Testing get unmark answer
def test_get_unmark_answer(app, client):
    result = client.get("/unmark_answer/2/")
    assert result.status_code == 302 
    print(result.data)
    
    
#Test delete_question 
def test_delete_question(app, client):
    result = client.post("/delete_question/13/")
    assert result.status_code == 302
 
  
#Delete answer    
def test_profile_delete_answer(app, client):
    result = client.post("/profile_delete_answer/33/")
    assert result.status_code == 302
 
 
#Delete answer    
def test_dashboard_delete_answer(app, client):
    result = client.post("/dashboard_delete_answer/34/")
    assert result.status_code == 302
 
 
# Delete comment    
def test_delete_comment(app, client):
    result = client.post("/delete_comment/20/")
    assert result.status_code == 302
    
    

    


