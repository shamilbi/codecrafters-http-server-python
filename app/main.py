import socket

RN = b'\r\n'


def parse_request(conn):
    d = {}
    headers = {}
    body = []

    target = 0  # request
    rest = b''
    ind = 0
    body_len = 0
    body_count = 0
    while data := conn.recv(1024):
        if rest:
            data = rest + data
            rest = b''

        if target == 0:
            ind = data.find(RN)
            if ind == -1:
                rest = data
                continue
            # GET URL HTTP
            line = data[:ind].decode()
            data = data[ind + 2:]
            d['request'] = line
            l = line.split()
            d['url'] = l[1]
            target = 1  # headers

        if target == 1:
            if not data:
                continue
            while True:
                ind = data.find(RN)
                if ind == -1:
                    rest = data
                    break
                if ind == 0:    # \r\n\r\n
                    data = data[ind + 2:]
                    target = 2
                    break
                line = data[:ind].decode()
                data = data[ind + 2:]
                l = line.split(':', maxsplit=1)
                field = l[0]
                value = l[1].strip()
                headers[field.lower()] = value
            if target == 1:
                continue

        if target == 2:
            if 'content-length' not in headers:
                break
            body_len =int(headers['content-length'])
            if not body_len:
                break
            target = 3

        if target == 3:
            body.append(data)
            body_count += len(data)
            if body_count >= body_len:
                break

    d['headers'] = headers
    d['body'] = b''.join(body).decode()
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
                conn.send(RN)
                conn.send(body)
            elif url == '/user-agent':
                body = d['headers']['user-agent'].encode()
                conn.send(b'HTTP/1.1 200 OK\r\n')
                conn.send(b'Content-Type: text/plain\r\n')
                conn.send(f'Content-Length: {len(body)}\r\n'.encode())
                conn.send(RN)
                conn.send(body)
            else:
                conn.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")


if __name__ == "__main__":
    main()
