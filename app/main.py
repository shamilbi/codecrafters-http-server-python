import socket


def read_lines(f_recv):
    'f_recv: read bytes (conn.recv, ...)'
    rest = b''
    while True:
        data = f_recv(1024)
        if not data:
            break
        l = data.split(b'\r\n')
        if rest:
            l = [rest + l[0]] + l[1:]
            rest = b''
        if not data.endswith(b'\r\n'):
            rest = l[-1]
            l = l[:-1]
        for i in l:
            yield i.decode()
    if rest:
        yield rest.decode()


def parse_request(conn):
    d = {}
    headers = []
    headersD = {}
    body = []
    target = 0  # request
    for line in read_lines(conn.recv):
        if target == 0:
            # GET URL HTTP
            d['request'] = line
            l = line.split()
            d['url'] = l[1]
            target = 1  # fields
        elif target == 1:
            if line:
                l = line.split(':', maxsplit=1)
                field = l[0]
                value = l[1].strip()
                headers.append((field, value))
                headersD[field.lower()] = value
                #print(f'field {field}: {value}')
            else:
                target = 2
        elif target == 2:
            if not line:
                break
            body.append(line)
    d['headers'] = headers
    d['headersD'] = headersD
    d['body'] = body
    return d


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:
        conn, _ = server_socket.accept()    # wait for client
        with conn:
            d = parse_request(conn)
            url = d['url']
            if url == '/':
                conn.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
            elif url.startswith('/echo/'):
                body = url[6:].encode()
                conn.send(b'HTTP/1.1 200 OK\r\n')
                conn.send(b'Content-Type: text/plain\r\n')
                conn.send(f'Content-Length: {len(body)}\r\n'.encode())
                conn.send(b'\r\n')
                conn.send(body)
            elif url == '/user-agent':
                body = d['headersD']['user-agent'].encode()
                conn.send(b'HTTP/1.1 200 OK\r\n')
                conn.send(b'Content-Type: text/plain\r\n')
                conn.send(f'Content-Length: {len(body)}\r\n'.encode())
                conn.send(b'\r\n')
                conn.send(body)
            else:
                conn.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")


if __name__ == "__main__":
    main()
