# Necessary Imports
from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect                  # The main FastAPI import
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse    # Used for returning HTML and JSON responses
from fastapi.staticfiles import StaticFiles   # Used for serving static files
import mysql.connector as mysql
from dotenv import load_dotenv
import uvicorn                                # Used for running the app
import userEntry as db                              # Import helper module of database functions!
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates    # Used for generating HTML from templatized files
import os                                         # Used for interacting with the system environment
from sessions import Sessions
from multiprocessing import Process

#Website Configuration
load_dotenv(os.path.dirname(__file__) + '/credentials.env')                 # Read in the environment variables for MySQL
db_host = os.environ['MYSQL_HOST']
db_user = os.environ['MYSQL_USER']
db_pass = os.environ['MYSQL_PASSWORD']
db_name = os.environ['MYSQL_DATABASE']
# session_manager = SessionManager(secret_key="mysecretkey")
# Use MySQL for storing session data
sessions = Sessions(db.db_config, secret_key=db.session_config['session_key'], expiry=3600)
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
def authenticate_user(username:str, password:str) -> bool:
  return db.check_user_password(username, password)

public = Jinja2Templates(directory= os.path.dirname(__file__) + '/public')        # Specify where the HTML files are located
views = Jinja2Templates(directory= os.path.dirname(__file__) + '/views')        # Specify where the HTML files are located

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Define a User class that matches the SQL schema we defined for our users
class User(BaseModel):
  first_name: str
  last_name: str
  email: str
  username: str
  password: str

class Visitor(BaseModel):
  username: str
  password: str

class PasswordForgetter(BaseModel):
  email: str
  password: str

# Define a User class that matches the SQL schema we defined for our users
class RewriteUser(BaseModel): # TODO use different unique identifier for password reset
  current_password: str
  first_name: str = ""
  last_name: str = ""
  email: str = ""
  username: str = ""
  password: str = ""


app = FastAPI()                   # Specify the "app" that will run the routing
# Mount the static directory
app.mount("/public", StaticFiles(directory=os.path.dirname(__file__) + "/public"), name="public")


#########################################################################
################                Content         #########################
#########################################################################
# Example route: return a static HTML page
@app.get("/", response_class=HTMLResponse)
def get_html() -> HTMLResponse:
    with open(os.path.dirname(__file__) + "/views/home.html") as html:
        return HTMLResponse(content=html.read())    

#######################################
###       Need to be Logged in      ###
#######################################

# Example route: return a HTML page
@app.get("/profile", response_class=HTMLResponse)
def get_html(request:Request) -> HTMLResponse:
    session = sessions.get_session(request)
    if len(session) > 0 and session.get('logged_in'):
        session_id = request.cookies.get("session_id")
        template_data = {'request':request, 'session':session, 'session_id':session_id}
        return views.TemplateResponse('profile.html', template_data)
    else:
        return RedirectResponse(url="/login", status_code=302)

# Example route: return a HTML page
@app.get("/upload", response_class=HTMLResponse)
def get_html(request:Request) -> HTMLResponse:
    session = sessions.get_session(request)
    if len(session) > 0 and session.get('logged_in'):
        session_id = request.cookies.get("session_id")
        template_data = {'request':request, 'session':session, 'session_id':session_id}
        return views.TemplateResponse('upload.html', template_data)
    else:
        return RedirectResponse(url="/log   in", status_code=302)

######################################################################
#################      Account and Sessions      #####################
######################################################################

#######################################
##########       Register      ########
#######################################
# Example route: return a HTML page
@app.get("/register", response_class=HTMLResponse)
def get_html() -> HTMLResponse:
    with open(os.path.dirname(__file__) +"/views/register.html") as html:
        return HTMLResponse(content=html.read())

#Creates new user then logs them in
@app.post('/register')
def post_register(user:User, request:Request, response:Response) -> dict:
  username = user.username
  password = user.password
  # Invalidate previous session if logged in
  session = sessions.get_session(request)
  if len(session) > 0:
    sessions.end_session(request, response)

  db.create_user(user.first_name, user.last_name, user.email, user.username,user.password)
  # Authenticate the user
  if authenticate_user(username, password):
    session_data = {'username': username, 'logged_in': True}
    session_id = sessions.create_session(response, session_data)
    return {'message': 'Login successful', 'session_id': session_id}
  else:
    return {'message': 'Invalid username or password', 'session_id': 0}


#######################################
##########       Login      ###########
#######################################

# Example route: return a HTML page
@app.get("/login", response_class=HTMLResponse)
def get_login(request:Request) -> HTMLResponse:
    session = sessions.get_session(request)
    if len(session) > 0 and session.get('logged_in'):
        return RedirectResponse(url="/jacket", status_code=302)
    else:
      with open(os.path.dirname(__file__) +"/views/login.html") as html:
        return HTMLResponse(content=html.read())

#Creates new session for logged in user
@app.post('/login')
def post_login(visitor:Visitor, request:Request, response:Response) -> dict:
  username = visitor.username
  password = visitor.password
  # Invalidate previous session if logged in
  session = sessions.get_session(request)
  if len(session) > 0:
    sessions.end_session(request, response)

  # Authenticate the user
  if authenticate_user(username, password):
    session_data = {'username': username, 'logged_in': True}
    session_id = sessions.create_session(response, session_data)
    return {'message': 'Login successful', 'session_id': session_id}
  else:
    return {'message': 'Invalid username or password', 'session_id': 0}

#######################################
######    Change Profile Data    ######
#######################################

@app.post('/profile')
def post_profile(user:RewriteUser, request:Request, response:Response) -> dict:
  current_password = user.current_password
  newFirst = user.first_name  
  newLast = user.last_name
  newEmail = user.email
  newUsername = user.username
  newPassword = user.password
  if (db.update_user_with_password(current_password, newFirst, newLast, newEmail, newUsername, newPassword)):
    return {'message': 'Data change successful!', 'changed' : True}
  else:
    return {'message': 'Invalid password or same data as before...', 'changed' : False}
  
@app.get('/forgotPassword')
def get_forgor(request:Request) -> HTMLResponse:
  with open(os.path.dirname(__file__) +"/views/forgotPassword.html") as html:
        return HTMLResponse(content=html.read())

  
@app.post('/forgotPassword')
def post_forgor(visitor:PasswordForgetter, request:Request, response:Response) -> dict:
  email = visitor.email
  newPassword = visitor.password
  if (db.update_user_password(email,newPassword)):
    return {'message': 'Password change successful', 'changed' : True}
  else:
    return {'message': 'Invalid email or password', 'changed' : False}
  
@app.post('/uploadFile')
def post_file(request:Request, response:Response) -> dict:
  fix this
  if (db.update_user_password(email,newPassword)): 
    return {'message': 'Your file made it :D', 'changed' : True}
  else:
    return {'message': 'Invalid email or password', 'changed' : False}
  
#######################################
##########       Logout      ##########
#######################################

@app.post('/logout')
def post_logout(request:Request, response:Response) -> dict:
  sessions.end_session(request, response)
  return {'message': 'Logout successful', 'session_id': 0}

######################################################################
#################      Debugging              #####################
######################################################################

@app.get('/protected')
def get_protected(request:Request) -> dict:
  session = sessions.get_session(request)
  if len(session) > 0 and session.get('logged_in'):
    return {'message': 'Access granted'}
  else:
    return {'message': 'Access denied'}

# GET /sessions
@app.get('/sessions')
def get_sessions(request:Request) -> dict:
  return sessions.get_session(request)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6543)