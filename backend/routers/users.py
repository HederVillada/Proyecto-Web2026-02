from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from database.connection import get_connection

router = APIRouter()

# Security Guard
def verify_admin_role(x_user_role: str = Header(default="student")):
    if x_user_role.lower() != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado: Solo administradores.")

class UserInput(BaseModel):
    full_name: str
    email: str
    password_hash: str
    role_id: int

@router.post("", status_code=201, dependencies=[Depends(verify_admin_role)])
def create_user(data: UserInput):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO USERS (USER_ID, FULL_NAME, EMAIL, PASSWORD_HASH, ROLE_ID) 
            VALUES (USERS_SEQ.NEXTVAL, :name, :email, :pwd, :role)
            """,
            {"name": data.full_name, "email": data.email, "pwd": data.password_hash, "role": data.role_id}
        )
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))
    conn.close()
    return {"message": "Usuario creado correctamente"}

@router.get("")
def list_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT USER_ID, FULL_NAME, EMAIL, ROLE_ID FROM USERS ORDER BY USER_ID")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "email": r[2], "role_id": r[3]} for r in rows]

@router.put("/{user_id}", dependencies=[Depends(verify_admin_role)])
def update_user(user_id: int, data: UserInput):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE USERS SET FULL_NAME = :name, EMAIL = :email, PASSWORD_HASH = :pwd, ROLE_ID = :role 
            WHERE USER_ID = :id
            """,
            {"name": data.full_name, "email": data.email, "pwd": data.password_hash, "role": data.role_id, "id": user_id}
        )
        if cursor.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        conn.commit()
    except HTTPException:
        raise
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))
    conn.close()
    return {"message": "Usuario actualizado"}

@router.delete("/{user_id}", dependencies=[Depends(verify_admin_role)])
def delete_user(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM USERS WHERE USER_ID = :id", {"id": user_id})
        if cursor.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        conn.commit()
    except HTTPException:
        raise
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))
    conn.close()
    return {"message": "Usuario eliminado"}