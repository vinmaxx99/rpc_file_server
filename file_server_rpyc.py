from rpyc.utils.server import ThreadedServer
import rpyc
import webbrowser
from os import listdir
import os
from os.path import isfile, join
from shutil import copyfile
import crypto
global session_records
import pickle
from termcolor import colored
"""
Handles File Server's RPC Port
"""


class MyService(rpyc.Service):
    # This Class will be running at the RPC port

    def __init__(self,service_id):
        self.current_dir=[]
        self.session_key=''
        self.client_id='.'
        self.service_id=service_id

    def get_session_key(self):
        return pickle.load(open('session'+self.service_id+'.p', 'rb'))

    def get_curr_dir(self):
        return pickle.load(open('dir'+self.service_id+'.p', 'rb'))

    def post_session_key(self, session_keys):
        pickle.dump(session_keys, open('session'+self.service_id+'.p', 'wb'))

    def post_curr_dir(self, curr_dir):
        pickle.dump(curr_dir, open('dir' + self.service_id + '.p', 'wb'))

    def create_path(self):
        out = '/'.join(self.current_dir)
        return out

    def on_connect(self, conn):
        pass

    def on_disconnect(self, conn):
        # Commiting Changes on disconnect
        curr_dirs = self.get_curr_dir()
        curr_dirs[self.client_id] = self.current_dir
        self.post_curr_dir(curr_dirs)

    def exposed_init(self, client_id, service_id):

        # Initialization received from client side
        print("Connection Init Request from ",client_id)
        self.service_id = service_id
        self.client_id = client_id

        session_keys = self.get_session_key()
        curr_dirs = self.get_curr_dir()

        self.session_key = session_keys[client_id]
        self.current_dir = curr_dirs[client_id]

        self.post_curr_dir(curr_dirs)
        self.post_session_key(session_keys)


    def exposed_pwd(self):
        # Return Present Working Directory of the Client at the file server
        print("pwd")
        return crypto.encrypt(crypto.serial(self.current_dir),self.session_key)

    def exposed_cdforward(self, foldername):
        # move to a folder
        print("cd")

        old_path = self.create_path()
        new_path = old_path+'/'+foldername

        if not os.path.exists(new_path):
            return None
        self.current_dir.append(foldername)

        return crypto.encrypt(crypto.serial(self.current_dir),self.session_key)

    def exposed_cdbackward(self):
        # Move one step backward
        print("cd ..")

        if(len(self.current_dir)==2):
            return None

        self.current_dir = self.current_dir[:len(self.current_dir)-1]

        return crypto.encrypt(crypto.serial(self.current_dir),self.session_key)

    def exposed_ls(self):
        # Print all files and Folder
        print("ls")

        path = self.create_path()[2:]


        directories = [name for name in os.listdir(path) if os.path.isdir(join(path,name))]
        files = [f for f in listdir(path) if isfile(join(path, f))]


        # Sending result as tuple where x[1] =1 for directory and 0 for file
        all_combined=[]
        for x in directories:
            all_combined.append((x,1))
        for x in files:
            all_combined.append((x,0))
        all_combined.sort()

        return crypto.encrypt(crypto.serial(all_combined),self.session_key)

    def exposed_cat(self,filename):
        # Return file content
        print("cat")
        newpath = self.create_path()+'/'+filename

        try:
            file_content = []
            with open(newpath) as myfile:
                for line in myfile:
                    file_content.append(line)
            return crypto.encrypt(crypto.serial(file_content),self.session_key)
        except:
            return None

    def exposed_cp(self,filename,new_path):
        # Copy File
        print("cp")
        try:
            newpath = new_path
            copyfile(self.create_path()+'/'+filename,newpath)
            return crypto.encrypt(crypto.serial("ACK"),self.session_key)
        except:
            return None


    def exposed_create_file(self,filename):
        # Create New File
        print("nano")
        path = self.create_path()+'/'+filename
        path = path[2:]
        # print(path)

        # Creating File
        with open(path,'w') as myfile:
                pass
        # Opening File for edit
        os.system('gedit '+path)
        # print("File created at " + path + "(You Can Edit)")
        return crypto.encrypt(crypto.serial(self.current_dir), self.session_key)

    def exposed_make_dir(self,foldername):
        # Make New Directory
        old_path = self.create_path()
        path = old_path+'/'+foldername
        path = path[2:]
        # print(path)
        if not os.path.exists(path):
            os.makedirs(path)
        return crypto.encrypt(crypto.serial(self.current_dir), self.session_key)


def main():
    # Start Server
    rpc_port = int(input("Enter RPC Port Number\n").strip())
    service_id = input("Enter Service ID\n").strip()
    print(colored("Started Port. Waiting for connection",'blue'))
    t = ThreadedServer(MyService(service_id), port=rpc_port)
    t.start()


if __name__ =="__main__":
    main()
