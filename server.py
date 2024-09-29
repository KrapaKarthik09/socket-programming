from socket import *
import sys # In order to terminate the program

def webServer(port):
    serverPort = port 
    serverSocket = socket(AF_INET, SOCK_STREAM)#server socket - TCP byte stream
    serverSocket.bind(('',serverPort)) #binding port to server port
    serverSocket.listen(1) #server begins listening for incoming requests
    print('Server being set up...')

    while True:
        print ('Ready to serve...')
        connectionSocket, addr = serverSocket.accept() #server waits on accept new socket returned on request as this is TCP
        print('Request accepted from:', addr)
        try:
            message = connectionSocket.recv(1024).decode() #decodes the received byte stream message
            filename = message.split()[1]
            f = open(filename[1:],'r')
            outputdata = f.read()

            headerLine = 'HTTP/1.1 200 OK\r\n' #header line containing response status code and status phrase
            connectionSocket.send(headerLine.encode()) #encoding to send back
            connectionSocket.send('\r\n'.encode()) #carriage return otherwise the headers won't be displayed

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




