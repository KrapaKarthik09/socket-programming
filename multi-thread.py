from socket import *
import sys
import threading

def handle_client(connectionSocket):
    try:
        message = connectionSocket.recv(1024).decode()
        filename = message.split()[1]
        f = open(filename[1:], 'r')
        outputdata = f.read()

        headerLine = 'HTTP/1.1 200 OK\r\n'
        connectionSocket.send(headerLine.encode())
        connectionSocket.send('\r\n'.encode())

        for char in outputdata:
            connectionSocket.send(char.encode())
        connectionSocket.send('\r\n'.encode())

        connectionSocket.close()
    
    except IOError:
        errHeaderLine = 'HTTP/1.1 404 Not Found\r\n'
        connectionSocket.send(errHeaderLine.encode())
        connectionSocket.send('\r\n'.encode())
        f2 = open('404page.html', 'r')
        outputdata_err = f2.read()

        for char in outputdata_err:
            connectionSocket.send(char.encode())
        connectionSocket.send('\r\n'.encode())
        connectionSocket.close()

def webServer(port):
    serverPort = port
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('', serverPort))
    serverSocket.listen(5) #this is for multiple connections - 5
    print('Server being set up...')

    while True:
        print('Server is ready!')
        connectionSocket, addr = serverSocket.accept()
        print('Request accepted from:', addr)
        
        client_thread = threading.Thread(target=handle_client, args=(connectionSocket,))#Creating a new thread for each connection
        client_thread.start()

if __name__ == '__main__':
    webServer(6879)
