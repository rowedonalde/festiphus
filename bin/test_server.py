#test_server.py
#This script is the temporary home of the server until I get the
#threading working in the main script

from pyftpdlib import ftpserver

SERVER_IP = '127.0.0.1'
SERVER_PORT = 3000

#Set up auths for the server:
authorizer = ftpserver.DummyAuthorizer()
#Right now, just set up a user with the following vars
#This user can read and move around--that's pretty much it
authorizer.add_user('don', 'pass', '.', msg_login = 'SUP BRO')
#Set up the handler and provide it with the previous authorizer:
handler = ftpserver.FTPHandler
handler.authorizer = authorizer
address = (SERVER_IP, SERVER_PORT)

#connect the handler to the address and fire up the server:
ftpd = ftpserver.FTPServer(address, handler)
ftpd.serve_forever()
