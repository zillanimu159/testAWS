''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Necessary Imports
import mysql.connector as mysql                   # Used for interacting with the MySQL database
import os                                         # Used for interacting with the system environment
from dotenv import load_dotenv                    # Used to read the credentials
import bcrypt

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Configuration
load_dotenv(os.path.dirname(__file__) + '/credentials.env')   # Read in the environment variables for MySQL
db_config = {
  "host": os.environ['MYSQL_HOST'],
  "user": os.environ['MYSQL_USER'],
  "password": os.environ['MYSQL_PASSWORD'],
  "database": os.environ['MYSQL_DATABASE']
}
session_config = {
  'session_key': os.environ['SESSION_KEY']
}

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Define helper functions for CRUD operations
# CREATE SQL query
def add_file(user_id, filePath) -> int:
  db = mysql.connect(**db_config)
  cursor = db.cursor()
  query = "insert into files (user_id, filepath) values (%s, %s)"
  values = (user_id, filePath)
  cursor.execute(query, values)
  db.commit()
  db.close()
  return cursor.lastrowid

# SELECT SQL query
def select_files(user_id:int=None) -> list:
  db = mysql.connect(**db_config)
  cursor = db.cursor()
  if user_id == None:
    query = "select id, user_id, filepath from files;"
    cursor.execute(query)
    result = cursor.fetchall()
  else:
    query = f"select id, user_id, filepath from files where id={user_id};"
    cursor.execute(query)
    result = cursor.fetchone()
  db.close()
  return result

# UPDATE SQL query
def update_file(file_id:int, file_path:str) -> bool:
  db = mysql.connect(**db_config)
  cursor = db.cursor()
  query = "update files set filepath=%s where id=%s;"
  values = (file_path, file_id)
  cursor.execute(query, values)
  db.commit()
  db.close()
  return True if cursor.rowcount == 1 else False

# DELETE SQL query
def delete_file(file_id:int) -> bool:
  db = mysql.connect(**db_config)
  cursor = db.cursor()
  cursor.execute(f"delete from files where id={file_id};")
  db.commit()
  db.close()
  return True if cursor.rowcount == 1 else False

