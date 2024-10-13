# Import socket module
# Import time and ctime to retrieve time
# Import sys to retrieve the arguments
from socket import *
from time import time, ctime
import sys

def main(serverHost, serverPort):
    # Preparing the socket
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.settimeout(1)

    for i in range(10):
        startTime = time()  # Retrieve the current time
        message = f"Ping {i + 1} {ctime(startTime)[11:19]}"

        try:
            # Sending the message and waiting for the answer
            clientSocket.sendto(message.encode(), (serverHost, int(serverPort)))
            encodedModified, serverAddress = clientSocket.recvfrom(1024)

            # Checking the current time and if the server answered
            endTime = time()
            modifiedMessage = encodedModified.decode()
            print(modifiedMessage)
            print("RTT: %.3f ms\n" % ((endTime - startTime) * 1000))
        except timeout:
            print(f"PING {i + 1} Request timed out\n")

    clientSocket.close()

if __name__ == '__main__':
    # Checking to see if we have three arguments
    if len(sys.argv) != 3:
        print("Wrong number of arguments.")
        print("Use: client.py <server_host> <server_port>")
    else:
        serverHost, serverPort = sys.argv[1:]
        main(serverHost, serverPort)
