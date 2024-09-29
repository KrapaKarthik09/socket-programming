from socket import *
import sys

if (len(sys.argv) != 4): #For arguments to the script so that client can connect to server
    print('Incorrect number of arguments.')
    print('Help: To run python client.py <server_host> <server_port> <filename>')
    sys.exit()

serverHost, serverPort, filename = sys.argv[1:] #server arguments
clientSocket = socket(AF_INET, SOCK_STREAM)
try:
    clientSocket.connect((serverHost, int(serverPort))) #client connecting to server
except:
    print('The server is currently inactive')
    clientSocket.close() #close connection if inactive
    sys.exit()
print('Connection OK.')

httpRequest = 'GET /' + filename + ' HTTP/1.1\r\n\r\n' #HTTP Request
clientSocket.send(httpRequest.encode())
print('Request message sent.')

print('Server HTTP Response:\r\n')

data = ""
while True:
    clientSocket.settimeout(5)
    newData = clientSocket.recv(1024).decode()
    data += newData
    if (len(newData) == 0):
        break
print(data)

print('Closing socket') #Closing socket
clientSocket.close()