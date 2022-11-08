# Stack-overflow-lite-backend-REST-**API**

## A fully functional question and answer backend REST API project written in flask python , css and html with postgresql as the database and can be deployed to heroku **

This project is a stack overflow lite challenge, Every part of this project is a sample code that shows how to do the following.

* Users can register an account API.
* Registered users can login into account API.
* Registered users can post questions API.
* Registered users can view all questions API.
* Registered users can view single question with all its answers API
* Registered user can edit and delete questions API's.
* Registered users can post an answer to a questions API.
* Registered users can upvote and downvote answers API.
* Registered users can mark answers suitable for their question API's.
* Registered users can edit and delete answers and questions API's.
* Registered users can post comments to answers API.
* Registered users can delete and edit comments API's
* Registered users profile pages viewing all current user questions and answers
* Unregistered users home page can view questions.
* Unregistered user home page can view single question with all its answers API's
* Data is saved to postgres database.

## How to setup the project**

1. Clone this project
2. Open it in vscode or any other editor
3. Activate the virtual environment
4. Pip install flask , functools and werkzeug
5. Pip install psycopg2 for the database
6. Pip install gunicorn
7. Change names of the project and create a repository on github
8. Push all new changes to github
9. Start heroku CL.
10. Heroku login.
11. Login into your account.
12. Create a new app on heroku
13. Create a postgresql free hobby database on heroku
14. Check for database url and put it in an environment variable to hide it
15. Use the database environment variable name in the app (DATABASE_URL = "ENVIRONMENT VARIABLE") to communicate with the heroku database
16. Git push to heroku main
17. Create tables on heroku database
18. Heroku run python
19. From init_db import create_tables.
20. Call the create_tables() func and tables will be created in the database
21. Git add all and git commit all changes
22. Git push to github
23. git push to heroku main
24. After app has bn deployed open it and enjoy.
  
**Find a bug?**
If you found an issue or would like to submit an improvement to this project, please issue using the issues tab above.if you would like to submit a PR with a fix, reference the issue created!

**Known issues (Work in progress)**
This project is ongoing and will be getting updated soon.
Pytest will be included in the next release.
