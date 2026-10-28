from password_utils import hash_password
from database.connection import get_connection

# Generate the new hash for "admin123"
new_hash = hash_password("admin123")

conn = get_connection()
cursor = conn.cursor()

try:
    # 1. Update the Admin (Lab Admin)
    cursor.execute(
        "UPDATE USERS SET PASSWORD_HASH = :pwd WHERE EMAIL = 'admin@lab.edu'",
        {"pwd": new_hash}
    )
    
    # 2. Update all other existing users (like John Doe) so they also get a working password
    cursor.execute(
        "UPDATE USERS SET PASSWORD_HASH = :pwd WHERE EMAIL != 'admin@lab.edu'",
        {"pwd": new_hash}
    )
    
    conn.commit()
    print("SUCCESS! All users have been updated with the new Argon2 hash.")
    print(f"Password for everyone is now: admin123")
except Exception as e:
    print("Error:", e)
finally:
    conn.close()