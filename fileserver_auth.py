import crypto
import socket
import constants
import sqlite3
from sqlite3 import Error

"""
Handles File Server Setup and Authorization
"""


def create_connection():
    # Connecting to the sqlite Database

    connection = None
    try:
        connection = sqlite3.connect(constants.KDC_DATABASE)
        print("Connection to SQLite DB successful")
        connection.execute('create table if not exists SERVICE_DATA(SERVICE_ID varchar(50) NOT NULL, KEY varchar(50), ACTIVE integer, UPDATED integer, PORT_NO integer, PRIMARY KEY(SERVICE_ID))')
    except Error as e:
        print("Database Error")
        exit(1)
    return connection


def authenticate(username,port_no):
    # Authenticating file server

    conn = create_connection()
    c = conn.execute('Select * from SERVICE_DATA where SERVICE_ID = ?', (username,))
    res = c.fetchone()

    #print(res)
    if(res == None):

        conn.execute('insert into SERVICE_DATA VALUES(?,?,?,?,?)',(str(username),str(crypto.get_key()), 1, 0, port_no))
        conn.commit()
        c = conn.execute('select * from SERVICE_DATA where SERVICE_ID=?',(username,))

        # for x in c:
        #     print(x)

        res1 = c.fetchone()
        conn.close()
        return True,res1[1]
    else:
        conn.close()
        return True, res[1]


def get_authenticated(server_id, port_no):
    # While Correct ID_PASS not obtained loop

    flag,client_key = authenticate(server_id, port_no)
    if flag:
        return True, client_key
    else:
        print("Could Not Verify UserID and Password")
        return False, None
    # Finished

# if __name__=="__main__":
#     server_id = "myfrigeesvsfhsDVEAhagedgasdhd"
#     port_no = 8004
#     key = get_authenticated(server_id,port_no)
#     print(key)
