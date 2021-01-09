import crypto
import socket
import constants
import sqlite3
from sqlite3 import Error

"""
A server with Accepts and respond to client authorization requests
"""
def create_connection():
    # Creates Connection with Database
    connection = None
    try:
        connection = sqlite3.connect(constants.KDC_DATABASE)
        # print("Connection to SQLite DB successful")
    except Error as e:
        print("Database Error")
        exit(1)
    return connection


def authenticate(username,password,connection):
    # Verifies USERID and Password
    cursor = connection.cursor()
    c = connection.execute('Select * from CLIENT_DATA where USER_ID =?',(username,))
    res = c.fetchone()
    if res == None:
        return 0
    return 1


def main():
    # Creating Connection to Database
    conn = create_connection()
    # Binding Server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Starting AuthClient on port %s", str(constants.KDC_CLIENT_VERIFICATION[1]))
    sock.bind(constants.KDC_CLIENT_VERIFICATION)
    sock.listen()
    while (True):
        print("Waiting for a connection....")
        connection, client_addr = sock.accept()

        # Receiving Input
        input_stream = connection.recv(4096)
        request = crypto.unserial(input_stream)
        user_id =  request[constants.USER_ID]
        password = request[constants.PASSWORD]

        # Verifies Client Details with Database
        client_secret_key = authenticate(user_id,password,conn)
        request[constants.USER_ID] = user_id
        if client_secret_key==0:
            request[constants.STATUS] = constants.FAILURE
        else:
            request[constants.STATUS] = constants.ACCOUNT_PRESENT

        # Sending Response
        data_stream = crypto.serial(request)
        connection.send(data_stream)
        connection.close()


if __name__=="__main__":
    main()
    # TEST CODE
    # conn = create_connection()
    # rf = conn.execute("Select * from CLIENT_DATA")
    # for x in rf:
    #     print(x)
    # # print(authenticate("df1","df2",conn))

