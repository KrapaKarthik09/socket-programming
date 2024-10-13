import random
from socket import *
import time
import hashlib
import sys

def serve(port):
    # Create a UDP socket
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('', port))
    
    while True:
        try:
            rand = random.randint(0, 10)
            message, address = serverSocket.recvfrom(1024)
            s_time = time.time()

            if rand < 4:
                # Simulate packet loss
                continue
            
            m = message.decode().split()
            seq = m[1]
            c_time = m[2]
            h = hashlib.md5(f'seq:{seq},c_time:{c_time},s_time:{s_time},key:randomkey'.encode()).hexdigest()

            # Log received message for debugging
            print(f"Received: {m}")

            # Prepare the response
            resp = f'Reply {seq} {c_time} {s_time} {h}\n'
            serverSocket.sendto(resp.encode(), address)

        except KeyboardInterrupt:
            serverSocket.close()
            sys.exit()
        except Exception as e:
            print(f"Error: {e}")
            continue

if __name__ == '__main__':
    serve(12000)
