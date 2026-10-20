from fastapi import APIRouter, HTTPException, Depends, Header # APIRouter es como un mini-FastAPI para separar módulos; Depends maneja inyección y Header lee las cabeceras HTTP
from pydantic import BaseModel # BaseModel nos ayuda a definir y validar la forma exacta del JSON que entra
from database.connection import get_connection # Importamos la función para conectarnos a la base de datos Oracle

router = APIRouter() # Creamos el router para agrupar todas las rutas de equipos aquí

class EquipmentInput(BaseModel): # Esta clase define qué campos esperamos recibir en el JSON cuando alguien crea o actualiza un equipo
    serial_no: str # El número de serie del equipo (obligatorio)
    name: str # El nombre descriptivo del equipo (obligatorio)
    category_id: int # El ID de la categoría (por ejemplo, 1 para 3D, 2 para VR)
    status: str = "AVAILABLE" # El estado del equipo, por defecto arranca como disponible ("AVAILABLE")

# Esta función de validación actúa como un guardia de seguridad en el backend:
# Lee la cabecera HTTP 'x-user-role' que envía el frontend para verificar si el usuario es administrador.
def verify_admin_role(x_user_role: str = Header(default="student")):
    # Convertimos a minúsculas para que no importe si llega como 'Admin', 'ADMIN' o 'admin'
    if x_user_role.lower() != "admin": # Si no dice admin, le bloqueamos el paso inmediatamente con un error 403 Prohibido
        raise HTTPException(
            status_code=403, 
            detail="Acceso denegado: Se requieren privilegios de administrador para alterar datos."
        )

@router.get("") # Endpoint tipo GET para obtener la lista de TODO el inventario de equipos (disponible para todos los roles)
def list_equipment():
    conn = get_connection() # Abrimos la conexión con Oracle
    cursor = conn.cursor() # Creamos el cursor para ejecutar las consultas SQL
    cursor.execute("SELECT EQUIPMENT_ID, SERIAL_NO, NAME, CATEGORY_ID, STATUS FROM EQUIPMENT") # Pedimos ID, serie, nombre, categoría y estado de la tabla
    rows = cursor.fetchall() # Guardamos todas las filas devueltas por la base de datos
    conn.close() # Cerramos la conexión para no gastar recursos
    # Transformamos las tuplas crudas de Oracle en una lista de diccionarios limpios en formato JSON para el frontend
    return [{"id": r[0], "serial_no": r[1], "name": r[2], "category_id": r[3], "status": r[4]} for r in rows]

@router.get("/{equipment_id}") # Endpoint tipo GET para buscar un solo equipo específico usando su ID único en la URL
def get_equipment(equipment_id: int):
    conn = get_connection() # Abrimos conexión
    cursor = conn.cursor() # Creamos cursor
    # Ejecutamos la consulta buscando por el ID que nos pasó el usuario de manera segura usando parámetros (:id) para evitar inyecciones SQL
    cursor.execute(
        "SELECT EQUIPMENT_ID, SERIAL_NO, NAME, CATEGORY_ID, STATUS FROM EQUIPMENT WHERE EQUIPMENT_ID = :id",
        {"id": equipment_id}
    )
    row = cursor.fetchone() # Buscamos una sola coincidencia
    conn.close() # Cerramos conexión
    if row is None: # Si el equipo no existe en la base de datos, lanzamos un error 404 clásico
        raise HTTPException(status_code=404, detail="Equipment not found")
    # Devolvemos el diccionario con los datos del equipo encontrado
    return {"id": row[0], "serial_no": row[1], "name": row[2], "category_id": row[3], "status": row[4]}

@router.post("", status_code=201, dependencies=[Depends(verify_admin_role)]) # POST crea nuevo equipo; 'dependencies' ejecuta verify_admin_role antes de dejar pasar a nadie que no sea Admin
def create_equipment(data: EquipmentInput):
    conn = get_connection() # Conexión a Oracle
    cursor = conn.cursor() # Cursor listo
    try:
        # Insertamos el nuevo equipo usando una secuencia de Oracle (EQUIPMENT_SEQ.NEXTVAL) para autoincrementar el ID automáticamente
        cursor.execute(
            "INSERT INTO EQUIPMENT (EQUIPMENT_ID, SERIAL_NO, NAME, CATEGORY_ID, STATUS) VALUES (EQUIPMENT_SEQ.NEXTVAL, :serial, :name, :cat, :status)",
            {"serial": data.serial_no, "name": data.name, "cat": data.category_id, "status": data.status}
        )
        conn.commit() # Guardamos los cambios permanentemente en la base de datos
    except Exception as e:
        conn.close() # Cerramos si algo falla
        raise HTTPException(status_code=400, detail=str(e)) # Si Oracle se queja de algo, devolvemos un error 400 con los detalles
    conn.close() # Cerramos la conexión con éxito
    return {"message": "Equipment created"} # Mensaje de confirmación de que se creó el registro

@router.put("/{equipment_id}", dependencies=[Depends(verify_admin_role)]) # PUT actualiza un equipo existente; protegido también para que solo el Admin pueda tocarlo
def update_equipment(equipment_id: int, data: EquipmentInput):
    conn = get_connection() # Conectamos
    cursor = conn.cursor() # Cursor
    try:
        # Actualizamos los campos del equipo que coincidan con el ID proporcionado en la URL
        cursor.execute(
            "UPDATE EQUIPMENT SET SERIAL_NO = :serial, NAME = :name, CATEGORY_ID = :cat, STATUS = :status WHERE EQUIPMENT_ID = :id",
            {"serial": data.serial_no, "name": data.name, "cat": data.category_id, "status": data.status, "id": equipment_id}
        )
        if cursor.rowcount == 0: # Si cursor.rowcount es 0 significa que no encontró ningún equipo con ese ID para actualizar
            conn.close()
            raise HTTPException(status_code=404, detail="Equipment not found")
        conn.commit() # Guardamos cambios en Oracle
    except HTTPException:
        raise
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))
    conn.close() # Cerramos conexión
    return {"message": "Equipment updated"} # Mensaje de éxito

@router.delete("/{equipment_id}", dependencies=[Depends(verify_admin_role)]) # DELETE borra un equipo; estrictamente limitado a administradores mediante la dependencia
def delete_equipment(equipment_id: int):
    conn = get_connection() # Conexión a la base de datos
    cursor = conn.cursor() # Creamos cursor
    try:
        # Borramos el registro de la tabla EQUIPMENT donde el ID coincida con el parámetro de la ruta
        cursor.execute(
            "DELETE FROM EQUIPMENT WHERE EQUIPMENT_ID = :id",
            {"id": equipment_id}
        )
        if cursor.rowcount == 0: # Si no se borró nada es porque el ID no existía
            conn.close()
            raise HTTPException(status_code=404, detail="Equipment not found")
        conn.commit() # Confirmamos el borrado en Oracle
    except HTTPException:
        raise
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))
    conn.close() # Cerramos conexión limpiamente
    return {"message": "Equipment deleted"} # Mensaje de confirmación de eliminación