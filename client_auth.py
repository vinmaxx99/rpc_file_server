import crypto
import socket
import constants
import sqlite3
from sqlite3 import Error
"""
Handles Authorization request from client Side
"""
def create_connection():
    # Create Connection to Client Database
    connection = None
    try:
        connection = sqlite3.connect(constants.KDC_DATABASE)
        print("Connection to SQLite DB successful")
        connection.execute('create table if not exists CLIENT_DATA(USER_ID varchar(50) NOT NULL,PASS varchar(50),KEY varchar(50),PRIMARY KEY(USER_ID))')
    except Error as e:
        print("Database Error")
        exit(1)
    return connection

def authenticate(username,password):
    # Authenticate Client
    # Fetch Details from Database
    conn = create_connection()
    c = conn.execute('Select * from CLIENT_DATA where USER_ID = ?', (username,))
    res = c.fetchone()
    # print(res)
    if (res == None):
        conn.execute('insert into CLIENT_DATA VALUES(?,?,?)',
                     (str(username), str(password),str(crypto.get_key())))
        conn.commit()
        c = conn.execute('select * from CLIENT_DATA where USER_ID = ?', (username,))
        res = c.fetchone()
        conn.close()

    # Getting Acceptance from KDC Authorization Service
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(constants.KDC_CLIENT_VERIFICATION)

    data = {}
    data[constants.USER_ID] = username
    data[constants.PASSWORD] = password

    # =1 when create account if not present
    data_stream = crypto.serial(data)
    client.send(data_stream)

    # Sended for Authentication
    response_stream = client.recv(4096)
    response = crypto.unserial(response_stream)
    # print(response)
    client.close()
    #print(response)

    if response[constants.STATUS] != constants.ACCOUNT_PRESENT:
        return False, ""
    return True, res[2]

def get_authenticated():
    # While Correct ID_PASS not obtained loop
    while(True):
        print("Enter Username: ")
        username = input()
        print("Enter Password:")
        password = input()
        flag,client_key = authenticate(username,password)
        if(flag == True):
            return username, client_key
        else:
            print("Could Not Verify UserID and Password")

    # Finished

# if __name__=="__main__":
    # # conn = create_connection()
    # # conn.execute("drop table SERVICE_DATA")
    # # conn.execute("drop table CLIENT_DATA")
    # # conn.close()
    # # conn = create_connection()
    # # for x in p:
    # #     print(x)
    # # conn.close()
    # key = get_authenticated()
    # print(key)
