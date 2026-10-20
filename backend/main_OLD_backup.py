from fastapi import FastAPI          # import the FastAPI class from the fastapi library
from database.connection import get_connection #THIS THING CRASHED STUFF ONCE. BECAUSE I DIDN'T ESTABLISH IT. Whatever, done and done.
from pydantic import BaseModel       #el bodyguard de este projecto basemodel is pydantic's base class

app = FastAPI()                       # create the app object

@app.get("/")                         # this is a decorator. Basically, it tells python "for every person who asks for /, run:" 
                                      # and then it runs the following code
def root():                           # define the function.. Define just means "I'm about to create a function".
    #define greet(): print(hello) creates a function called greet. Now when you use 'greet', it automatically prints out hello. 
    return {"status": "backend is running"}   # return this dictionary to Python, which thanks to the decorator, passes it to FastAPI
    ## and fastapi into JSON
    #not when root(): is called, it prints out "status: backend is running"

@app.get("/api/equipment") #Now we run for every time someone asks for /api/equipment
def list_equipment():  #"I am going to create a function named list_Equipment, here's what it'll do"
    conn = get_connection() #conn is a variable that gets assigned get_connection() function. This is a 'phone line' to Oracle
    cursor = conn.cursor() #cursor is a variable that get assigned to conn_cursor() function. The cursor is the thing that actually 
    #sends SQL and holds the rows that come back
    cursor.execute("SELECT EQUIPMENT_ID, NAME, STATUS FROM EQUIPMENT") #This text string is the SQL We want to run
    rows = cursor.fetchall() #this returns all the rows the query produced
    conn.close() #once that we are done with the 'phone call', we shut it. We close it, use the function close.
    return [{"id": r[0], "name": r[1], "status": r[2]} for r in rows] #The [ ] means "this is a list of items."
#Why r[0], r[1], r[2]? Because each row (r) is a tuple. I used "r" as the variable, so r[] selects, 0 is Equipment_ID
#This is comma separation.

#-------------------------- el GET one esta aqui abaho

# Import the FastAPI class (the web framework) and HTTPException (for returning error codes like 404)
from fastapi import FastAPI, HTTPException  # type: ignore


@app.get("/api/equipment/{equipment_id}") #esto va a /api/equipment/ y CUALQUIER cosa a dentro de api/equipment/. Si?
def get_equipment(equipment_id: int):
    # "equipment_id: int" is a TYPE HINT. FastAPI lo valida antes de correr este codigo
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT EQUIPMENT_ID, NAME, STATUS FROM EQUIPMENT WHERE EQUIPMENT_ID = :id",
        {"id": equipment_id}      # y le dice: ''Lenna a "ID" con este valor
    )
    row = cursor.fetchone()       # get ONE row, or None if nothing matched
    conn.close()                 
    if row is None:              
        raise HTTPException(status_code=404, detail="Equipment not found")
    return {"id": row[0], "name": row[1], "status": row[2]} #esto es un 404 si el row es None.

#---------------------- el POST esta aqui abajo

from pydantic import BaseModel # pydantic is a library that defines what shape data must have

class EquipmentInput(BaseModel): #"this is the shape of data a user must send to create equipment"
    serial_no: str #the serial must be text
    name: str #the name must be text
    category_id: int #the category must be a number

@app.post("/api/equipment", status_code=201) #when someone POSTs to /api/equipment, run the function below. 201 means "created"
def create_equipment(data: EquipmentInput): #data is the JSON the user sent, shaped like EquipmentInput
    conn = get_connection() #open a phone line to Oracle
    cursor = conn.cursor() #cursor sends SQL and holds the result
    try: #try to do this, and if it fails, catch the error
        cursor.execute( #send this SQL to Oracle
            "INSERT INTO EQUIPMENT (EQUIPMENT_ID, SERIAL_NO, NAME, CATEGORY_ID, STATUS) VALUES (EQUIPMENT_SEQ.NEXTVAL, :serial, :name, :cat, 'AVAILABLE')", #insert a new row. EQUIPMENT_SEQ.NEXTVAL will give us the next ID automatically
            {"serial": data.serial_no, "name": data.name, "cat": data.category_id} #fill the holes with the values the user sent
        )
        conn.commit() #save the change. Without this, the insert is lost
    except Exception as e: #if Oracle throws an error (e.g., the serial_no already exists)
        conn.close() 
        raise HTTPException(status_code=400, detail=str(e)) #send a 400 "bad request" with the error message
    conn.close() #hang up the phone on success
    return {"message": "Equipment created"} #tell the browser it worked


# -------------- el PUT esta aqui abajo

@app.put("/api/equipment/{equipment_id}") #when someone PUTs to /api/equipment/SOMETHING, run this
def update_equipment(equipment_id: int, data: EquipmentInput): #data is the JSON body, shaped like EquipmentInput
    conn = get_connection() #open a phone line
    cursor = conn.cursor() #cursor to send SQL
    try: #try the SQL, catch errors
        cursor.execute( #send this
            "UPDATE EQUIPMENT SET SERIAL_NO = :serial, NAME = :name, CATEGORY_ID = :cat WHERE EQUIPMENT_ID = :id", #change 3 columns for the row with this ID
            {"serial": data.serial_no, "name": data.name, "cat": data.category_id, "id": equipment_id} #fill all 4 holes
        )
        if cursor.rowcount == 0: #if 0 rows were changed, the ID didn't exist
            conn.close() #close the phone
            raise HTTPException(status_code=404, detail="Equipment not found") #send 404
        conn.commit() #save the change
    except HTTPException: #if we raised a 404, re-raise it
        raise
    except Exception as e: #any other DB error
        conn.close() #close
        raise HTTPException(status_code=400, detail=str(e)) #send 400
    conn.close() #close on success
    return {"message": "Equipment updated"} #tell the browser+


### --------------- aqui esta el DELETE abajo de aqui de este mensaje

@app.delete("/api/equipment/{equipment_id}") #when someone DELETEs /api/equipment/SOMETHING, run this
def delete_equipment(equipment_id: int): #equipment_id is the number from the URL
    conn = get_connection() #open a phone line
    cursor = conn.cursor() #cursor to send SQL
    try: #try, catch errors
        cursor.execute( #send this
            "DELETE FROM EQUIPMENT WHERE EQUIPMENT_ID = :id", #delete the row with this ID
            {"id": equipment_id} #fill the hole
        )
        if cursor.rowcount == 0: #if 0 rows were deleted, the ID didn't exist
            conn.close() #close
            raise HTTPException(status_code=404, detail="Equipment not found") #send 404
        conn.commit() #save
    except HTTPException: #re-raise our own 404
        raise
    except Exception as e: #any other DB error
        conn.close() #close
        raise HTTPException(status_code=400, detail=str(e)) #send 400
    conn.close() #close on success
    return {"message": "Equipment deleted"} #tell the browser