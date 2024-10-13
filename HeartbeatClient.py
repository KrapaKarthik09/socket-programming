from socket import *
import time
import sys

def heartbeat(host, port, interval=2):
    seq = 0  # Sequence number for heartbeat messages

    clientSocket = socket(AF_INET, SOCK_DGRAM)

    while True:
        try:
            current_time = time.time()  # Current time
            message = f"Heartbeat {seq} {current_time}"

            # Sending heartbeat to server
            clientSocket.sendto(message.encode(), (host, port))

            print(f"Sent Heartbeat {seq} at {current_time}")
            seq += 1

            # Wait for the specified interval before sending the next heartbeat
            time.sleep(interval)

        except KeyboardInterrupt:
            print("Stopping the heartbeat client.")
            clientSocket.close()
            sys.exit()

if __name__ == '__main__':
    heartbeat('127.0.0.1', 12000)
