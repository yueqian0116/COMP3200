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

def check_port_range(port):
    if not port.isdigit():
        invalid_config_file()
    port = int(port) # port is a int
    if port < 1024 or port > 65535:
        invalid_config_file()
    
def invalid_config_file():
    print(f"Error: Invalid configuration file.", file=sys.stderr)
    sys.exit(EXIT_STATUS["INVALID_CONFIG_FILE"])

def check_capacity_range(capacity):
    if not capacity.isdigit():
        invalid_config_file()
    capacity = int(capacity) # port is a int
    if capacity < 1 or capacity > 8:
        invalid_config_file()

def check_config_file(config_file):
    channels = {}
    try:
        with open(config_file, "r") as file:
            for line in file:
                format = line.split()
                if len(format) != 4:
                    invalid_config_file()
                elif format[0] != "channel":
                    print(format[1])
                    invalid_config_file()

                # lets say we have all the arguments
                channel_name = format[1]
                channel_port = format[2]
                channel_capacity = format[3]

                # check for duplicate names
                if channel_name in channels:
                    invalid_config_file()
                else:    
                    channels[channel_name] = {}

                # validity of port
                check_port_range(channel_port)
                channel_port = int(channel_port) # valid port number
                channels[channel_name]["port"] = channel_port

                # validity of capacity
                check_capacity_range(channel_capacity)
                channel_capacity = int(channel_capacity) # valid capacity
                channels[channel_name]["capacity"] = channel_capacity

            
    except Exception:
        invalid_config_file()
    
    return channels


def testing():
    channel = {
        "channel1": "userA",
        "channel2": "userB",
        "channel3": "abc",  # Duplicate value (userA)
    }

    values = list(channel.values())
    print(values)


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
        if argv[1].isdigit():
            usage_error()
        config_file = argv[1]
    
    channels = check_config_file(config_file)
    print(channels)
    

   

    

