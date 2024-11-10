import mimetypes
import socket
import sys
import threading
import os
import time

class Server:
    def __init__(self, host="127.0.0.1", port=8000):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.active_connections = 0  # Decrement active connections count

    def handle_get(self, client_socket, path):
        if os.path.exists(path):
            with open(path, 'rb') as file:
                data = file.read()
                content_type, _ = mimetypes.guess_type(path)

                response = (
                    "HTTP/1.1 200 OK\r\n"
                    f"Content-Length: {len(data)}\r\n"
                    f"Content-Type: {content_type}\r\n\r\n"
                ).encode("utf-8") + data + b"\r\n"
                client_socket.send(response)
        else:
            client_socket.send("HTTP/1.1 404 NOT FOUND\r\n".encode("utf-8"))

    def handle_post(self, client_socket, request, path):
        headers_end = request.find(b"\r\n\r\n")  # Find the end of headers
        body = request[headers_end + 4:]  # Get the body after headers
        file_path = path
        # Write the file content in binary mode
        with open(file_path, 'wb') as file:
            file.write(body)  # Write binary data directly to file
            file.flush()
            os.fsync(file.fileno())
        # Send success response
        response = "HTTP/1.1 200 OK\r\n\r\n"
        client_socket.send(response.encode("utf-8"))

    def handle_error(self, client_socket, status_code, message):
        client_socket.send(f"HTTP/1.1 {status_code} {message}\r\n".encode("utf-8"))

    def handle_client(self, client_socket, addr):
        with threading.Lock():
            self.active_connections += 1
        timeout = max(5,20-self.active_connections)
        try:
            while True:
                client_socket.settimeout(timeout)
                request = b""
                while True:
                    try:
                        chunk = client_socket.recv(1024)
                        if not chunk:
                            print("Client closed the connection.")
                            client_socket.close()
                            return
                        request += chunk
                        if len(chunk) < 1024:
                            break
                    except socket.timeout:
                        print("Client idle timeout reached. Closing connection.")
                        client_socket.close()
                        return
                # Decode and parse the request
                request_str = request.decode("utf-8", errors="ignore")
                request_lines = request_str.split('\r\n')
                print(f"Received: {request_lines[0]}")
                # Extract the method, path, and headers
                method, path, _ = request_lines[0].split(' ')
                # Handle the request based on the method
                if method == 'GET':
                    self.handle_get(client_socket, path)
                elif method == 'POST':
                    self.handle_post(client_socket, request, path)
                else:
                    self.handle_error(client_socket, 405, "Method Not Allowed")

        except Exception as e:
            print(f"Error when handling client: {e}")
            # client_socket.close()
        finally:
            client_socket.close()
            with threading.Lock():
                self.active_connections -= 1  # Decrement active connections count
            print(f"Connection closed for client {addr}. Active connections: {self.active_connections}")

    def run_server(self):
        try:
            # Bind the socket to the host and port
            self.server_socket.bind((self.host, self.port))
            # Listen for incoming connections
            self.server_socket.listen()
            print(f"Listening on {self.host}:{self.port}")
            while True:
                # Accept a client connection
                client_socket, addr = self.server_socket.accept()
                print(f"Accepted connection from {addr[0]}:{addr[1]}")
                # Start a new thread to handle the client
                thread = threading.Thread(target=self.handle_client, args=(client_socket, addr))
                thread.start()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.server_socket.close()

if __name__ == '__main__':
    try:
        port = int(sys.argv[1])
    except Exception as e:
        print("No port found, using default port 80")
        port = 80
    server = Server(port=port)
    server.run_server()
