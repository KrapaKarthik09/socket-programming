from socket import *
from time import time, ctime
import sys

def ping(serverHost, serverPort):
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.settimeout(1)

    results = []

    for i in range(10):
        startTime = time()
        message = f"Ping {i + 1} {startTime:.6f}"

        try:
            clientSocket.sendto(message.encode(), (serverHost, serverPort))
            encodedModified, serverAddress = clientSocket.recvfrom(1024)
            endTime = time()

            modifiedMessage = encodedModified.decode()
            rtt = (endTime - startTime) * 1000
            
            # Append results to list
            results.append((i + 1, modifiedMessage.strip(), rtt))
        except timeout:
            print(f"PING {i + 1} Request timed out")

    clientSocket.close()
    return results

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python client.py <server_host> <server_port>")
        sys.exit(1)

    serverHost, serverPort = sys.argv[1], int(sys.argv[2])
    response = ping(serverHost, serverPort)
    print("Client Response:", response)
