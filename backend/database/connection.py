import oracledb                    # load the library

def get_connection():              # define a function called get_connection
                                   # (takes no arguments)
    return oracledb.connect(       # open a connection to Oracle
        user="system",             # and log in as this user
        password="Oracle123",      # with this password
        dsn="localhost:1521/XEPDB1"# at this address
    )                              # hand the connection back to the caller