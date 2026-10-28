from pwdlib import PasswordHash

password_hasher = PasswordHash.recommended() # This creates a password-hashing object using the library's recommended algorithm. 
# With the Argon2 support installed, this uses Argon2id.


def hash_password(password: str) -> str: #recibe una contraseña...
    return password_hasher.hash(password)  # y devuelve hash


def verify_password(password: str, stored_hash: str) -> bool: #password = what the user input (in login.html), stored_hash = what Oracle sees
    return password_hasher.verify(password, stored_hash) #es un bool, osea si true: el password igual al hash, si false: no.