import rpyc
import constants
import crypto
import socket
from os import system, name
from termcolor import colored
"""
Handles Services
1. File Server RPC
2. Shell 
"""


class file_server:
    # This class will be used to access file server's data

    def __init__(self,service_id, port_no, session_key):
        self.__hostname = 'localhost'
        self.__service_id = service_id
        self.__port_no = port_no
        self.__session_key = session_key
        self.client = None

    def ls(self):
        # Out : list of tuples [(name,1 for dir 0 for file)]
        data_en_stream = self.client.root.ls()
        if(data_en_stream == None):
            return None
        data_stream = crypto.decrypt(data_en_stream, self.__session_key)
        data = crypto.unserial(data_stream)
        print(colored('RPC Procedure Success', 'green'))
        return data

    def pwd(self):
        # Out: Path List
        data = self.client.root.pwd()
        if data == None:
            return None
        data = crypto.decrypt(data, self.__session_key)
        data = crypto.unserial(data)
        print(colored('RPC Procedure Success', 'green'))
        return data


    def cd_forward(self, folder_name):
        # Out: Path List
        data = self.client.root.cdforward(folder_name)
        if data == None:
            return None
        data = crypto.decrypt(data, self.__session_key)
        data = crypto.unserial(data)
        print(colored('RPC Procedure Success', 'green'))
        return data

    def cd_backward(self):
        # Out: Path List
        data = self.client.root.cdbackward()
        if data == None:
            return None
        data = crypto.decrypt(data, self.__session_key)
        data = crypto.unserial(data)
        print(colored('RPC Procedure Success', 'green'))
        return data

    def create_file(self, file_name):
        # Out: ACK
        data = self.client.root.create_file(file_name)
        if data == None:
            return None
        data = crypto.decrypt(data, self.__session_key)
        data = crypto.unserial(data)
        print(colored('RPC Procedure Success', 'green'))
        return data

    def make_dir(self, folder_name):
        # Out: Path
        data = self.client.root.make_dir(folder_name)
        if data == None:
            return None
        data = crypto.decrypt(data, self.__session_key)
        data = crypto.unserial(data)
        print(colored('RPC Procedure Success', 'green'))
        return data

    def cat(self, file_name):
        # Out : list(String)
        data = self.client.root.cat(file_name)
        if data == None:
            return None
        data = crypto.decrypt(data, self.__session_key)
        data = crypto.unserial(data)
        print(colored('RPC Procedure Success', 'green'))
        return data

    def cp(self,filename, newpath):
        # Out: ACK
        data =  self.client.root.cp(filename, newpath)
        if data == None:
            return None
        data = crypto.decrypt(data, self.__session_key)
        data = crypto.unserial(data)
        print(colored('RPC Procedure Success', 'green'))
        return data

    def open(self,user_id):
        # Init Server Connection
        self.client = rpyc.connect(self.__hostname,self.__port_no)
        self.client.root.init(user_id,self.__service_id)

    def close(self):
        # Close Server Connection
        self.client.close()

    def get_service_id(self):
        return self.__service_id


def get_session_key(file_server_id,file_server_port,user_id,client_key):
    # Provides Session Key for accessing a file server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # client.bind((hostname, port))
    client.connect(constants.KDC)

    data = {}
    data[constants.USER_ID] = user_id
    data[constants.SERVICE_ID] = file_server_id
    data[constants.REQUEST_TYPE] = constants.SPECIFIC
    data_stream = crypto.serial(data)
    client.send(data_stream)
    print("Request sent to the Authentication server for Session Key")
    print("Establishing Session Key Using Needham Schroder Protocol")
    response_stream = client.recv(4096)
    response = crypto.unserial(response_stream)
    if not response[constants.STATUS]:
        print("Bad Request")
        exit(1)

    user_response_encoded = response[constants.SERVER_RESPONSE]
    service_ticket_encoded = response[constants.SERVICE_TICKET]

    user_response = crypto.unserial(crypto.decrypt(user_response_encoded,client_key))
    session_key = user_response[constants.SESSION_SERVICE_KEY]
    client.close()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost',file_server_port))
    client.send(service_ticket_encoded)

    response_service_stream = client.recv(4096)
    response_service = crypto.unserial(crypto.decrypt(response_service_stream,session_key))

    if response_service[constants.SERVICE_ID]!=file_server_id:
        print("Could Not Establish Communication with File server")
        return False,None
    rpc_port = response_service[constants.RPC_PORT]
    return True,session_key,rpc_port


def create_path(current_working_directory):
    return '/'.join(current_working_directory)


def get_portno(file_server,active_file_server_list):
    for x,y in active_file_server_list:
        if(x==file_server):
            return y
    return None


def get_object(service_id,port_no,session_key,user_id):
    fs = file_server(service_id,port_no,session_key)
    fs.open(user_id)
    print(colored('RPC connection Established with'+ service_id, 'green'))
    return fs


def shell(file_server_list,user_id,client_key):
    active_file_server_list = file_server_list
    current_working_directory = ["."]
    open_file_object = None
    print(colored("All commands will be implemented using RPC calls in terminal",'blue'))
    while True:
        inp = input('your_prompt' +create_path(current_working_directory)+'$ ').strip().split()

        if inp[0] == 'ls':
            # Listing Directories
            if(len(current_working_directory)==1):
                for x in active_file_server_list:
                    print(colored('<'+x[0]+'>','green'))
            else:
                result = open_file_object.ls()

                if(result==None):
                    print(colored("Could Not Execute the Command",'red'))
                else:
                    for x,y in result:
                        if y == 1:
                            print(colored('<'+x+'>','green'))
                        else:
                            print(colored(x,'yellow'))

        elif inp[0] == 'cd':
            # Moving between files
            if(inp[1] == '..'):
                if(len(current_working_directory)==1):
                    print(colored("Already at Root Cant Go Further",'red'))
                elif(len(current_working_directory)==2):
                    current_working_directory = current_working_directory[:len(current_working_directory)-1]
                else:
                    result = open_file_object.cd_backward()
                    if(result==None):
                        print(colored("Could Not Execute the Command",'red'))
                    else:
                        current_working_directory = result
            else:
                if(len(current_working_directory)==1):
                    pno = get_portno(inp[1],active_file_server_list)
                    if pno == None:
                        print(colored("Invalid Directory",'red'))
                    else:
                        ls,session_key,rpc_port = get_session_key(inp[1],pno,user_id,client_key)
                        if(ls == False):
                            print(colored("Could Not Connect to the Server",'red'))
                        else:
                            open_file_object = get_object(inp[1],rpc_port,session_key,user_id)
                            current_working_directory.append(inp[1])
                else:
                    result = open_file_object.cd_forward(inp[1])
                    if (result == None):
                        print(colored("Could Not Execute the Command",'red'))
                    else:
                        current_working_directory = result


        elif inp[0] == 'cat':
            # Open File
            result = open_file_object.cat(inp[1])
            if(result == None):
                print(colored("Could Not Execute Command",'red'))
            else:
                for x in result:
                    print(x)
        elif inp[0] == 'pwd':
            # Present Working Directory
            result = open_file_object.pwd()
            if (result == None):
                print(colored("Could Not Execute Command",'red'))
            else:
                print(colored(create_path(current_working_directory),'yellow'))
                current_working_directory = result
        elif inp[0]== 'exit':
            break
        elif inp[0]== 'clear':
            if name == 'nt':
                _ = system('cls')
            else:
                _ = system('clear')
        elif inp[0] == 'mkdir':
            if (len(current_working_directory) == 1):
                print(colored("Please select a file_server first",'red'))
            else:
                result = open_file_object.make_dir(inp[1])
                if result == None:
                    print(colored("Could Not Execute Command",'red'))
                else:
                    print(colored("Created New Directory",'yellow'))
        elif inp[0] == 'nano':
            if (len(current_working_directory) == 1):
                print(colored("Please select a file_server first",'red'))
            else:
                open_file_object.create_file(inp[1])
        elif inp[0] == 'cp':
            if (len(current_working_directory) == 1):
                print(colored("Please select a file_server first",'red'))
            else:
                open_file_object.cp(inp[1], inp[2])
        else:
            print(colored("Invalid command",'red'))
