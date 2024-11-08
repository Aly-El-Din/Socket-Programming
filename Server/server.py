import socket
import sys
import threading
import os


class Server:

    def __init__(self, host="127.0.0.1", port = 8000):

        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    def handle_get(self,client_socket, path):
            print(path)
            if os.path.exists(path):
                with open(path, 'rb') as file:
                    data = file.read()
                    response = (
                                   "HTTP/1.1 200 OK\r\n"
                                   "Content-Type: text/plain\r\n"
                                   "\r\n"
                               ).encode("utf-8") + data + b"\r\n"
                    client_socket.send(response)

            else:
                client_socket.send("HTTP/1.1 404 NOT FOUND\r\n".encode("utf-8"))

    def handle_post(self, client_socket, request, path):
        # print(request)
        # Extract the headers and body from the request
        headers_end = request.find(b"\r\n\r\n")  # Find the end of headers
        body = request[headers_end + 4:]  # Get the body after headers

        # # Check for multipart form data for file upload
        # content_type = ""
        # headers = request[:headers_end]
        # for line in headers.split("\r\n"):
        #     if line.startswith("Content-Type:"):
        #         content_type = line.split(": ")[1]
        #         break
        #
        #
        # # Extract the boundary from Content-Type header
        # boundary = content_type.split("boundary=")[1]
        # boundary = "--" + boundary

        # Find the file content within the body
        # file_start = body.find(boundary) + len(boundary)
        # file_start = body.find("\r\n\r\n", file_start) + 4  # Skip headers within multipart
        # file_end = body.find(boundary, file_start) - 4  # Adjust for end boundary
        #
        # file_content = body[file_start:file_end]  # The actual file content (binary data)

        # Save the file
        # upload_dir = "./uploads"
        # os.makedirs(upload_dir, exist_ok=True)
        # file_path = os.path.join(upload_dir, os.path.basename(path))  # Save to uploads directory
        file_path = path
        # Write the file content in binary mode
        with open(file_path, 'wb') as file:
            file.write(body)  # Write binary data directly to file
            file.flush()
            os.fsync(file.fileno())
        # Send success response
        response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nFile uploaded successfully.\r\n"
        client_socket.send(response.encode("utf-8"))

    def handle_error(self,client_socket, status_code, message):
            client_socket.send(f"HTTP/1.1 {status_code} {message}\r\n".encode("utf-8"))

    def handle_client(self, client_socket, addr):
        try:
            request = b""
            while True:
                chunk = client_socket.recv(1024)
                request += chunk
                if len(chunk) < 1024:  # No more data to read
                    break

            if not request:
                client_socket.send("closed".encode("utf-8"))
                return

            # Split the request into lines to handle the headers
            request_str = request.decode("utf-8", errors="ignore")  # Decode the header part
            request_lines = request_str.split('\r\n')
            print(f"Received: {request_lines[0]}")  # The first line will have the method and path

            # Extract method and path
            method, path, _ = request_lines[0].split(' ')

            if method == 'GET':
                self.handle_get(client_socket, path)
            elif method == 'POST':
                # Handle POST and pass the raw data (request) for file processing
                self.handle_post(client_socket, request, path)
            else:
                self.handle_error(client_socket, 405, "Method Not Allowed")
        except Exception as e:
            print(f"Error when handling client: {e}")
        finally:
            client_socket.close()
            print(f"Connection to client ({addr[0]}:{addr[1]}) closed")

    def run_server(self):
            try:
                # bind the socket to the host and port
                self.server_socket.bind((self.host,self.port))
                # listen for incoming connections
                self.server_socket.listen()
                print(f"Listening on {self.host}:{self.port}")

                while True:
                    # accept a client connection
                    client_socket, addr = self.server_socket.accept()
                    print(f"Accepted connection from {addr[0]}:{addr[1]}")
                    # start a new thread to handle the client
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
        print("no port found")
    server = Server()
    server.run_server()

