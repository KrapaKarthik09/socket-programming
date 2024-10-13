# Import socket module
from socket import *
from time import time
import sys

def ping(serverHost, serverPort):
    # Preparing the socket
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.settimeout(1)
    
    # List to store results
    results = []

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
            rtt = (endTime - startTime) * 1000  # RTT in milliseconds
            
            # Append results as a tuple (sequence number, server response, RTT)
            results.append((i + 1, modifiedMessage.strip(), rtt))
        except timeout:
            print(f"PING {i + 1} Request timed out\n")

    clientSocket.close()
    return results

if __name__ == "__main__":
    # Define server host and port
    if len(sys.argv) != 3:
        print("Usage: python client.py <server_host> <server_port>")
        sys.exit(1)

    serverHost, serverPort = sys.argv[1], int(sys.argv[2])
    response = ping(serverHost, serverPort)
    print("Client Response:", response)
