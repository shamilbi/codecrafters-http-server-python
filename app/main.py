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


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:
        conn, _ = server_socket.accept()    # wait for client
        with conn:
            for i, line in enumerate(read_lines(conn.recv)):
                if i == 0:
                    # GET URL HTTP
                    l = line.split()
                    url = l[1]
                    if url == '/':
                        conn.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
                    elif url.startswith('/echo/'):
                        body = url[6:].encode()
                        conn.send(b'HTTP/1.1 200 OK\r\n')
                        conn.send(b'Content-Type: text/plain\r\n')
                        conn.send(f'Content-Length: {len(body)}\r\n'.encode())
                        conn.send(b'\r\n')
                        conn.send(body)
                    else:
                        conn.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")
                break


if __name__ == "__main__":
    main()
