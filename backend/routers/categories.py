from fastapi import APIRouter
from database.connection import get_connection

router = APIRouter()

@router.get("")
def list_categories():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT CATEGORY_ID, NAME FROM CATEGORIES ORDER BY CATEGORY_ID")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1]} for r in rows]