#From the skeleton code let's build the client code
from socket import *
from time import time, ctime
import sys

def ping(host, port):
    resps = [] #List for storing response
    clientSocket = socket(AF_INET, SOCK_DGRAM) #UDP Socket
    clientSocket.settimeout(1)  #setting timeout value of 1s
    
    for seq in range(10):
        startTime = time()  #time capture when ping is sent
        message = f"Ping {seq} {ctime(startTime)[11:19]}"  #ping message
        
        try:
            clientSocket.sendto(message.encode(), (host, port))
            
            encodedModified, serverAddress = clientSocket.recvfrom(1024) #receiving message and measuring RTT
            endTime = time()  #time capture when message is received
            
            server_reply = encodedModified.decode()
            rtt = (endTime - startTime) * 1000  #rtt in ms
            
            print(f"Reply from {serverAddress}: {server_reply}")
            print(f"RTT: {rtt:.3f} ms\n")
            
            resps.append((seq, server_reply, rtt)) #appending to resps list
        
        except timeout:
            print(f"PING {seq} Request timed out\n") 
            resps.append((seq, 'Request timed out', 0))
        
    #Close the client socket after all pings
    clientSocket.close()
    
    return resps

if __name__ == '__main__':
    resps = ping('127.0.0.1', 12000)
    print(resps)
