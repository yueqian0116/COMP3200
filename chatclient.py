from socket import *
from sys import stdout,stdin,argv,exit
from client_support import *


BUFSIZE = 1024

check_arguments(argv)
# we have passed the command line argument checks
port = int(argv[1])
username = argv[2]
hostname = "localhost"

# check addrinfo


# sock.connect(serverAddr[0][4])
try:
    sock = socket(AF_INET, SOCK_STREAM)
    serverAddr = getaddrinfo(hostname, port, 
           AF_INET, SOCK_STREAM)
    sock.connect((hostname,port))
    # we have succesfully connected to the server
    sock.send(username.encode())
    print(f"Welcome to chatclient, {username}.")
except Exception: # unable to create a socket and connect to server
    unable_to_connect_port(port)


# If your client detects that the connection to the server has been closed then it should print the following 246
#  message (terminated by a newline) to stderr:
for line in stdin:
      sock.send(line.encode())
      data = sock.recv(BUFSIZE)
      if not data:
            break
      stdout.buffer.write(data)
      stdout.flush()

sock.close()

