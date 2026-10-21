import oracledb  # load the library
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

def get_connection(): # define a function called get_connection
     # (takes no arguments)
    return oracledb.connect( # open a connection to Oracle
        user=os.getenv("DB_USER"), # and log in as this user
        password=os.getenv("DB_PASSWORD"), # with this password
        dsn=os.getenv("DB_DSN") # at this address
    ) # hand the connection back to the caller