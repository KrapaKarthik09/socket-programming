# Import socket module
# Import time and ctime to retrieve time
from socket import *
from time import time
import sys

# Define server host and port
serverHost = 'localhost'  # or '127.0.0.1'
serverPort = 12000  # Specify your server port here

# Preparing the socket
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.settimeout(1)

for i in range(10):
    startTime = time()  # Retrieve the current time
    message = f"Ping {i + 1} {startTime:.6f}"  # Include time in seconds

    try:
        # Sending the message and waiting for the answer
        clientSocket.sendto(message.encode(), (serverHost, serverPort))
        encodedModified, serverAddress = clientSocket.recvfrom(1024)

        # Checking the current time and if the server answered
        endTime = time()
        modifiedMessage = encodedModified.decode()
        print(modifiedMessage)
        print("RTT: %.3f ms\n" % ((endTime - startTime) * 1000))
    except timeout:
        print("PING %i Request timed out\n" % (i + 1))

clientSocket.close()
