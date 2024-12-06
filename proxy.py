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
    try:
        if fileCachePath is not None:
            os.makedirs(os.path.dirname(fileCachePath), exist_ok=True)
            cachef = open(fileCachePath, 'w+b')

        # Parse the response headers
        statusLine, headers = parse_http_headers(sockf)
        headers = [h for h in headers if h[0].lower() != 'connection']
        headers.append(('Connection', 'close'))

        # Forward response headers
        clisockf.write(f"{statusLine}\r\n".encode())
        for header in headers:
            clisockf.write(f"{header[0]}: {header[1]}\r\n".encode())
        clisockf.write(b"\r\n")

        # Forward response body
        while True:
            data = sockf.read(4096)
            if not data:
                break
            clisockf.write(data)
            if cachef:
                cachef.write(data)
    except Exception as e:
        print(f"Error while forwarding response: {e}")
    finally:
        if cachef:
            cachef.close()

def forward_request(sockf, requestUri, hostn, origRequestLine, origHeaders, cliSock_f):
    try:
        headers = [h for h in origHeaders if h[0].lower() != 'host']
        headers.append(('Host', hostn))

        # Forward the request
        sockf.write(f"{origRequestLine}\r\n".encode())
        for header in headers:
            sockf.write(f"{header[0]}: {header[1]}\r\n".encode())
        sockf.write(b"\r\n")

        # Forward POST body if applicable
        if origRequestLine.startswith("POST"):
            content_length = int(dict(origHeaders).get('Content-Length', 0))
            body = cliSock_f.read(content_length)
            sockf.write(body)
    except Exception as e:
        print(f"Error while forwarding request: {e}")

def proxyServer(port):
    if os.path.isdir(cacheDir):
        shutil.rmtree(cacheDir)

    tcpSerSock = socket(AF_INET, SOCK_STREAM)
    tcpSerSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    tcpSerSock.bind(('', port))
    tcpSerSock.listen(5)

    try:
        while True:
            print("Proxy ready to serve...")
            tcpCliSock, addr = interruptible_accept(tcpSerSock)
            print(f"Received connection from {addr}")
            cliSock_f = tcpCliSock.makefile('rwb', 0)

            try:
                # Parse client request
                requestLine, requestHeaders = parse_http_headers(cliSock_f)
                if not requestLine:
                    tcpCliSock.close()
                    continue

                method, requestUri, _ = requestLine.split()
                uri_parts = requestUri.partition('http://')
                if uri_parts[1] == '':
                    filename = requestUri.partition('/')[2]
                else:
                    filename = uri_parts[2]

                # Determine caching logic
                if method == "GET":
                    fileCachePath = os.path.join(cacheDir, filename.replace('/', '_'))
                    cached = os.path.exists(fileCachePath)
                else:
                    fileCachePath = None
                    cached = False

                # Serve from cache if available
                if cached and fileCachePath:
                    with open(fileCachePath, 'rb') as cache_file:
                        cliSock_f.write(cache_file.read())
                    print(f"Served from cache: {fileCachePath}")
                else:
                    # Forward request to server
                    hostn = filename.partition('/')[0]
                    c = socket(AF_INET, SOCK_STREAM)
                    c.connect((hostn, 80))
                    fileobj = c.makefile('rwb', 0)
                    forward_request(fileobj, f'/{filename.partition("/")[2]}', hostn, requestLine, requestHeaders, cliSock_f)

                    # Cache and forward response
                    forward_and_cache_response(fileobj, fileCachePath, cliSock_f)
                    c.close()
            except Exception as e:
                print(f"Error handling client request: {e}")
            finally:
                cliSock_f.close()
                tcpCliSock.close()
    except KeyboardInterrupt:
        print("\nShutting down proxy server.")
    finally:
        tcpSerSock.close()

if __name__ == "__main__":
    proxyServer(8888)
