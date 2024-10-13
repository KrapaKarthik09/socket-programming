import random
from socket import *
import time
import hashlib
import sys

def serve(port):
    # Create a UDP socket
    # Notice the use of SOCK_DGRAM for UDP packets
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    # Assign IP address and port number to socket
    serverSocket.bind(('', port))
    print(f"Server listening on port {port}")

    while True:
        try:
            # Generate random number in the range of 0 to 10
            rand = random.randint(0, 10)

            # Receive the client packet along with the address it is coming from
            message, address = serverSocket.recvfrom(1024)
            s_time = time.time()

            # If rand is less than 4, we consider the packet lost and do not respond
            if rand < 4:
                print(f"Packet lost: {message.decode()}")  # Log lost packet
                continue

            # Decode the message and extract sequence and client time
            m = message.decode().split()
            seq = m[1]
            c_time = m[2]

            # Create a message digest (MD5 hash) using the provided format
            key = 'randomkey'  # Use the actual secret key for grading
            h = hashlib.md5(f'seq:{seq},c_time:{c_time},s_time:{s_time},key:{key}'.encode()).hexdigest()

            # Prepare the response
            resp = f'Reply {seq} {c_time} {s_time} {h}\n'

            # Send the response to the client
            serverSocket.sendto(resp.encode(), address)
            print(f"Responded to {address}: {resp.strip()}")  # Log response

        except KeyboardInterrupt:
            print("Server shutting down...")
            serverSocket.close()
            sys.exit()
        except Exception as e:
            print(f"An error occurred: {e}")
            continue

if __name__ == '__main__':
    serve(12000)  # Start the server on port 12000
