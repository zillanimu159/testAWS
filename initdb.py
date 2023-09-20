# Add the necessary imports
import mysql.connector as mysql
import os
import datetime
from dotenv import load_dotenv
import bcrypt

# Read Database connection variables
load_dotenv(os.path.dirname(__file__) + "/credentials.env")

db_host = os.environ['MYSQL_HOST']
db_user = os.environ['MYSQL_USER']
db_pass = os.environ['MYSQL_PASSWORD']


# Connect to the db and create a cursor object
db =mysql.connect(user=db_user, password=db_pass, host=db_host)
cursor = db.cursor()


cursor.execute("create database if not exists hostingtime;")
cursor.execute("use hostingtime;")
cursor.execute("drop table if exists users;")
cursor.execute("drop table if exists sessions;")
cursor.execute("drop table if exists files;")
##############################################################################
try:
   cursor.execute("""
   create table if not exists users (
      id         integer auto_increment primary key,
      first_name varchar(64) not null,
      last_name  varchar(64) not null,
      email      varchar(64) not null unique,
      username   varchar(64) not null unique,
      password   varchar(64) not null,
      created_at timestamp not null default current_timestamp
   );
 """)
except RuntimeError as err:
   print("runtime error: {0}".format(err))

try:
   cursor.execute("""
   create table if not exists sessions (
      session_id varchar(64) primary key,
      session_data json not null,
      created_at timestamp not null default current_timestamp
   );
 """)
except RuntimeError as err:
   print("runtime error: {0}".format(err))

try:
   cursor.execute("""
   create table if not exists files (
      id integer auto_increment primary key,
      user_id integer not null,
      filepath varchar(1000) not null,
      created_at timestamp not null default current_timestamp
   );
 """)
except RuntimeError as err:
   print("runtime error: {0}".format(err))

# Collection of users with plain-text passwords – BIG NONO! NEVER EVER DO THIS!!!
"""users = [
  {'first_name':'Zendaya', 'last_name':'',          'student_id': '00000000', 'email': 'a@wow.com',   'username': 'ZD123',   'password': 'abc123'},
  {'first_name':'Tom',     'last_name':'Holland',   'student_id': '00000001', 'email': 'a@epic.com',  'username': 'tommy',   'password': 'abc123'},
  {'first_name':'Tobey',   'last_name':'Maguire',   'student_id': '00000002', 'email': 'a@crazy.com',   'username': 'tobes',   'password': 'abc123'},
  {'first_name':'Andrew',  'last_name':'Garfield',  'student_id': '00000003', 'email': 'a@impossible.com',   'username': 'drewie',  'password': 'abc123'},
  {'first_name':'Rick',    'last_name':'Gessner',   'student_id': '00000004', 'email': 'a@now.com',   'username': 'rickg',   'password': 'drowssap'},
  {'first_name':'Ramsin',  'last_name':'Khoshabeh', 'student_id': '00000005', 'email': 'a@die.com',   'username': 'ramujin', 'password': 'password'}
]
"""


# Commit the changes and close the connection
db.commit()
cursor.close()
db.close()

print('Initialized.')
