from socket import *
from time import time, ctime
import sys

def ping(host, port):
    rtts = []  # to store the RTTs
    packet_loss_count = 0  # packet lost counter

    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.settimeout(1)

    for seq in range(1, 11):
        startTime = time()  
        message = f"Ping {seq} {ctime(startTime)[11:19]}"  

        try:
            clientSocket.sendto(message.encode(), (host, port))

            encodedModified, serverAddress = clientSocket.recvfrom(1024)
            endTime = time()  

            server_reply = encodedModified.decode()
            rtt = (endTime - startTime) * 1000  # RTT in ms
            rtts.append(rtt)  # storing the RTT in list for getting stat report on this

            print(f"Reply from {serverAddress}: {server_reply}")
            print(f"RTT: {rtt:.3f} ms\n")

        except timeout:
            print(f"PING {seq} Request timed out\n")
            packet_loss_count += 1

    # Closing client
    clientSocket.close()

    # RTT stats
    if rtts:
        print("UDP Pinger Report:")
        print(f"Maximum RTT: {max(rtts):.3f} ms")  # max value from the list
        print(f"Minimum RTT: {min(rtts):.3f} ms")  # min value from the list
        print(f"Average RTT: {sum(rtts) / len(rtts):.3f} ms")  # avg calculation from the list
    else:
        print("No successful pings, all requests timed out.")
    
    # Calculating Packet Loss Rate
    total_packets = 10  # since 10 pings were made from the client skeleton code earlier
    packet_loss_rate = (packet_loss_count / total_packets) * 100
    print(f"Packet loss rate: {packet_loss_rate:.2f}%")

if __name__ == '__main__':
    ping('127.0.0.1', 12000)
