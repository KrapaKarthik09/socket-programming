from socket import *
import sys
import os
import shutil
import select

# Directory for storing cached responses
cacheDir = os.path.join(os.path.dirname(__file__), 'cache')

# Helper function for interruptible operations
def wait_interruptible(waitable, timeLeft=10):
    ready = select.select([waitable], [], [], timeLeft)
    if not ready[0]:
        raise TimeoutError("Timeout waiting for connection or data")

def interruptible_accept(sock):
    wait_interruptible(sock)
    return sock.accept()

def interruptible_recv(sock, nbytes):
    wait_interruptible(sock)
    return sock.recv(nbytes)

def interruptible_readline(fileObj):
    wait_interruptible(fileObj)
    return fileObj.readline()

def interruptible_read(fileObj, nbytes=-1):
    wait_interruptible(fileObj)
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
    return headline, headers

def forward_and_cache_response(sockf, fileCachePath, clisockf):
    cachef = None
    if fileCachePath is not None:
        os.makedirs(os.path.dirname(fileCachePath), exist_ok=True)
        cachef = open(fileCachePath, 'wb')
    try:
        statusLine, headers = parse_http_headers(sockf)
        headers = [h for h in headers if h[0].lower() != 'connection']
        headers.append(('Connection', 'close'))

        response = f"{statusLine}\r\n".encode()
        for header in headers:
            response += f"{header[0]}: {header[1]}\r\n".encode()
        response += b"\r\n"

        clisockf.write(response)
        clisockf.flush()
        if cachef:
            cachef.write(response)

        while True:
            data = interruptible_read(sockf, 4096)
            if not data:
                break
            clisockf.write(data)
            clisockf.flush()
            if cachef:
                cachef.write(data)
        
    except Exception as e:
        print(f"Error in forward_and_cache_response: {e}")
    finally:
        if cachef:
            cachef.close()

def forward_request(sock, requestUri, hostn, origRequestLine, origHeaders, method, body=None):
    headers = [h for h in origHeaders if h[0].lower() != 'host']
    headers.append(('Host', hostn))

    request = f"{origRequestLine}\r\n".encode()
    for header in headers:
        request += f"{header[0]}: {header[1]}\r\n".encode()
    
    if method == "POST" and body:
        request += f"Content-Length: {len(body)}\r\n".encode()
    
    request += b"\r\n"
    
    if method == "POST" and body:
        request += body

    sock.sendall(request)

def handle_client(tcpCliSock):
    cliSock_f = tcpCliSock.makefile('rwb', 0)
    try:
        requestLine, requestHeaders = parse_http_headers(cliSock_f)
        print(f"Request Line: {requestLine}")
        
        if not requestLine:
            return

        method, requestUri, _ = requestLine.split()
        uri_parts = requestUri.partition('http://')

        if uri_parts[1] == '':
            filename = requestUri.partition('/')[2]
        else:
            filename = uri_parts[2]

        print(f"Filename: {filename}")

        if filename:
            fileCachePath = os.path.join(cacheDir, filename.replace('/', '_'))
            cached = os.path.exists(fileCachePath) and method == "GET"

            if cached:
                with open(fileCachePath, 'rb') as cache_file:
                    cliSock_f.write(cache_file.read())
                print("Read from cache")
            else:
                c = socket(AF_INET, SOCK_STREAM)
                c.settimeout(10)
                hostn = filename.partition('/')[0]

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
                    print(f"Error handling request: {e}")
                finally:
                    c.close()
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        tcpCliSock.close()

def proxyServer(port):
    if os.path.isdir(cacheDir):
        shutil.rmtree(cacheDir)
    os.makedirs(cacheDir, exist_ok=True)

    try:
        tcpSerSock = socket(AF_INET, SOCK_STREAM)
        tcpSerSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        tcpSerSock.bind(('', port))
        tcpSerSock.listen(5)
        print(f"Proxy server is running on port {port}")
    except Exception as e:
        print(f"Error initializing proxy server: {e}")
        sys.exit(1)

    try:
        while True:
            try:
                tcpCliSock, addr = interruptible_accept(tcpSerSock)
                print(f"Connection from {addr}")
                handle_client(tcpCliSock)
            except TimeoutError:
                continue
            except Exception as e:
                print(f"Error accepting connection: {e}")
    except KeyboardInterrupt:
        print("Proxy server is shutting down")
    finally:
        tcpSerSock.close()

if __name__ == "__main__":
    proxyServer(8888)
