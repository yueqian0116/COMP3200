from socket import *
from sys import stdout,stdin,argv,exit
import sys

#  basically an enum for exit status
EXIT_STATUS = {
    "USAGE": 4,
    "INVALID_CONFIG_FILE": 5,
    "PORT": 6,
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

def check_config_file(config_file):
    print("hello")    

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

    # assign config file if there are only 2 args
    if len(argv) == 2:
        if argv[1].isdigit():
            usage_error()
        config_file = argv[1]
    
    check_config_file(config_file)
    

   

    

