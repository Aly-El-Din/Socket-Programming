import socket
import os
import sys

"""A simple client that communicates with a server using HTTP-like GET and POST requests."""


class Client:
    def __init__(self, ip, port):

        """
                Initializes the client by creating a socket attribute for server communication.
        """
        self.client_socket = None
        self.ip = ip
        self.port = port
        # Create a new socket connection at the start of the session
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to the server once before starting the requests
        self.client_socket.connect((ip, port))  # Replace with actual server IP and port

    def handle_post(self, file_path, method, server_ip, server_port):
        """
        Handles a POST request by sending the file content to the server.

        Args:
            file_path (str): The path of the file to upload.
            method (str): HTTP method to be used (POST).
            server_ip (str): IP address of the server.
            server_port (int): Port number of the server.
        
        Reads the file content, constructs the request, and sends it to the server.
        """
        with open(file_path, 'rb') as file:
            file_content = file.read()
        request = f"{method} {file_path} HTTP/1.1\r\n\r\n"
        print(f"Connecting to server POST {server_ip}:{server_port}")
        self.client_socket.send(request.encode("utf-8") + file_content)
        self.receive_response()

    def handle_get(self, file_path, method, server_ip, server_port):
        """
        Handles a GET request by requesting a file from the server and saving it locally.

        Args:
            file_path (str): The path of the file to download.
            method (str): HTTP method to be used (GET).
            server_ip (str): IP address of the server.
            server_port (int): Port number of the server.
        
        Sends the request to the server and saves the received file content.
        """
        request = f"{method} {file_path} HTTP/1.1\r\n\r\n"
        self.client_socket.send(request.encode("utf-8"))
        response = self.receive_response()
        headers_end = response.find(b"\r\n\r\n")  # Locate end of headers
        body = response[headers_end + 4:]  # Extract the body
        # Write the file content to a local file
        with open(file_path, 'wb') as file:
            file.write(body)  # Write binary data to file
            file.flush()
            os.fsync(file.fileno())

    def receive_response(self):
        """
        Receives the response from the server.

        Returns:
            bytes: The complete response from the server.
        
        Reads data in chunks and stops when no more data is available.
        """
        response = b""
        while True:
            chunk = self.client_socket.recv(1024)
            if not chunk:
                break
            response += chunk
            if len(chunk) < 1024:
                break
        response_str = response.decode("utf-8", errors="ignore")
        print(response_str)
        # header_end_index = response_str.find("\r\n\r\n")
        # if header_end_index != -1:
        #     headers = response_str[:header_end_index]
        #     print(headers)
        # else:
        #     # In case there's no \r\n\r\n, print the whole response
        #     print(f"Received: {response_str}")
        return response

    def parse_request(self, request):
        """
        Parses a single request line to extract HTTP details.

        Args:
            request (str): A line containing request information.
        
        Returns:
            dict: Parsed request details, including method, path, server IP, and port.
        """
        splitted_request = request.split(' ')
        method = splitted_request[0]
        if method == 'client_get':
            method = 'GET'
        elif method == 'client_post':
            method = 'POST'
        else:
            return None

        path = splitted_request[1]
        server_ip = splitted_request[2]
        port_number = splitted_request[3]

        return {
            "method": method,
            "path": path,
            "server_ip": server_ip,
            "port_number": port_number
        }

    def send_request(self, request_parts):
        """
        Sends an HTTP request to the server based on parsed request details.

        Args:
            request_parts (dict): Details of the request (method, path, IP, port).
        
        Determines whether the request is GET or POST and calls the appropriate handler.
        """
        try:
            method = request_parts["method"]
            file_path = request_parts["path"]
            server_ip = request_parts["server_ip"]
            server_port = int(request_parts["port_number"])
            if method == "POST":
                self.handle_post(file_path, method, server_ip, server_port)
            elif method == "GET":
                self.handle_get(file_path, method, server_ip, server_port)
        except Exception as e:
            print(f"Error sending request: {e}")

    def run(self):
        """
        Runs the client, enabling it to connect to the server and process requests from a file.
        
        Continuously prompts for an input file path and processes each line in the file as a request.
        """
        try:
            # Create a new socket connection at the start of the session
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Connect to the server once before starting the requests
            self.client_socket.connect(("127.0.0.1", 8000))  # Replace with actual server IP and port

            while True:
                # Prompt user for file path
                input_file_path = input("Enter the path of the input file ('q' to quit or 'r' to reconnect): ")
                if input_file_path.lower() == 'q':
                    print("Exiting client.")
                    break
                if input_file_path.lower() == 'r':
                    print("Reconnecting...")
                    self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.client_socket.connect((self.ip, self.port))  # Replace with actual server IP and port
                    continue
                try:
                    # Read requests from the specified file
                    with open(input_file_path, "r") as input_file:
                        msg_lines = input_file.read().splitlines()

                    # Process each request line in the file
                    for request in msg_lines:
                        request_parts = self.parse_request(request)
                        if request_parts is not None:
                            self.send_request(request_parts)

                except FileNotFoundError:
                    print(f"Error: The file '{input_file_path}' was not found. Please enter a valid file path.")
                except Exception as e:
                    print(f"Error: {e}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            # Close the socket only when the client quits
            if self.client_socket:
                self.client_socket.close()
                print("Connection to server closed")

    def test(self):
        """
        Test method for running the client with a predefined input file (input.txt).

        Mimics the run method by reading requests from input.txt and processing each.
        """
        try:
            # Create a new socket connection at the start of the session
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Connect to the server once before starting the requests
            self.client_socket.connect(("127.0.0.1", 8000))  # Replace with actual server IP and port
            input_file_path = "input.txt"
            try:
                # Read requests from the specified file
                with open(input_file_path, "r") as input_file:
                    msg_lines = input_file.read().splitlines()

                # Process each request line in the file
                for request in msg_lines:
                    request_parts = self.parse_request(request)
                    if request_parts is not None:
                        self.send_request(request_parts)

            except FileNotFoundError:
                print(f"Error: The file '{input_file_path}' was not found. Please enter a valid file path.")
            except Exception as e:
                print(f"Error: {e}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            # Close the socket only when the client quits
            if self.client_socket:
                self.client_socket.close()
                print("Connection to server closed")

# Instantiate and run the client
if __name__ == "__main__":
    try:
        ip = sys.argv[1]
    except Exception as e:
        print("No ip found, using default ip")
        ip = "127.0.0.1"
    try:
        port = int(sys.argv[2])
    except Exception as e:
        print("No port found, using default port 80")
        port = 80
    client = Client(ip, port)
    client.run()
