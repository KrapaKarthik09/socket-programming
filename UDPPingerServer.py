import random
from socket import *
import time
import hashlib
import sys

def serve(port, timeout=10):  
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('', port))  # Bind to all interfaces on the specified port
    
    # Set a timeout for the server socket to avoid indefinite waiting
    serverSocket.settimeout(timeout)
    
    print(f"Server is running on port {port} with {timeout} seconds timeout.")
    
    while True:
        try:
            rand = random.randint(0, 10)
            print("Waiting for a message...")  # Debug message
            
            # Try receiving the client message
            message, address = serverSocket.recvfrom(1024)  # This blocks till data is received or times out
            print(f"Received message from {address}: {message.decode()}")  # Print received message
            
            s_time = time.time()
            if rand < 4:
                print("Simulating packet loss. Ignoring message.")
                continue
            
            # Decode message and construct server reply
            m = message.decode().split()
            seq = m[1]
            c_time = m[2]
            h = hashlib.md5(f'seq:{seq},c_time:{c_time},s_time:{s_time},key:randomkey'.encode()).hexdigest()

            # Reply format: "Reply <sequence_number> <client_time> <server_time> <message_digest>"
            resp = f'Reply {seq} {c_time} {s_time} {h}\n'
            serverSocket.sendto(resp.encode(), address)
        
        except timeout:
            print("Server timed out waiting for messages. Closing server.")
            break  # Exit the while loop after timeout

        except Exception as e:
            print(f"An error occurred: {e}")
            break  # Exit on unexpected error

if __name__ == '__main__':
    serve(12000, timeout=15)  # Setting a 15-second timeout for the server