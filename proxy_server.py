import socket
import os
import signal
import sys

import socket
import threading

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', 8080))
    server_socket.listen(100)
    print("Proxy server listening on port 8080")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Accepted connection from {addr}")
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

def handle_client(client_socket):
    try:
        request_data = b""
        while True:
            chunk = client_socket.recv(4096)
            if not chunk:
                break
            request_data += chunk
            if b"\r\n\r\n" in request_data:
                break

        parsed = parse_http_request(request_data)
        if not parsed or 'error' in parsed:
            send_error_response(client_socket, parsed.get('error', 400) if parsed else 400)
            return

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.connect((parsed['host'], parsed['port']))
            request = f"GET {parsed['path']} HTTP/1.0\r\n"
            headers = parsed['headers'].copy()
            headers['Host'] = f"{parsed['host']}:{parsed['port']}" if parsed['port'] != 80 else parsed['host']
            headers['Connection'] = 'close'
            request += "\r\n".join(f"{k}: {v}" for k, v in headers.items()) + "\r\n\r\n"
            server_socket.sendall(request.encode())

            while True:
                data = server_socket.recv(4096)
                if not data:
                    break
                client_socket.sendall(data)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

def parse_http_request(request_data):
    lines = request_data.split(b"\r\n")
    if not lines:
        return None

    request_line = lines[0].decode('utf-8', errors='ignore').strip()
    parts = request_line.split()
    if len(parts) != 3:
        return None

    method, url, protocol = parts
    method = method.upper()
    if method != 'GET':
        return {'error': 501}

    if not url.startswith('http://'):
        return {'error': 400}
    url = url[7:]

    path_split = url.split('/', 1)
    host_port = path_split[0]
    if len(path_split) > 1:
        path = '/' + path_split[1]
    else:
        path = '/'

    port = 80
    host_port_split = host_port.split(':', 1)
    host = host_port_split[0]
    if len(host_port_split) > 1:
        try:
            port = int(host_port_split[1])
        except ValueError:
            return {'error': 400}

    headers = {}
    for line in lines[1:]:
        line = line.strip()
        if not line:
            break
        if b':' not in line:
            continue
        key, value = line.split(b':', 1)
        key = key.decode('utf-8', errors='ignore').strip().lower()
        value = value.decode('utf-8', errors='ignore').strip()
        headers[key] = value

    return {
        'method': method,
        'host': host,
        'port': port,
        'path': path,
        'headers': headers,
        'protocol': protocol,
    }

def send_error_response(client_socket, error_code):
    if error_code == 400:
        response = b"HTTP/1.0 400 Bad Request\r\n\r\n"
    elif error_code == 501:
        response = b"HTTP/1.0 501 Not Implemented\r\n\r\n"
    elif error_code == 502:
        response = b"HTTP/1.0 502 Bad Gateway\r\n\r\n"
    else:
        response = b"HTTP/1.0 500 Internal Server Error\r\n\r\n"
    client_socket.sendall(response)
    client_socket.close()

if __name__ == '__main__':
    start_server()