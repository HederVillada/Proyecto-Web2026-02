from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from database.connection import get_connection
import datetime

router = APIRouter()

# Security Guard
def verify_admin_role(x_user_role: str = Header(default="student")):
    if x_user_role.lower() != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado: Solo administradores pueden prestar equipos.")

class LoanInput(BaseModel):
    user_id: int
    equipment_id: int

@router.post("", status_code=201, dependencies=[Depends(verify_admin_role)])
def create_loan(data: LoanInput):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # 1. Check if equipment is available
        cursor.execute("SELECT STATUS FROM EQUIPMENT WHERE EQUIPMENT_ID = :eid", {"eid": data.equipment_id})
        eq = cursor.fetchone()
        if not eq or eq[0] != 'AVAILABLE':
            conn.close()
            raise HTTPException(status_code=400, detail="El equipo no existe o ya está prestado")

        print(f"--- CREANDO PRESTAMO ---")
        print(f"User ID: {data.user_id} | Equipment ID: {data.equipment_id}")

        # Calcular fechas en Python para evitar errores de Oracle
        hoy = datetime.datetime.now()
        fin = hoy + datetime.timedelta(days=7)

        # 2. Create the Reservation (Usando nombres largos para evitar ORA-01745)
        cursor.execute(
            """
            INSERT INTO RESERVATIONS (RESERVATION_ID, USER_ID, REQUEST_DATE, START_DATE, END_DATE, STATUS) 
            VALUES (RESERVATIONS_SEQ.NEXTVAL, :user_val, :req_date, :start_date, :end_date, 'APPROVED')
            """,
            {
                "user_val": data.user_id, 
                "req_date": hoy, 
                "start_date": hoy, 
                "end_date": fin
            }
        )
        
        # 3. Get the ID of the reservation we just created
        cursor.execute("SELECT MAX(RESERVATION_ID) FROM RESERVATIONS WHERE USER_ID = :user_val", {"user_val": data.user_id})
        res_id = cursor.fetchone()[0]
        
        # 4. Create the Details
        cursor.execute(
            """
            INSERT INTO RESERVATION_DETAILS (DETAIL_ID, RESERVATION_ID, EQUIPMENT_ID, NOTES) 
            VALUES (DETAILS_SEQ.NEXTVAL, :res_val, :equip_val, 'Préstamo web')
            """,
            {"res_val": res_id, "equip_val": data.equipment_id}
        )
        
        # 5. Update the equipment status
        cursor.execute("UPDATE EQUIPMENT SET STATUS = 'LOANED' WHERE EQUIPMENT_ID = :eid", {"eid": data.equipment_id})
        
        conn.commit()
    except HTTPException:
        raise
    except Exception as e:
        print("!!! ERROR EN ORACLE:", str(e))
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))
    conn.close()
    return {"message": "Préstamo registrado exitosamente"}

@router.put("/return/{equipment_id}", dependencies=[Depends(verify_admin_role)])
def return_equipment(equipment_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # 1. Find the active reservation for this equipment
        cursor.execute("""
            SELECT R.RESERVATION_ID 
            FROM RESERVATIONS R
            JOIN RESERVATION_DETAILS RD ON R.RESERVATION_ID = RD.RESERVATION_ID
            WHERE RD.EQUIPMENT_ID = :eid AND R.STATUS = 'APPROVED'
        """, {"eid": equipment_id})
        row = cursor.fetchone()
        
        if row:
            res_id = row[0]
            # 2. Mark the reservation as RETURNED
            cursor.execute("UPDATE RESERVATIONS SET STATUS = 'RETURNED' WHERE RESERVATION_ID = :rid", {"rid": res_id})

        # 3. Set the equipment back to AVAILABLE
        cursor.execute("UPDATE EQUIPMENT SET STATUS = 'AVAILABLE' WHERE EQUIPMENT_ID = :eid", {"eid": equipment_id})
        
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))
    conn.close()
    return {"message": "Equipo devuelto exitosamente"}

@router.get("/report")
def loan_report():
    conn = get_connection()
    cursor = conn.cursor()
    # FIX: Only show ACTIVE loans (APPROVED), so returned items disappear from the active list.
    cursor.execute("""
        SELECT U.FULL_NAME, E.NAME, E.SERIAL_NO, R.STATUS, R.START_DATE
        FROM RESERVATIONS R
        JOIN USERS U ON R.USER_ID = U.USER_ID
        JOIN RESERVATION_DETAILS RD ON R.RESERVATION_ID = RD.RESERVATION_ID
        JOIN EQUIPMENT E ON RD.EQUIPMENT_ID = E.EQUIPMENT_ID
        WHERE R.STATUS = 'APPROVED'
    """)
    rows = cursor.fetchall()
    conn.close()
    return [{"user": r[0], "equipment": r[1], "serial": r[2], "status": r[3], "date": str(r[4])} for r in rows]