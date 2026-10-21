import oracledb

conn = oracledb.connect(
    user="system",
    password="Oracle123",
    dsn="localhost:1521/XEPDB1"
)
cursor = conn.cursor()
cursor.execute("SELECT 1 FROM DUAL")
print(cursor.fetchone())
conn.close()
print("SUCCESS")