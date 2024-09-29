from socket import *
import sys  # In order to terminate the program

def webServer(port):
    serverPort = port 
    serverSocket = socket(AF_INET, SOCK_STREAM)  # server socket - TCP byte stream
    serverSocket.bind(('', serverPort))  # binding port to server port
    serverSocket.listen(1)  # server begins listening for incoming requests
    print('Server being set up...')

    while True:
        print('Ready to serve...')
        connectionSocket, addr = serverSocket.accept()  # server waits on accept new socket returned on request as this is TCP
        print('Request accepted from:', addr)
        try:
            message = connectionSocket.recv(1024).decode()  # decodes the received byte stream message
            filename = message.split()[1]
            with open(filename[1:], 'r') as f:  # Use 'with' to automatically close the file
                outputdata = f.read()

            headerLine = 'HTTP/1.1 200 OK\r\n'
            connectionSocket.send(headerLine.encode())  # encoding to send back
            connectionSocket.send("Content-Type: text/html\r\n".encode())
            connectionSocket.send('\r\n'.encode())  # end of headers

            connectionSocket.send(outputdata.encode())  # Send entire output data at once
            connectionSocket.close()
        
        except IOError:
            errHeaderLine = 'HTTP/1.1 404 Not Found\r\n'
            connectionSocket.send(errHeaderLine.encode())
            connectionSocket.send('\r\n'.encode())
            with open('404page.html', 'r') as f2:  # Use 'with' for error page as well
                outputdata_err = f2.read()
                connectionSocket.send(outputdata_err.encode())  # Send entire error page at once
            connectionSocket.close()

if __name__ == '__main__':
    webServer(6879)
