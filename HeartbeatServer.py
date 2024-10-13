from socket import *
import time
import sys

def serve(port, heartbeat_timeout=5):
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('', port))
    last_seq = -1  # to keep track of sequence number for detecting lost packets
    last_heartbeat_time = time.time()  # the last heartbeat was received time

    print("Server is ready to receive heartbeat signals.")
    
    while True:
        try:
            message, address = serverSocket.recvfrom(1024)
            current_time = time.time()
            heartbeat = message.decode().split()  # heartbeat message decode
            seq = int(heartbeat[1])
            c_time = float(heartbeat[2])

            print(f"Received Heartbeat {seq} from {address} at {current_time}, sent at {c_time}")

            if seq != last_seq + 1 and last_seq != -1:  # checking packet loss
                print(f"Warning: Packet loss detected! Expected seq {last_seq + 1}, but got {seq}.")

            if current_time - last_heartbeat_time > heartbeat_timeout:  # checking heartbeat timeout
                print("Warning: Heartbeat timeout. Client may have stopped.")
            
            # Updating last sequence number and heartbeat time
            last_seq = seq
            last_heartbeat_time = current_time

        except KeyboardInterrupt:
            serverSocket.close()
            sys.exit()

if __name__ == '__main__':
    serve(12000)
