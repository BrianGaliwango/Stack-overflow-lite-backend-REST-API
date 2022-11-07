
user_sql = """
insert into users (first_name, last_name, username, email, password) values (%(first_name)s, %(last_name)s, %(username)s, %(email)s, %(password)s)
"""