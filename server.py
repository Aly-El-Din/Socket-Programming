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


    def handle_post(self,client_socket,request, path):
        headers_end = request.find("\r\n\r\n")
        body = request[headers_end + 4:]  # Extract the body of the request

        # Save the file
        upload_dir = "./uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, os.path.basename(path))

        with open(file_path, 'wb') as file:
            file.write(body.encode("utf-8"))

        # Send success response
        response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nFile uploaded successfully.\r\n"
        client_socket.send(response.encode("utf-8"))


    def handle_error(self,client_socket, status_code, message):
            client_socket.send(f"HTTP/1.1 {status_code} {message}\r\n".encode("utf-8"))

    def handle_client(self,client_socket, addr):
            try:
                while True:
                    # receive and print client messages
                    request = client_socket.recv(1024).decode("utf-8")

                    if request.lower() == "close" or not request:
                        client_socket.send("closed".encode("utf-8"))
                        break
                    print(f"Received: {request}")
                    # # convert and send accept response to the client
                    # response = "accepted"
                    # client_socket.send(response.encode("utf-8"))

                    request_lines = request.split('\r\n')
                    method,path,protocol = request_lines[0].split(' ')
                    blank_line_idx = request_lines.index('')
                    headers = request_lines[1:blank_line_idx]

                    if method == 'GET':
                        self.handle_get(client_socket, path[1:])
                    elif method == 'POST':
                        self.handle_post(client_socket,request, path[1:])
                    else:
                        self.handle_error(client_socket, 405, "Method Not Allowed")


            except Exception as e:
                print(f"Error when hanlding client: {e}")
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
