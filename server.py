from socket import *
import sys

def webServer(port):
    serverPort = port
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('',serverPort))
    serverSocket.listen(1) #server begins listening for incoming requests
    print('Server being set up...')

    while True:
        print ('Server is ready !')
        connectionSocket, addr = serverSocket.accept() #server waits on accept new socket returned on request
        print('Request accepted from:', addr)
        try:
            message = connectionSocket.recv(1024).decode()
            filename = message.split()[1]
            f = open(filename[1:],'r')
            outputdata = f.read()

            headerLine = 'HTTP/1.1 200 OK\r\n'
            connectionSocket.send(headerLine.encode())
            connectionSocket.send('\r\n'.encode())

            for i in range(0, len(outputdata)):
                connectionSocket.send(outputdata[i].encode())
            connectionSocket.send('\r\n'.encode())

            connectionSocket.close()
        
        except IOError:
            errHeaderLine = 'HTTP/1.1 404 Not Found\r\n'  #r for carriage return and n for new line
            connectionSocket.send(errHeaderLine.encode())
            connectionSocket.send('\r\n'.encode())
            f2 = open('404page.html','r')
            outputdata_err = f2.read()

            for i in range(0, len(outputdata_err)):
                connectionSocket.send(outputdata_err[i].encode())
            connectionSocket.send('\r\n'.encode())
            connectionSocket.close()
        
        serverSocket.close()
        sys.exit()


if __name__ == '__main__':
    webServer(6879)




