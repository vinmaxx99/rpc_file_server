import socket
import crypto
import constants
import sqlite3
from sqlite3 import Error

"""
Setting up The KDC Server
"""


def clear():
	# Initial Clearing functions
	conn = sqlite3.connect(constants.KDC_DATABASE)
	conn.execute("DROP TABLE IF EXISTS CLIENT_DATA")
	conn.execute("DROP TABLE IF EXISTS SERVICE_DATA")
	conn.close()


def database_init():
	# Loading Sqlite Database
	try:
		conn = sqlite3.connect(constants.KDC_DATABASE)
		print("Connection to SQLite DB successful")
		return conn
	except Error as e:
		print("Database Error")
		exit(1)


def create_server_response(ss_key,user_key):

	# Response for sending Session key to Client
	data={}
	data[constants.SESSION_SERVICE_KEY] = ss_key
	# Encrpyting with Users_Key
	return crypto.encrypt(crypto.serial(data),user_key)


def create_service_ticket(userid, serviceid, ss_key, service_key, user_ip):

	# Generating Service Ticket for file server
	data = {}
	data[constants.USER_ID] = userid
	data[constants.SERVICE_ID] = serviceid
	data[constants.SESSION_SERVICE_KEY] = ss_key
	data[constants.USER_IP] = user_ip

	# Encrypt Service ticket with file_server.py's Key
	return crypto.encrypt(crypto.serial(data),service_key)


def get_active_file_servers():
	# Get active File Servers from database
	conn = database_init()
	crs = conn.cursor()
	c = crs.execute('Select * from SERVICE_DATA where ACTIVE =1')
	ls =[]
	for x in c:
		ls.append((x[0],x[4]))
	conn.close()
	return ls


def handle_init_request(user_request,connection):
	# Handles Active File Server List Request

	user_id = user_request[constants.USER_ID]

	# Check in database if user id exists
	conn = database_init()
	crs = conn.cursor()
	c = crs.execute('Select * from CLIENT_DATA where USER_ID =?', (user_id,))
	res = c.fetchone()
	conn.close()
	if(res == None):
		print("USER ID doesn't exist")
		data={}
		data[constants.STATUS] = False
	else:
		print("User Verified")
		data={}
		data[constants.STATUS] = True
		data[constants.ACTIVE_SERVERS] = get_active_file_servers()
	# Sending Response
	data_stream = crypto.serial(data)
	connection.send(data_stream)
	print("Responded to ",user_id)


def handle_connection_request(user_request,connection,client_addr):
	# Handles Specific Request to obtain session key for a particular server
	user_id = user_request[constants.USER_ID]

	# Check in database if user id exists
	conn = database_init()
	crs = conn.cursor()
	c = crs.execute('Select * from CLIENT_DATA where USER_ID =?', (user_id,))
	res = c.fetchone()

	if(res==None):
		print("USER ID doesn't exist")
		data = {}
		data[constants.STATUS] = False
		conn.close()
	else:
		service_id = user_request[constants.SERVICE_ID]
		crs = conn.cursor()
		c = crs.execute('Select * from SERVICE_DATA where SERVICE_ID =?', (service_id,))
		res1 = c.fetchone()
		if(res1==None):
			data = {}
			data[constants.STATUS] = False
			conn.close()
		else:
			data={}
			data[constants.STATUS] = True
			conn.close()
			# Getting Keys
			client_key = res[2]
			session_key = crypto.get_key()
			service_key = res1[1]
			# Creating Response
			server_response = create_server_response(session_key, client_key)
			service_ticket = create_service_ticket(user_id, service_id, session_key, service_key, client_addr)

			data[constants.SERVER_RESPONSE] = server_response
			data[constants.SERVICE_TICKET] = service_ticket
			# Sending Response
			data_stream = crypto.serial(data)
			connection.send(data_stream)
		print("Responded to ", user_id)


def main():
	# Connecting with Database
	clear()
	database_init()
	# Bind and wait for Incoming Connection
	sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	print("Starting AuthServer on port %s",str(constants.KDC[1]))
	sock.bind(constants.KDC)
	sock.listen()

	while True:
		print("Waiting for a connection....")
		connection, client_addr = sock.accept()
		try:
			print("Connection From ", client_addr)
			# Receiving Data
			data = connection.recv(4096)
			user_request=crypto.unserial(data)

			# Handling Requests
			if user_request[constants.REQUEST_TYPE] == constants.INIT:
				handle_init_request(user_request, connection)
			else:
				handle_connection_request(user_request, connection, client_addr)
		finally:
			print("Response Sent")
		connection.close()


if __name__=="__main__":
	main()
