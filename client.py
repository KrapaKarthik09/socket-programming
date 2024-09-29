from socket import *
import sys

if (len(sys.argv) != 4):
    print('Incorrect number of arguments.')
    print('Help: client.py <server_host> <server_port> <filename>')
    sys.exit()

serverHost, serverPort, filename = sys.argv[1:]
clientSocket = socket(AF_INET, SOCK_STREAM)
try:
    clientSocket.connect((serverHost, int(serverPort)))
except:
    print('The server is currently inactive')
    clientSocket.close()
    sys.exit()
print('Connection OK.')

#HTTP Request
httpRequest = 'GET /' + filename + ' HTTP/1.1\r\n\r\n'
clientSocket.send(httpRequest.encode())
print('Request message sent.')

#Recieving the response
print('Server HTTP Response:\r\n')

data = ""
while True:
    clientSocket.settimeout(5)
    newData = clientSocket.recv(1024).decode()
    data += newData
    if (len(newData) == 0):
        break
print(data)

#Closing socket
print('Closing socket')
clientSocket.close()