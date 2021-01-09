import os
import constants
import crypto
import socket
import fileserver_auth
import pickle
from termcolor import colored
"""
Setting Up File Server's TCP Side
"""


def get_server_key(server_id,port_no):

    # Obtain Session Key From the Database
    flag,server_key = fileserver_auth.get_authenticated(server_id,port_no)
    if(flag==False):
        exit(1)

    # Init Server Folder
    if not os.path.exists(server_id):
        os.makedirs(server_id)

    # Init Server's Temporary Database
    s={}
    pickle.dump(s,open('session'+server_id+'.p','wb'))
    pickle.dump(s, open('dir' + server_id + '.p', 'wb'))
    return server_key


def get_session_key(service_id):
    return pickle.load(open('session' +service_id + '.p', 'rb'))


def get_curr_dir(service_id):
    return pickle.load(open('dir' +service_id + '.p', 'rb'))


def post_session_key( service_id, session_keys):
    pickle.dump(session_keys, open('session' +service_id + '.p', 'wb'))


def post_curr_dir(service_id, curr_dir):
    pickle.dump(curr_dir, open('dir' +service_id + '.p', 'wb'))


def update_my_database(user_id,session_key,server_id):

    # Updates Database to allow a new Client to be able to interact with file server
    curr_dirs = get_curr_dir(server_id)
    session_keys = get_session_key(server_id)
    curr_dirs[user_id]=['.',server_id]
    session_keys[user_id]=session_key
    post_session_key(server_id,session_keys)
    post_curr_dir(server_id,curr_dirs)


def get_service_ticket(stream,server_key):
    # Decrypt Service Ticket
    dstream=crypto.decrypt(stream,server_key)
    return crypto.unserial(dstream)


def verify_and_update(connection,client_addr,server_id,server_key,rpc_port):
    # Handles Client Authorization Request

    print("Connection from ", client_addr)

    data = connection.recv(4096)
    ticket = get_service_ticket(data, server_key)
    if (ticket[constants.SERVICE_ID] != server_id):
        raise Exception("Wrong Message Received")

    update_my_database(ticket[constants.USER_ID], ticket[constants.SESSION_SERVICE_KEY],server_id)

    # Acknowledgement
    response = {}
    response[constants.SERVICE_ID] = ticket[constants.SERVICE_ID]
    response[constants.RPC_PORT] = rpc_port
    connection.send(crypto.encrypt(crypto.serial(response), ticket[constants.SESSION_SERVICE_KEY]))
    connection.close()
    return True

def main():
    # Server Info
    hostname = 'localhost'
    port = int(input("Enter Port Number\n").strip())
    rpc_port = int(input("Enter RPC Port Number\n").strip())
    server_id=input("Enter Server ID\n")

    server_key=get_server_key(server_id,port)
    print(colored("Server Key "+ server_key,'yellow'),colored('Sensitive Information Only Printed for Demo Purpose','red'))

    server_address=(hostname,port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Starting AuthServer on port %s", str(server_address[1]))

    sock.bind(server_address)
    sock.listen()

    while True:
        print("Waiting for a connection....")
        connection, client_addr = sock.accept()
        verify_and_update(connection,client_addr,server_id,server_key,rpc_port)


if __name__ == "__main__":
    main()








# def create_new_file(path):
#     with open(path) as myfile:
#         for line in myfile:
#             pass
#     webbrowser.open(path)
#     print("File created at "+path+"(You Can Edit)")
# def make_dir(path):
#     if not os.path.exists(path):
#         os.makedirs(path)
# def update_files_and_directories():
#     while(True):
#         print("1. Create Directory")
#         print("2. Create File")
#         option = int(input())
#         if(option==1):
#             print("Enter Complete Path of Directory")
#             path = input().strip()
#             make_dir(path)
#         elif(option==2):
#             print("Enter Complete Path of File")
#             path = input().strip()
#             create_new_file(path)
#         print("Edit More? yes/no")
#         ty = input().strip()
#         if(ty=="no"):
#             break




