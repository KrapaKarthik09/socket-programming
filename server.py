from socket import *
import sys  # In order to terminate the program

def webServer(port):
    serverPort = port 
    serverSocket = socket(AF_INET, SOCK_STREAM)  # server socket - TCP byte stream
    serverSocket.bind(('', serverPort))  # binding port to server port
    serverSocket.listen(1)  # server begins listening for incoming requests
    print('Server being set up...')

    while True:  # Keep the server running
        print('Ready to serve...')
        connectionSocket, addr = serverSocket.accept()  # Accept a new connection
        print('Request accepted from:', addr)
        try:
            message = connectionSocket.recv(1024).decode()  # Decode the received message
            filename = message.split()[1]  # Extract the filename
            with open(filename[1:], 'r') as f:  # Open the requested file
                outputdata = f.read()

            headerLine = 'HTTP/1.1 200 OK\r\n'
            connectionSocket.send(headerLine.encode())  # Send HTTP response header
            connectionSocket.send("Content-Type: text/html\r\n".encode())
            connectionSocket.send('\r\n'.encode())  # End of headers

            connectionSocket.send(outputdata.encode())  # Send the file content
            connectionSocket.close()  # Close the connection to this client
        
        except IOError:
            # Handle the case where the file is not found
            errHeaderLine = 'HTTP/1.1 404 Not Found\r\n'
            connectionSocket.send(errHeaderLine.encode())
            connectionSocket.send('\r\n'.encode())
            with open('404page.html', 'r') as f2:  # Open the 404 error page
                outputdata_err = f2.read()
                connectionSocket.send(outputdata_err.encode())  # Send the error page
            connectionSocket.close()  # Close the connection to this client

# Removed the closing of serverSocket and sys.exit()

if __name__ == '__main__':
    webServer(6879)