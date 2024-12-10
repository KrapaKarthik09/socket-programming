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
    return (headline, headers)

def forward_and_cache_response(sockf, fileCachePath, clisockf):
    cachef = None
    if fileCachePath is not None:
        os.makedirs(os.path.dirname(fileCachePath), exist_ok=True)
        cachef = open(fileCachePath, 'w+b')
    try:
        statusLine, headers = parse_http_headers(sockf)
        headers = [h for h in headers if h[0].lower() != 'connection']
        headers.append(('Connection', 'close'))

        clisockf.write(f"{statusLine}\r\n".encode())
        for header in headers:
            clisockf.write(f"{header[0]}: {header[1]}\r\n".encode())
        clisockf.write(b"\r\n")

        while True:
            data = interruptible_read(sockf, 4096)
            if not data:
                break
            clisockf.write(data)
            if cachef:
                cachef.write(data)
    except Exception as e:
        print(e)
    finally:
        if cachef is not None:
            cachef.close()

def forward_request(sockf, requestUri, hostn, origRequestLine, origHeaders, method, body=None):
    headers = [h for h in origHeaders if h[0].lower() != 'host']
    headers.append(('Host', hostn))

    sockf.write(f"{origRequestLine}\r\n".encode())
    for header in headers:
        sockf.write(f"{header[0]}: {header[1]}\r\n".encode())
    
    if method == "POST":
        sockf.write(f"Content-Length: {len(body)}\r\n".encode())
    
    sockf.write(b"\r\n")
    
    if method == "POST" and body:
        sockf.write(body)

def proxyServer(port):
    if os.path.isdir(cacheDir):
        shutil.rmtree(cacheDir)
    os.makedirs(cacheDir, exist_ok=True)

    tcpSerSock = socket(AF_INET, SOCK_STREAM)
    tcpSerSock.bind(('', port))
    tcpSerSock.listen(1)

    while 1:
        print('Ready to serve...')
        tcpCliSock, addr = interruptible_accept(tcpSerSock)
        print('Received a connection from:', addr)
        cliSock_f = tcpCliSock.makefile('rwb', 0)
        
        try:
            requestLine, requestHeaders = parse_http_headers(cliSock_f)
            print(requestLine)
            
            if len(requestLine) == 0:
                continue
            
            method, requestUri, _ = requestLine.split()
            uri_parts = requestUri.partition('http://')
            
            if uri_parts[1] == '':
                filename = requestUri.partition('/')[2]
            else:
                filename = uri_parts[2]
            
            print(f'filename: {filename}')
            
            if len(filename) > 0:
                fileCachePath = os.path.join(cacheDir, filename.replace('/', '_'))
                cached = os.path.exists(fileCachePath) and method == "GET"
                
                if cached:
                    with open(fileCachePath, 'rb') as cache_file:
                        cliSock_f.write(cache_file.read())
                    print('Read from cache')
                else:
                    c = socket(AF_INET, SOCK_STREAM)
                    hostn = filename.partition('/')[0]
                    print(f'hostn: {hostn}')
                    
                    try:
                        c.connect((hostn.split(':')[0], int(hostn.split(':')[1]) if ':' in hostn else 80))
                        fileobj = c.makefile('rwb', 0)
                        
                        body = None
                        if method == "POST":
                            content_length = next((int(h[1]) for h in requestHeaders if h[0].lower() == 'content-length'), 0)
                            body = interruptible_read(cliSock_f, content_length)
                        
                        forward_request(fileobj, f'/{filename.partition("/")[2]}', hostn, requestLine, requestHeaders, method, body)
                        forward_and_cache_response(fileobj, fileCachePath if method == "GET" else None, cliSock_f)
                    
                    except Exception as e:
                        print(e)
                    finally:
                        c.close()
        
        except Exception as e:
            print(f"Error handling request: {e}")
        finally:
            tcpCliSock.close()

    tcpSerSock.close()
    sys.exit()

if __name__ == "__main__":
    proxyServer(8888)
