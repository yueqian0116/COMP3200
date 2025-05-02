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
    
def invalid_config_file(error: str = "Unknown"):
    print(f"Error: Invalid configuration file - {error}", file=sys.stderr)
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
            for line in file:
                format = line.split()
                if len(format) != 4:
                    invalid_config_file("Invalid line length")

                if format[0] != "channel":
                    invalid_config_file("Malformed line, missing 'channel'")

                # Retrieve line values
                name = format[1]
                port_str = format[2]
                capacity_str = format[3]

                # Validate channel name
                if name in channels:
                    invalid_config_file("Duplicate channel name")

                # Validate channel port
                if not port_str.isdigit():
                    invalid_config_file("Port is not a number")
                port = int(port_str)
                if port < 1024 or port > 65535:
                    invalid_config_file("Port not in range")
                if check_duplicate_port(port, channels):
                    invalid_config_file("Duplicate port value")

                # Validate channel capacity
                if not capacity_str.isdigit():
                    invalid_config_file("Capacity is not a number")
                capacity = int(capacity_str)
                if capacity < 1 or capacity > 8:
                    invalid_config_file("Capacity not in range")
                
                # Channel validated - add to channels
                channel = {
                    "name": name,
                    "port": port,
                    "capacity": capacity
                }
                channels[name] = channel


            
    except Exception as e:
        print(e)
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
    # print(channels)
    return afk_time, channels
    

   

    

