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
        # Continue receiving further messages
        while True:
            data = sock.recv(BUFSIZE)
            if not data:
                raise ConnectionResetError
            msg = data.decode()
            if msg.startswith("FILE"):
                _, filename, filesize = msg.split()
                filesize = int(filesize)

                with open(filename, 'wb') as f:
                    bytes_read = 0
                    while bytes_read < filesize:
                        chunk = sock.recv(min(4096, filesize - bytes_read))
                        if not chunk:
                            break
                        f.write(chunk)
                        bytes_read += len(chunk)
                break
            stdout.buffer.write(data)
            stdout.flush()
    except (ConnectionResetError, OSError, BrokenPipeError) as e:
        pass

def receive_initial_message(sock):
    data = sock.recv(BUFSIZE)
    if not data:
        raise ConnectionResetError
    # Check if the server rejected the username
    if "already has user" in data.decode():
        stdout.buffer.write(data)
        stdout.flush()
        exit(EXIT_STATUS["USERNAME"])  # Exit with status 2
    else:
        print(f"Welcome to chatclient, {username}.")
        stdout.flush()
        stdout.buffer.write(data)
        stdout.flush()

def send_server_message(sock):
    try:
        for line in stdin: # Read line from stdin
            if line.startswith("/quit"):
                if line != "/quit\n":
                    print("[Server Message] Usage: /quit")
                    sys.stdout.flush()
                
                else: # valid quit
                    sock.send(line.encode()) # Send data to server
                    stdout.flush()
                    sock.shutdown(SHUT_RDWR)
                    sock.close()
                    sys.exit(0)

            elif line.startswith("/list"):
                if line != "/list\n":
                    print("[Server Message] Usage: /list")
                    sys.stdout.flush()
                else:
                    sock.send(line.encode()) # Send data to server
                    stdout.flush()
            elif line.startswith("/whisper"):
                token = line.split()
                if token[0] != "/whisper" or len(token) != 3:
                    print(f"[Server Message] Usage: /whisper receiver_client_username chat_message")
                    sys.stdout.flush()
                else:
                    sock.send(line.encode()) # Send data to server
                    sys.stdout.flush()
            elif line.startswith("/switch"):
                raw = line.rstrip("\n")  # only remove newline
                token = raw.split()
                if token[0] != "/switch" or len(token) != 2 or raw != f"/switch {token[1]}":
                    print("[Server Message] Usage: /switch channel_name")
                    sys.stdout.flush()
                else:
                    sock.send(line.encode())
                    sys.stdout.flush()
            else: # broadcast message / not a command
                sock.send(line.encode()) # Send data to server
                stdout.flush()
        # EOF detected
        msg = "/quit"
        sock.send(msg.encode())
        sock.shutdown(SHUT_RDWR)
        sock.close()
        sys.exit(0)
    except (BrokenPipeError, ConnectionResetError):
        server_closed()


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
try:
    sock.send(username.encode())
    receive_initial_message(sock)

except (BrokenPipeError, ConnectionResetError):
    server_closed()

# receive_initial_message(sock)

recv_thread = Thread(target=receive_server_message, args=(sock,), daemon=True)
send_thread = Thread(target=send_server_message, args=(sock,), daemon=True)

recv_thread.start()
send_thread.start()

try:
    send_thread.join()
    recv_thread.join()
except KeyboardInterrupt:
    sock.close()

# sock.close()
