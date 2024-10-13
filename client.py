from socket import *
import time
import sys

def ping(host, port):
    resps = []
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.settimeout(1)  # Set timeout for the socket

    for seq in range(1, 11):
        startTime = time.time()  # Get the current time
        message = f"Ping {seq} {startTime:.6f}"  # Create the ping message

        try:
            # Send the message to the server
            clientSocket.sendto(message.encode(), (host, port))

            # Wait for a response from the server
            encodedReply, serverAddress = clientSocket.recvfrom(1024)
            endTime = time.time()  # Get the end time after receiving response

            # Decode the server's reply
            server_reply = encodedReply.decode()

            # Calculate round trip time (RTT)
            rtt = (endTime - startTime) * 1000  # Convert to milliseconds

            # Append successful response to results
            resps.append((seq, server_reply.strip(), rtt))

        except timeout:
            # If a timeout occurs, append the timeout message
            resps.append((seq, 'Request timed out', 0))

    clientSocket.close()  # Close the socket
    return resps

if __name__ == '__main__':
    # Usage: python client.py <server_host> <server_port>
    if len(sys.argv) != 3:
        print("Usage: python client.py <server_host> <server_port>")
        sys.exit(1)

    serverHost, serverPort = sys.argv[1], int(sys.argv[2])
    responses = ping(serverHost, serverPort)
    print(responses)
