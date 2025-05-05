from socket import *
from sys import stdout,stdin,argv,exit
import sys

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
                    "sockets": {} # dict: user: socket
                }
                channels[name] = channel         
    except Exception as e:
        invalid_config_file()
    
    return channels


# def testing():
#     channel = {
#         "channel1": "userA",
#         "channel2": "userB",
#         "channel3": "abc",  # Duplicate value (userA)
#     }

#     values = list(channel.values())
#     print(values)


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
    # print(channels)
    return afk_time, channels

def capacity_reached(channels: dict, name: str) -> bool:
    return len(channels[name]["users"]) >= channels[name]["capacity"] 

def process_message(message: str, client_socket, channels: dict,
        username: str, name:str):
    if message.startswith('/'):
        # parse commands
        print("This is a command")
        sys.stdout.flush()
    
    broadcast_msg = f"[{username}] {message}"
    print(broadcast_msg, end='')
    sys.stdout.flush()
    for user in channels[name]["users"]:
        sock = channels[name]["sockets"][user]
        sock.sendall(broadcast_msg.encode())

