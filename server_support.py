from socket import *
from sys import stdout,stdin,argv,exit
import sys
import os

#  basically an enum for exit status
EXIT_STATUS = {
    "USAGE": 4,
    "INVALID_CONFIG_FILE": 5,
    "PORT": 6
}

def usage_error():
    print("Usage: chatserver [afk_time] config_file", file=sys.stderr)
    sys.exit(EXIT_STATUS["USAGE"])

def unable_to_listen_port(port_number):
    print(f"Error: unable to listen on port {port_number}.", file=sys.stderr)
    sys.exit(EXIT_STATUS["PORT"])
    
def invalid_config_file():
    print(f"Error: Invalid configuration file.", file=sys.stderr)
    sys.exit(EXIT_STATUS["INVALID_CONFIG_FILE"])

def check_duplicate_port(port: int, channels: dict) -> bool:
    for channel in channels.values():
        if (channel['port'] == port):
            return True
    return False

def check_config_file(config_file):
    channels = {}
    try:
        with open(config_file, "r") as file:
            lines = file.readlines()

            if not lines:
                invalid_config_file()
            for line in lines:
                format = line.split()
                if len(format) != 4:
                    invalid_config_file()

                if format[0] != "channel":
                    invalid_config_file()

                # Retrieve line values
                name = format[1]
                port_str = format[2]
                capacity_str = format[3]

                # Validate channel name
                if name in channels or (not all(c.isalnum() or c == '_' for c in name)):
                    invalid_config_file()

                # Validate channel port
                if not port_str.isdigit():
                    invalid_config_file()
                port = int(port_str)
                if port < 1024 or port > 65535:
                    invalid_config_file()
                if check_duplicate_port(port, channels):
                    invalid_config_file()

                # Validate channel capacity
                if not capacity_str.isdigit():
                    invalid_config_file()
                capacity = int(capacity_str)
                if capacity < 1 or capacity > 8:
                    invalid_config_file()
                
                # Channel validated - add to channels
                channel = {
                    "name": name,
                    "port": port,
                    "capacity": capacity,
                    "users": [],    # initialise user and queue
                    "queue": [],
                    "sockets": {}, # dict: user: socket
                    "q_sockets": {}
                }
                channels[name] = channel         
    except Exception as e:
        invalid_config_file()
    
    return channels


def check_arguments(argv):
    afk_time = 100
    config_file = None
    # check length of args
    if len(argv) != 2 and len(argv) != 3:
        usage_error()

    # check for valid afk_time and config file
    if len(argv) == 3:
        if not argv[1].isdigit():
            usage_error()
        afk_time = int(argv[1])
        # check validity of afk time
        if afk_time < 1 or afk_time > 1000:
            usage_error()
        config_file = argv[2]
        
    # assign config file if there are only 2 args
    if len(argv) == 2:
        config_file = argv[1]
    
    if not config_file or ' ' in config_file:
        usage_error()

    channels = check_config_file(config_file)
    return afk_time, channels

def capacity_reached(channels: dict, name: str) -> bool:
    return len(channels[name]["users"]) >= channels[name]["capacity"] 

def process_message(message: str, client_socket, channels: dict,
        username: str, name:str):
    if message.startswith('/send'):
        token = message.split()
        send_failed = False
        if len(token) != 3:
            reply = "[Server Message] Usage: /send target_client_username file_path\n"
            client_socket.sendall(reply.encode())
        else:
            to_user = token[1]
            filepath = token[2]
            if to_user == username:
                reply = "[Server Message] Cannot send file to yourself.\n"
                client_socket.sendall(reply.encode())
                send_failed = True
            if to_user not in channels[name]["users"]:
                reply = f"[Server Message] {to_user} is not in the channel.\n"
                client_socket.sendall(reply.encode())
                send_failed = True
            if not os.path.exists(filepath) or not os.access(filepath, os.R_OK):
                reply = f"[Server Message] \"{filepath}\" does not exist.\n"
                client_socket.sendall(reply.encode())
                send_failed = True
            # passes all checks for /send
            if not send_failed:
                try:
                    filename = os.path.basename(filepath)
                    filesize = os.path.getsize(filepath)
                    receiver_sock = channels[name]["sockets"][to_user]

                    header = f"FILE {filename} {filesize}\n"
                    receiver_sock.sendall(header.encode())
                    
                    with open(filepath, 'rb') as f:
                        while chunk := f.read(4096):
                            receiver_sock.sendall(chunk)

                    rcved_msg = f"[Server Message] {username} sent \"{filepath}\" to {to_user}.\n"
                    succesful_msg = f"[Server Message] Sent \"{filepath}\" to {to_user}.\n"
                    print(rcved_msg)
                    sys.stdout.flush()
                    client_socket.sendall(succesful_msg.encode())
                    receiver_sock.sendall(rcved_msg.encode())
                except Exception:
                    msg = f"[Server Message] Failed to send \"{filepath}\" to {to_user}\n"
                    client_socket.sendall(msg.encode())
          
    elif message.startswith("/quit"):
        quit_channel(username, channels, name)

    elif message.startswith("/list"): # also apply to q users
        for channel in channels.values():
            msg = f"[Channel] {channel['name']} {channel['port']} "\
                f"Capacity: {len(channel['users'])}/{channel['capacity']}, "\
                    f"Queue: {len(channel['queue'])}\n"
            client_socket.sendall(msg.encode())

    elif message.startswith("/whisper"):
        if not user_in_queue(username, channels, name):
            token = message.split()
            receiver_client = token[1]
            msg_to_send = token[2]
            if not user_in_queue(receiver_client, channels, name) and not user_in_users(receiver_client, channels, name):
                msg = f"[Server Message] {receiver_client} is not in the channel.\n"
                client_socket.sendall(msg.encode())
            else:
                receiver_sock = channels[name]["sockets"][receiver_client]
                msg_to_receiver = f"[{username} whispers to you] {msg_to_send}\n"
                receiver_sock.sendall(msg_to_receiver.encode())
                msg = f"[{username} whispers to {receiver_client}] {msg_to_send}\n"
                client_socket.sendall(msg.encode())
                print(msg, end='')
                sys.stdout.flush()

    elif message.startswith("/switch"):
        token = message.split()
        channel_to_switch = token[1]
        if channel_to_switch not in channels:
            msg = f"[Server Message] Channel \"{channel_to_switch}\" does not exist.\n"
            client_socket.sendall(msg.encode())
        elif username in channels[channel_to_switch]["users"] or \
            username in channels[channel_to_switch]["queue"]:
            msg = f"[Server Message] Channel \"{channel_to_switch}\" already has user {username}.\n"
            client_socket.sendall(msg.encode())
        else:
            quit_channel(username, channels, name)
            join_channel(username, channels, channel_to_switch, client_socket)

    else:    
        broadcast_msg = f"[{username}] {message}"
        if user_in_queue(username, channels, name):
            pass # do ntg
        else:
            broadcast(broadcast_msg, channels, name)
       
# send message to all clients and server
def broadcast(message, channels, name):
    print(message, end='')
    sys.stdout.flush()
    for user in channels[name]["users"]:
            sock = channels[name]["sockets"][user]
            sock.sendall(message.encode())

def quit_channel(username: str, channels: dict, name: str):
    broadcast_msg = f"[Server Message] {username} has left the channel.\n"
    remove_user_from_users(username, channels, name)
    if not user_in_queue(username, channels, name):
        broadcast(broadcast_msg, channels, name)
    else:
        print(broadcast_msg, end='')
        sys.stdout.flush()

def join_channel(username: str, channels: dict, name: str, client_socket):
    if username in channels[name]["users"] or \
        username in channels[name]["queue"]:
            msg = f"[Server Message] Channel \"{name}\" already "\
            f"has user {username}."
            client_socket.sendall(msg.encode())
            return

    if not capacity_reached(channels, name):
        # msg = f"Welcome to chatclient, {username}.\n"
        # client_socket.sendall(msg.encode())
        add_user_to_users(username, channels, name, client_socket)
        message = f"[Server Message] You have joined the channel \"{name}\".\n"
        print(f"[Server Message] {username} has joined the channel \"{name}\".")
        sys.stdout.flush()
    else:
        add_user_to_queue(username, channels, name, client_socket)
        users_in_front = len(channels[name]["queue"]) - 1
        message = f"[Server Message] You are in the waiting queue "\
                    f"and there are {users_in_front} user(s) ahead of you.\n"
    
    client_socket.sendall(message.encode())

def user_in_queue(username: str, channels: dict, name: str) -> bool:
    return username in channels[name]["queue"]

def user_in_users(username: str, channels: dict, name: str) -> bool:
    return username in channels[name]["users"]

def remove_user_from_users(username: str, channels: dict, name: str):
    if username in channels[name]["users"]:
        channels[name]["users"].remove(username)
    if username in channels[name]["sockets"]:
        channels[name]["sockets"].pop(username)
    if channels[name]["queue"] and channels[name]["q_sockets"]: # there is someone in the queue
        userToAdd, socketToAdd = next(iter(channels[name]["q_sockets"].items()))
        add_user_to_users(userToAdd, channels, name, socketToAdd)
        remove_user_from_queue(userToAdd, channels, name)
        message = f"[Server Message] You have joined the channel \"{name}\".\n"
        print(f"[Server Message] {userToAdd} has joined the channel \"{name}\".")
        sys.stdout.flush()
        socketToAdd.sendall(message.encode())

def add_user_to_users(username: str, channels: dict, name: str, client_sock):
    channels[name]["users"].append(username)
    channels[name]["sockets"][username] = client_sock

def add_user_to_queue(username: str, channels: dict, name: str, client_sock):
    channels[name]["queue"].append(username)
    channels[name]["q_sockets"][username] = client_sock 

def remove_user_from_queue(username: str, channels: dict, name: str):
    if username in channels[name]["queue"]:
        channels[name]["queue"].remove(username)
    if username in channels[name]["q_sockets"]:
        channels[name]["q_sockets"].pop(username)  

def check_for_trailing_spaces(line):
    if line.rstrip() != line:
        if line.startswith("/kick"):
            print("Usage: /kick channel_name client_username")
        elif line.startswith("/mute"):
            print("Usage: /mute channel_name client_username duration")
        elif line.startswith("/empty"):
            print("Usage: /empty channel_name")

        sys.stdout.flush()
        return True  # Tell caller to skip further processing
    return False
