from socket import *
from sys import stdout,stdin,argv,exit
from client_support import *
from threading import Lock, Thread, current_thread

BUFSIZE = 1024

check_arguments(argv)
# we have passed the command line argument checks
port = int(argv[1])
username = argv[2]
hostname = "localhost"

def receive_server_message(sock):
    try:
        while True:
            data = sock.recv(BUFSIZE)
            if not data:
                raise ConnectionResetError  # Treat EOF as disconnection
            stdout.buffer.write(data)
            stdout.flush()
    except (ConnectionResetError, OSError, BrokenPipeError) as e:
        pass


def send_server_message(sock):
    try:
        for line in stdin: # Read line from stdin
            sock.send(line.encode()) # Send data to server
            stdout.flush()
    except:
        pass

# sock.connect(serverAddr[0][4])
try:
    sock = socket(AF_INET, SOCK_STREAM)
    serverAddr = getaddrinfo(hostname, port, 
           AF_INET, SOCK_STREAM)
    sock.connect((hostname,port))
    # we have succesfully connected to the server
    
except Exception: # unable to create a socket and connect to server
    unable_to_connect_port(port)


# If your client detects that the connection to the server has been closed then it should print the following 246
#  message (terminated by a newline) to stderr:
sock.send(username.encode())
print(f"Welcome to chatclient, {username}.")

recv_thread = Thread(target=receive_server_message, args=(sock,), daemon=True)
send_thread = Thread(target=send_server_message, args=(sock,), daemon=True)

recv_thread.start()
send_thread.start()

try:
    recv_thread.join()
except KeyboardInterrupt:
    sock.close()


# sock.close()

