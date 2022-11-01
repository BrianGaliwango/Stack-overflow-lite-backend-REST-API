# # from tests.conftest import cursor, registrant1, registrant2


# # # test table exists
# # def test_table_users_exists(cursor, registrant1):
# #   cursor.execute("SELECT * FROM users")
# #   rs = cursor.fetchall()
# #   assert len(rs) == 4

# # Init db
# # DB_HOST = "localhost"
# # DB_NAME = "stack_over_flow_psycopg2"
# @pytest.fixture
# def db_user():
#     DB_USER = os.environ["DB_USERNAME"]
#     yield DB_USER
  
# @pytest.fixture
# def db_password():  
#     DB_PASS = os.environ["DB_PASSWORD"]
#     yield DB_PASS


# # db fixture
# @pytest.fixture
# def cursor(db_user, db_password):
#   conn = psycopg2.connect("host=localhost, dbname=stack_over_flow_psycopg2, user=DB_USER, password=DB_PASS")
#   cur = conn.cursor()
#   yield cur 
  

# @pytest.fixture
# def registrant1(cursor):
#     cursor.execute(registrant_sql, {
#           "first_name":"Galice", "last_name":"John",
#           "username":"galice", "email":"galice@gmail.com" ,"password":"12345"     
#     })  
  

# @pytest.fixture
# def registrant2(cursor):
#     cursor.execute(registrant_sql, {
#           "first_name":"John", 
#           "last_name":"Doe",
#           "username":"Doe", 
#           "email":"doe@gmail.com" ,"password":"12345"     
#     })  