from socket import *
import os
import shutil
import select

# Directory for caching
cacheDir = os.path.join(os.path.dirname(__file__), 'cache')

# Helper to wait with timeout
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

def parse_http_headers(sockf):
    headline = sockf.readline().decode().strip()
    headers = []
    while True:
        header = sockf.readline().decode().strip()
        if not header:
            break
        headerParts = header.partition(":")
        if headerParts[1] == "":
            continue
        headers.append((headerParts[0].strip(), headerParts[2].strip()))
    return headline, headers

def forward_response(sockf, clientSockf, cachePath=None):
    cacheFile = None
    try:
        if cachePath:
            os.makedirs(os.path.dirname(cachePath), exist_ok=True)
            cacheFile = open(cachePath, 'wb')

        statusLine, headers = parse_http_headers(sockf)
        headers = [(k, v) for k, v in headers if k.lower() != "connection"]
        headers.append(("Connection", "close"))

        response = f"{statusLine}\r\n".encode()
        for k, v in headers:
            response += f"{k}: {v}\r\n".encode()
        response += b"\r\n"

        clientSockf.write(response)
        clientSockf.flush()
        if cacheFile:
            cacheFile.write(response)

        while True:
            chunk = sockf.read(4096)
            if not chunk:
                break
            clientSockf.write(chunk)
            clientSockf.flush()
            if cacheFile:
                cacheFile.write(chunk)

    finally:
        if cacheFile:
            cacheFile.close()

def forward_request(host, port, method, uri, headers, body=None):
    connSock = socket(AF_INET, SOCK_STREAM)
    connSock.connect((host, port))
    sockf = connSock.makefile("rwb")

    # Forward the request
    request = f"{method} {uri} HTTP/1.1\r\n".encode()
    for k, v in headers:
        request += f"{k}: {v}\r\n".encode()
    request += b"\r\n"
    if body:
        request += body
    sockf.write(request)
    sockf.flush()

    return connSock, sockf

def handle_client(clientSock, addr):
    clientSockf = clientSock.makefile("rwb")
    try:
        requestLine, headers = parse_http_headers(clientSockf)
        method, uri, _ = requestLine.split()
        print(f"Request: {method} {uri}")

        # Parse the host and path
        host = None
        if "://" in uri:
            _, _, path = uri.partition("://")
            host, _, path = path.partition("/")
        else:
            path = uri

        host, _, port = host.partition(":")
        port = int(port) if port else 80

        # Caching for GET requests
        cachePath = os.path.join(cacheDir, path.replace("/", "_")) if method == "GET" else None
        if cachePath and os.path.exists(cachePath):
            with open(cachePath, "rb") as cacheFile:
                clientSockf.write(cacheFile.read())
                clientSockf.flush()
            print(f"Cache hit for {uri}")
            return

        # Forward the request to the target server
        body = None
        if method == "POST":
            contentLength = next((int(v) for k, v in headers if k.lower() == "content-length"), 0)
            body = clientSockf.read(contentLength)

        connSock, connSockf = forward_request(host, port, method, f"/{path}", headers, body)
        forward_response(connSockf, clientSockf, cachePath)

    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        clientSock.close()

def proxyServer(port):
    if os.path.exists(cacheDir):
        shutil.rmtree(cacheDir)
    os.makedirs(cacheDir)

    serverSock = socket(AF_INET, SOCK_STREAM)
    serverSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serverSock.bind(("", port))
    serverSock.listen(5)
    print(f"Proxy server running on port {port}")

    try:
        while True:
            try:
                clientSock, addr = interruptible_accept(serverSock)
                print(f"Connection from {addr}")
                handle_client(clientSock, addr)
            except TimeoutError:
                continue
    except KeyboardInterrupt:
        print("Shutting down proxy server")
    finally:
        serverSock.close()

if __name__ == "__main__":
    proxyServer(8888)
