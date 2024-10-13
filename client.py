from socket import *
from time import time
import sys

def ping(host, port):
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.settimeout(1)  # Timeout set to 1 second for each ping
    
    for seq in range(1, 11):  # Sequence numbers from 1 to 10
        startTime = time()  # Current time in seconds (floating-point)
        message = f"Ping {seq} {startTime}"  # Message format
        
        try:
            # Send the message
            clientSocket.sendto(message.encode(), (host, port))
            
            # Receive the reply from the server
            encodedModified, serverAddress = clientSocket.recvfrom(1024)
            endTime = time()  # Time when response is received

            # Decode and parse the server response
            server_reply = encodedModified.decode()

            # Calculate RTT (in seconds)
            rtt = endTime - startTime

            # Print the server reply and RTT
            print(f"Reply from {serverAddress}: {server_reply}")
            print(f"RTT: {rtt:.6f} seconds\n")  # RTT in floating-point seconds (6 decimal places)

        except timeout:
            # Handle case where server does not respond
            print(f"PING {seq} Request timed out\n")

    # Close the socket after all pings
    clientSocket.close()

# Run the ping function if this script is executed directly
if __name__ == '__main__':
    ping('127.0.0.1', 12000)  # Test by pinging localhost (127.0.0.1)
