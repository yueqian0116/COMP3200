from socket import *
from sys import exit,stderr,argv

BUFIZE = 1024

# Get port from command line arguments
if len(argv) != 2:
    print("Usage: python3 udp_server.py <port>", file=stderr)
    exit(1)

port = int(argv[1])

# Create a UDP socket
sock = socket(AF_INET, SOCK_DGRAM)
sock.bind(("", port))

print(f"UDP server listening on port {port}")

while True:
    # Receive data
    data, client_addr = sock.recvfrom(BUFIZE)
    text = data.decode()
    print(f"Received: {text}", end="")
    
    # Capitalize text
    capitalized_text = text.upper()
    
    # Send response back
    sock.sendto(capitalized_text.encode(), client_addr)
