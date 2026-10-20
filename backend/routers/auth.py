from fastapi import APIRouter, HTTPException # APIRouter for the router, HTTPException for 401
from pydantic import BaseModel # shapes the JSON body
from database.connection import get_connection # our Oracle connector

router = APIRouter() # create this router

class LoginInput(BaseModel): #shape of the JSON body: email and password
    email: str
    password: str

@router.post("/login") #POST /login (will be prefixed with /api in main.py, so final URL is /api/login)
def login(data: LoginInput): #data is the JSON body shaped like LoginInput
    conn = get_connection() #open a phone line
    cursor = conn.cursor() #cursor to send SQL
    cursor.execute(
        "SELECT U.USER_ID, U.FULL_NAME, R.ROLE_NAME FROM USERS U JOIN ROLES R ON U.ROLE_ID = R.ROLE_ID WHERE U.EMAIL = :email AND U.PASSWORD_HASH = :pwd",
        {"email": data.email, "pwd": data.password} #fill the holes with what the user typed
    )
    row = cursor.fetchone() #get one row, or None
    conn.close() #hang up the phone
    if row is None: #no match means bad email or bad password
        raise HTTPException(status_code=401, detail="Invalid credentials") #send 401 Unauthorized
    return {"user_id": row[0], "full_name": row[1], "role": row[2]} #tell the browser who logged in and their role