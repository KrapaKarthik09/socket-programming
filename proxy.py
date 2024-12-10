from socket import *
import sys
import os
import shutil
import select

cacheDir = os.path.join(os.path.dirname(__file__), 'cache')

def wait_interruptible(waitable, timeLeft):
    while True:
        ready = select.select([waitable], [], [], timeLeft)
        if len(ready[0]) > 0:
            return

def interruptible_accept(socket):
    wait_interruptible(socket, 5)
    return socket.accept()

def interruptible_recv(socket, nbytes):
    wait_interruptible(socket, 5)
    return socket.recv(nbytes)

def interruptible_readline(fileObj):
    wait_interruptible(fileObj, 5)
    return fileObj.readline()

def interruptible_read(fileObj, nbytes=-1):
    wait_interruptible(fileObj, 5)
    return fileObj.read(nbytes)

def parse_http_headers(sockf):
    headline = interruptible_readline(sockf).decode().strip()
    headers = []
    while True:
        header = interruptible_readline(sockf).decode()
        if len(header.rstrip('\r\n')) == 0:
            break
        headerPartitions = header.partition(':')
        if headerPartitions[1] == '':
            continue
        headers.append((headerPartitions[0].strip(), headerPartitions[2].strip()))
    return(headline, headers)

def forward_and_cache_response(sockf, fileCachePath, clisockf):
    cachef = None
    if fileCachePath is not None:
        os.makedirs(os.path.dirname(fileCachePath), exist_ok=True)
        cachef = open(fileCachePath, 'w+b')

    try:
        statusLine, headers = parse_http_headers(sockf)
        headers = [h for h in headers if h[0] != 'Connection']
        headers.append(('Connection', 'close'))
        # Fill in start.
        clisockf.write(f"{statusLine}\r\n".encode())
        for header in headers:
            clisockf.write(f"{header[0]}: {header[1]}\r\n".encode())
        clisockf.write(b"\r\n")
        
        while True:
            data = interruptible_read(sockf,4096)
            if not data:
                break
            clisockf.write(data)
            if cachef:
                cachef.write(data)
        # Fill in end.
    except Exception as e:
        print(e)
    finally:
        if cachef is not None:
            cachef.close()

def forward_request(sockf, requestUri, hostn, origRequestLine, origHeaders):
    headers = [h for h in origHeaders if h[0] != 'Host']
    headers.append(('Host', hostn))
    # Fill in start.
    sockf.write(f"{origRequestLine}\r\n".encode())
    for header in headers:
        sockf.write(f"{header[0]}: {header[1]}\r\n".encode())
    sockf.write(b"\r\n")
    # Fill in end.

def proxyServer(port):
    if os.path.isdir(cacheDir):
        shutil.rmtree(cacheDir)
    tcpSerSock = socket(AF_INET, SOCK_STREAM)

    # Fill in start.
    tcpSerSock.bind(('', port))
    tcpSerSock.listen(1)
    # Fill in end.

    tcpCliSock = None
    try:
        while 1:
            print('Ready to serve...')
            tcpCliSock, addr = interruptible_accept(tcpSerSock)

            print('Received a connection from:', addr)
            cliSock_f = tcpCliSock.makefile('rwb', 0)

            requestLine, requestHeaders = parse_http_headers(cliSock_f)
            print(requestLine)

            if len(requestLine) == 0:
                continue

            requestUri = requestLine.split()[1]
            uri_parts = requestUri.partition('http://')
            if uri_parts[1] == '':
                filename = requestUri.partition('/')[2]
            else:
                filename = uri_parts[2]

            print(f'filename: {filename}')

            if len(filename) > 0:
                method = requestLine.split()[0]
                if method == "GET":
                    fileCachePath = os.path.join(cacheDir, filename.replace('/', '_'))
                    cached = os.path.exists(fileCachePath)
                else:
                    fileCachePath = None
                    cached = False

                print(f'fileCachePath: {fileCachePath}')

                if fileCachePath is not None and cached:
                    # Fill in start.
                    with open(fileCachePath, 'rb') as cache_file:
                        cliSock_f.write(cache_file.read())
                    # Fill in end.
                    print('Read from cache')
                else:
                    c = socket(AF_INET, SOCK_STREAM)  # Fill in start.
                    hostn = filename.partition('/')[0]
                    print(f'hostn: {hostn}')

                    try:
                        # Fill in start.
                        c.connect((hostn.split(':')[0], int(hostn.split(':')[1])))
                        # Fill in end.

                        fileobj = c.makefile('rwb', 0)
                        forward_request(fileobj, f'/{filename.partition("/")[2]}', hostn, requestLine, requestHeaders)

                        forward_and_cache_response(fileobj, fileCachePath, cliSock_f)
                    except Exception as e:
                        print(e)
                    finally:
                        c.close()
            tcpCliSock.close()
    except KeyboardInterrupt:
        pass

    # Fill in start.
    tcpSerSock.close()
    # Fill in end.
    sys.exit()

if __name__ == "__main__":
    proxyServer(8888)
