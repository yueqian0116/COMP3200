from socket import *
from sys import stdout,stdin,argv,exit
import sys

# PLEASE REFERENCE THIS TO 2310 A4

#  basically an enum for exit status
EXIT_STATUS = {
    "USAGE": 3,
    "PORT": 7,
    "USERNAME": 2,
    "CONNECTION_CLOSED": 8
}

def usage_error():
    print("Usage: chatclient port_number client_username", file=sys.stderr)
    sys.exit(EXIT_STATUS["USAGE"])

def unable_to_connect_port(port_number):
    print(f"Error: Unable to connect to port {port_number}.", file=sys.stderr)
    sys.exit(EXIT_STATUS["PORT"])
    
def username_error(channel_name, client_username):
    print(f"[Server Message] Channel \"{channel_name}\" already has user {client_username}.", file=sys.stderr)
    sys.exit(EXIT_STATUS["USERNAME"])

def server_closed():
    print(f"Error: server connection closed.", file=sys.stderr)
    sys.exit(EXIT_STATUS["CONNECTION_CLOSED"])



def channel_full(number_of_users):
    print(f"[Server Message] You are in the waiting queue and there are {number_of_users} user(s) ahead of you.")

def channel_has_user(username, member_list: list) -> bool:
    return username in member_list
    
def connection_closed():
    print(f"Error: server connection closed.", file=sys.stderr)
    sys.exit(EXIT_STATUS["CONNECTION_CLOSED"])

def check_arguments(argv) -> None:
    if len(argv) != 3:
        usage_error()

    port = argv[1]
    username = argv[2]

    if not port or not username or ' ' in username:
        usage_error()

    # client port checking
    if not port.isdigit():
        unable_to_connect_port(port)

# def process_commands(msg):
#     token = msg.split()
#     if msg.startswith("/send"):
#         if len(token) != 3:
#             print("[Server Message] Usage: /send target_client_username file_path ")



    
