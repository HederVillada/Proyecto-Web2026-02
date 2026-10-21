import oracledb

conn = oracledb.connect(user="system", password="Oracle123", dsn="localhost:1521/XEPDB1")
cursor = conn.cursor()

# This is the same as running SQL, but from Python.
# We use "try/except" because if the sequence already exists, Oracle will throw an error, and we just want to ignore it.
try:
    cursor.execute("CREATE SEQUENCE RESERVATIONS_SEQ START WITH 1 INCREMENT BY 1")
    print("Created RESERVATIONS_SEQ")
except Exception as e:
    print("RESERVATIONS_SEQ already exists or error:", e)

try:
    cursor.execute("CREATE SEQUENCE DETAILS_SEQ START WITH 1 INCREMENT BY 1")
    print("Created DETAILS_SEQ")
except Exception as e:
    print("DETAILS_SEQ already exists or error:", e)

conn.commit()
conn.close()
print("Done checking sequences.")