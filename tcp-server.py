from socket import *
from sys import argv,exit


BUFSIZE = 1024

port = int(argv[1])
sock = socket(AF_INET, SOCK_STREAM)
try:
    sock.bind(('', port))
except Exception:
    exit(1)
sock.listen(5)

while True:
    clientSocket, clientAddr = sock.accept()
    while line := clientSocket.recv(BUFSIZE).decode():
        capitalised = line.upper()
        clientSocket.send(capitalised.encode())
    clientSocket.close()
