from socket import *
from sys import exit,stdout,stdin,stderr, argv

BUFSIZE = 1024

# Get port from command line arguments
if len(argv) != 3:
    print(f"Usage: python3 {argv[0]} hostname port", file=stderr)
    exit(1)

hostname = argv[1]
port = int(argv[2])

# Create a UDP socket
sock = socket(AF_INET, SOCK_DGRAM)

serverAddr = getaddrinfo(hostname, port, AF_INET, SOCK_DGRAM)

for line in stdin:
    sock.sendto(line.encode(), serverAddr[0][4])

    # Receive data
    data, _ = sock.recvfrom(BUFSIZE)

    # Print the response
    stdout.buffer.write(data);
    stdout.flush();

# Close the socket when done
sock.close();
