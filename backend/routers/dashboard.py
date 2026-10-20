from fastapi import APIRouter #just the router, no error handling needed
from database.connection import get_connection # Oracle connector

router = APIRouter() #create the router

@router.get("/metrics") #GET on the router's base URL, which main.py will prefix with /api/dashboard
def metrics(): #returns counts for the KPI cards on the dashboard
    conn = get_connection() 
    cursor = conn.cursor() 

    cursor.execute("SELECT COUNT(*) FROM EQUIPMENT") #how many equipment rows
    total_equipment = cursor.fetchone()[0] #first column of the first row

    cursor.execute("SELECT COUNT(*) FROM EQUIPMENT WHERE STATUS = 'AVAILABLE'") #how many are available
    available_equipment = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM USERS") #how many users
    total_users = cursor.fetchone()[0]

    conn.close()
    return {"total_equipment": total_equipment, "available_equipment": available_equipment, "total_users": total_users} #send the counts as JSON


##now what does this do? {
 # "total_equipment": 2,
 # "available_equipment": 2,
 # "total_users": 2
 #}
# the frontend must dispaly some numbers pulled from the database, not hardcoded in HTML
# The three counts above are those numbers. The frontend shows them as the three cards (KPI boxes) at the top of the dashboard.
# This was asked for in  the sectionw where it said "Dashboard con indicadores obtenidos desde el backend". Here it is
# Could we not use this? Of course! We could've told Frontend to run:
# const equipment = await fetch("/api/equipment").then(r => r.json());
# document.getElementById("kpiTotal").innerText = equipment.length;
# so why don't we? t's "the frontend doing the work," not "indicators obtained from the backend." 
# The assignment specifically wants the backend to compute the totals via SQL and hand them over as numbers.