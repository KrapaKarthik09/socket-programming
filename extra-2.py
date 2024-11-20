from socket import *
import os
import sys
import struct
import time
import select
import pprint

ICMP_ECHO_REQUEST = 8  # ICMP Type
IP_HEADER_SIZE = 20

ICMP_ERROR_TYPES = {
    3: "Destination Unreachable",
    5: "Redirect",
    11: "Time Exceeded",
    12: "Parameter Problem",
    4: "Source Quench",
}

ICMP_ERROR_CODES = {
    3: {
        0: "Net Unreachable,[RFC792]",
        1: "Host Unreachable,[RFC792]",
        2: "Protocol Unreachable,[RFC792]",
        3: "Port Unreachable,[RFC792]",
        4: "Fragmentation Needed and Don't Fragment was Set, [RFC792]",
        5: "Source Route Failed,[RFC792]",
        6: "Destination Network Unknown,[RFC1122]",
        7: "Destination Host Unknown,[RFC1122]",
        8: "Source Host Isolated,[RFC1122]",
        9: "Communication with Destination Network is Administratively Prohibited,[RFC1122]",
        10: "Communication with Destination Host is Administratively Prohibited,[RFC1122]",
        11: "Destination Network Unreachable for Type of Service,[RFC1122]",
        12: "Destination Host Unreachable for Type of Service,[RFC1122]",
        13: "Communication Administratively Prohibited,[RFC1812]",
        14: "Host Precedence Violation,[RFC1812]",
        15: "Precedence cutoff in effect,[RFC1812]",
    },
    4: {0: "No Code"},
    5: {
        0: "Redirect Datagram for the Network (or subnet)",
        1: "Redirect Datagram for the Host",
        2: "Redirect Datagram for the Type of Service and Network",
        3: "Redirect Datagram for the Type of Service and Host",
    },
    11: {0: "Time to Live exceeded in Transit", 1: "Fragment Reassembly Time Exceeded"},
    12: {0: "Pointer indicates the error", 1: "Missing a Required Option", 2: "Bad Length"},
}


def get_icmp_packet(respPacket):
    return struct.unpack_from("bbHHh8s", respPacket, offset=IP_HEADER_SIZE)


def extract_icmp_fields(icmp_pkt):
    return {
        "type": icmp_pkt[0],
        "code": icmp_pkt[1],
        "checksum": icmp_pkt[2],
        "identifier": icmp_pkt[3],
        "sequence_number": icmp_pkt[4],
        "data": icmp_pkt[5],
    }


def get_data_as_double(data):
    return struct.unpack("d", data)[0]


def parse_icmp_error(icmp_type, icmp_code):
    error_type = ICMP_ERROR_TYPES.get(icmp_type, None)
    if error_type is None:
        return "All Good, No Error"
    error_msg = ICMP_ERROR_CODES.get(icmp_type, {}).get(icmp_code, None)
    if error_msg is None:
        return "An Invalid Error Code was Returned, Might be Malicious"
    return f"Error Type: {error_type} with the error: {error_msg}"


def checksum(string):
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0
    while count < countTo:
        thisVal = (string[count + 1]) * 256 + (string[count])
        csum += thisVal
        csum &= 0xFFFFFFFF
        count += 2
    if countTo < len(string):
        csum += (string[len(string) - 1])
        csum &= 0xFFFFFFFF
    csum = (csum >> 16) + (csum & 0xFFFF)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xFFFF
    answer = answer >> 8 | (answer << 8 & 0xFF00)
    return answer


def receiveOnePing(mySocket, ID, timeout, destAddr, sendTime):
    timeLeft = timeout
    while True:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []:  # Timeout
            return (None, None)
        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)

        icmp_pkt = get_icmp_packet(recPacket)
        icmp_fields = extract_icmp_fields(icmp_pkt)
        verdict = parse_icmp_error(icmp_fields["type"], icmp_fields["code"])
        print(f"Parsing For ICMP Results: {verdict}")
        return ((timeReceived - sendTime) * 1000, icmp_fields)
        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return (None, None)


def sendOnePing(mySocket, destAddr, ID):
    myChecksum = 0
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("d", time.time())
    myChecksum = checksum(header + data)
    myChecksum = htons(myChecksum)
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data
    mySocket.sendto(packet, (destAddr, 1))
    return time.time()


def doOnePing(destAddr, timeout):
    icmp = getprotobyname("icmp")
    mySocket = socket(AF_INET, SOCK_RAW, icmp)
    myID = os.getpid() & 0xFFFF
    sendTime = sendOnePing(mySocket, destAddr, myID)
    result = receiveOnePing(mySocket, myID, timeout, destAddr, sendTime)
    mySocket.close()
    return result


def ping(host, timeout=1):
    dest = gethostbyname(host)
    resps = []
    print("Pinging " + dest + " using Python:")
    print("")
    maxRTT = 0
    minRTT = 1001
    avgRTT = 0
    total_pkts_received = 0

    for i in range(0, 5):
        result = doOnePing(dest, timeout)
        resps.append(result)
        currRTT = result[0]
        if currRTT is None:
            continue
        maxRTT = max(currRTT, maxRTT)
        minRTT = min(currRTT, minRTT)
        avgRTT = ((avgRTT * total_pkts_received) + currRTT) / (total_pkts_received + 1)
        total_pkts_received += 1
        time.sleep(1)

    print("PING STATISTICS")
    print(f"Packets Sent: 5 \nPackets Received: {total_pkts_received}")
    print(f"Packet Loss: {str((5 - total_pkts_received) / 100)}%")
    print(f"Maximum RTT: {str(maxRTT)}ms")
    print(f"Minimum RTT: {str(minRTT)}ms")
    return resps


if __name__ == "__main__":
    ping("google.co.il")
