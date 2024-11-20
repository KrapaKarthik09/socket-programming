from socket import *
import os
import sys
import struct
import time
import select

ICMP_ECHO_REQUEST = 8  # ICMP Type
IP_HEADER_SIZE = 20    #Standard size

def checksum(string):
    csum = 0 #initialize checksum
    countTo = (len(string) // 2) * 2
    count = 0
    while count < countTo:
        thisVal = (string[count + 1]) * 256 + (string[count])
        csum += thisVal
        csum &= 0xffffffff #Keeping checksum within 32 bytes
        count += 2
    if countTo < len(string):
        csum += (string[len(string) - 1])
        csum &= 0xffffffff
    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def receiveOnePing(mySocket, ID, timeout, destAddr):
    timeLeft = timeout  #setting timeout value
    while True:
        startedSelect = time.time() #start time
        whatReady = select.select([mySocket], [], [], timeLeft) #incoming data
        howLongInSelect = (time.time() - startedSelect) #time spent
        if whatReady[0]==[]:  # Timeout
            return (None, None)
        timeReceived = time.time() #packet received time
        recPacket, addr = mySocket.recvfrom(1024) #receive packet and sender's address

        #Extract ICMP header fields from the received packet
        #fill in start
        icmpHeader = recPacket[IP_HEADER_SIZE:IP_HEADER_SIZE + 8]
        icmpType, icmpCode, checksum, packetID, sequence = struct.unpack("bbHHh", icmpHeader)
        if packetID == ID:
            #Extract the data payload
            data = recPacket[IP_HEADER_SIZE + 8:]
            sendTimestamp = struct.unpack("d", data)[0]
            return ((timeReceived - sendTimestamp) * 1000,  #RTT in ms
                    (icmpType, icmpCode, checksum, packetID, sequence, sendTimestamp))
        #fill in end
        timeLeft -= howLongInSelect
        if timeLeft <= 0:
            return (None, None)

def sendOnePing(mySocket, destAddr, ID):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    myChecksum = 0
    # Create dummy header with 0 checksum
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("d", time.time())
    # Calculate checksum on header + data
    myChecksum = checksum(header + data)
    # Put checksum into the header
    if sys.platform == 'darwin':
        myChecksum = htons(myChecksum) & 0xffff  # Convert for MacOS
    else:
        myChecksum = htons(myChecksum)
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data
    mySocket.sendto(packet, (destAddr, 1))  # Destination must be tuple
    return time.time()  # Return send time to calculate RTT later

def doOnePing(destAddr, timeout):
    icmp = getprotobyname("icmp")
    mySocket = socket(AF_INET, SOCK_RAW, icmp)
    myID = os.getpid() & 0xFFFF  # Get process ID for unique identifier
    sendOnePing(mySocket, destAddr, myID)
    result = receiveOnePing(mySocket, myID, timeout, destAddr)
    mySocket.close()
    return result

def ping(host, timeout=1):
    dest = gethostbyname(host)
    resps = []
    print("Pinging " + dest + " using Python:")
    print("")
    for i in range(5):  # Send 5 pings
        result = doOnePing(dest, timeout)
        resps.append(result)
        time.sleep(1)
    print(resps)
    return resps

if __name__ == '__main__':
    ping("google.com")
