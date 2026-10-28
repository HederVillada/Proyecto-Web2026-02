from fastapi import APIRouter, HTTPException # APIRouter for the router, HTTPException for 401
from pydantic import BaseModel # shapes the JSON body
from database.connection import get_connection # our Oracle connector
from password_utils import verify_password #aqui importamos el HASH de las contraseñas, importante

router = APIRouter() # create this router

class LoginInput(BaseModel): #shape of the JSON body: email and password
    email: str
    password: str

@router.post("/login")
def login(data: LoginInput):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT U.USER_ID, U.FULL_NAME, R.ROLE_NAME, U.PASSWORD_HASH 
                FROM USERS U
                JOIN ROLES R ON U.ROLE_ID = R.ROLE_ID
                WHERE U.EMAIL = :email
                """,
                {"email": data.email} # en mi codigo viejo, se buscaba EMAIL y PASSWORD. Ahora el password es hash
                #pro como el email no es hash, entonces los mantenemos separaditos y bonitos
                #We need U.PASSWORD_HASH because verify_password() needs the stored hash to check the password the user inputted.
                

            )
            row = cursor.fetchone()
        finally:
            cursor.close() #yo encontre este 'finally', segúnchis, es basicamente lo que hacia en OTRAS partes, pero esta tiene
            #menos capacidad de tener un error donde se cierra antes de tener que cerrarse, y se queda colgado
            #honestamente, esto a mi JAMAS me ha pasado en TODOS mis intentos durante TODAS estas semanas
            #pero lo tengo aqui porque mas seguridad que no sea tediosa no hace daño a nadie. 
            # de todas formas, me da pereza reemplazar todo, así que como yo ahora estoy reemplazando esto, lo uso. 
            #Si luego necesito escalar mi projecto, naturalmente, utilizare finally
            #pero por ahora no
    finally:
        conn.close()
    if row is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials" #credenciales invalidas si no sale ninngun usuario
            
        )
    user_id, full_name, role, stored_hash = row
    if not stored_hash or not verify_password(data.password, stored_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials" #credenciales invalidas si no esta el hash correcto tampoco
        )
    return {
        "user_id": user_id,
        "full_name": full_name,
        "role": role
    }