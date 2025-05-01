from socket import *
from threading import Lock, Thread, current_thread
from time import sleep
from sys import argv,exit
from server_support import *

# Shared resource (counter to count the number of data packets received)
counter = 0
counter_lock = Lock()

BUFSIZE=1024

# if you do the check on the server side and tell the client the result of the check. 
# we have to find a way to keep track of all the usernames in a channel, and make sure it does not exceed the channel capacity
# can use dictionary to keep track of channels and usernames

def handle_client(client_socket, client_address):
    global counter
    host,_ = getnameinfo(client_address, 0)
    print(f"Connection from {client_address} ({host}) has been established.")
    with client_socket:
        # getting username from client, CHATGPT
        username = client_socket.recv(BUFSIZE).decode().strip()
        print(f"[Server Message] {username} has joined the channel \"channel_name\"")
        # Send a message to the client
        message = f"Welcome to the chatclient, {host}.\n"
        client_socket.sendall(message.encode())

        while data := client_socket.recv(BUFSIZE):
            # Locking the shared resource (counter)
            with counter_lock:
                print(f"Thread {current_thread().name} got the lock.")
                counter += 1
                print(f"Counter value updated to: {counter}")
                # Simulate doing some work
                sleep(2)
                data = data.decode().upper() 
                client_socket.sendall(data.encode())
        # error or EOF - client disconnected

    print(f"Connection from {client_address} closed.")

def start_server(port):
    listening_socket = socket(AF_INET, SOCK_STREAM)
    listening_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    try:
        listening_socket.bind(('', port))
    except Exception:
        exit(1)
    listening_socket.listen(5)
    
    print(f"Server listening on port {port}")
    return listening_socket

def process_connections(listening_socket):
    while True:
        client_socket, client_address = listening_socket.accept()
        client_thread = Thread(target=handle_client, 
                args=(client_socket, client_address))
        client_thread.start()

        

# Run the server
if __name__ == "__main__":
    print("hello")
    check_arguments(argv)
    # socket = start_server(int(argv[1]))
    # process_connections(socket)

    
