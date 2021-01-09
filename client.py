
import os, sys, crypto, rpyc
import pickle
import client_auth
import socket
import constants
import Service
from termcolor import colored
"""
Setting Up the Client Side
"""


def get_access_init(user_id):
    # Returns List of all active File servers
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # client.bind((hostname, port))
    client.connect(constants.KDC)  # Authentication server
    print("Connected to Authentication Server")

    data = {}
    data[constants.USER_ID] = user_id
    data[constants.REQUEST_TYPE] = constants.INIT
    data_stream = crypto.serial(data)
    client.send(data_stream)
    print("Request sent to the Authentication server for Initialization")

    response_stream = client.recv(4096)
    response= crypto.unserial(response_stream)
    if response[constants.STATUS]==False:
        print("Could Not Verify with Server")
        exit(1)
    active_file_servers = response[constants.ACTIVE_SERVERS]
    client.close()
    return active_file_servers



def main():
    # hostname = sys.argv[0]
    # port = sys.argv[1]
    # # Get Client ID
    client_id, client_key = client_auth.get_authenticated()
    print(colored("Private Key:"+client_key,'yellow'),colored('Sensitive Information, Printed Only for Demo','red'))
    print("Authentication Successful")
    active_file_server_list = get_access_init(client_id)
    print(colored("Starting Shell",'blue'))
    Service.shell(active_file_server_list,client_id,client_key)

if __name__=="__main__":
	main()
