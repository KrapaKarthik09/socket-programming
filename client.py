# Import socket module
# Import time to retrieve current time
from socket import *
import time
import sys

def ping(host, port):
    resps = []
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.settimeout(1)

    for seq in range(1, 11):
        startTime = time.time()  # Retrieve the current time
        message = "Ping {} {}".format(seq, startTime)

        try:
            # Sending the message and waiting for the answer
            clientSocket.sendto(message.encode(), (host, port))
            encodedModified, serverAddress = clientSocket.recvfrom(1024)

            # Checking the current time and if the server answered
            endTime = time.time()
            modifiedMessage = encodedModified.decode()
            rtt = (endTime - startTime) * 1000  # Convert to milliseconds
            resps.append((seq, modifiedMessage, rtt))
        except timeout:
            resps.append((seq, 'Request timed out', 0))

    clientSocket.close()
    return resps

if __name__ == '__main__':
    resps = ping('127.0.0.1', 12000)
    print(resps)
