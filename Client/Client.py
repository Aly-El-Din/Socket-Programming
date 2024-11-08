import socket


class Client:
    def __init__(self):
        self.client_socket = None

    def parse_request(self, request):
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
        try:
            # Create a new socket connection for each request
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            method = request_parts["method"]
            file_path = request_parts["path"]
            with open(file_path, 'rb') as file:
                file_content = file.read()
            server_ip = request_parts["server_ip"]
            server_port = int(request_parts["port_number"])

            request = f"{method} {file_path} HTTP/1.1\r\n\r\n"
            print(f"Connecting to server {server_ip}:{server_port}")
            self.client_socket.connect((server_ip, server_port))
            self.client_socket.send(request.encode("utf-8")[:1024])
            self.client_socket.send(file_content)

            # Receive message from the server
            response = self.client_socket.recv(1024)
            response = response.decode("utf-8")
            print(f"Received: {response}")

            # If server sent "closed" in the payload, return False to end connection
            if response.lower() == "closed":
                return False
        except Exception as e:
            print(f"Error sending request: {e}")
        finally:
            # Close the socket after each request
            if self.client_socket:
                self.client_socket.close()
                print("Connection to server closed")
        return True

    def run(self):
        while True:
            # Prompt user for file path
            input_file_path = input("Enter the path of the input file (or 'q' to quit): ")
            if input_file_path.lower() == 'q':
                print("Exiting client.")
                break

            try:
                # Read requests from the specified file
                with open(input_file_path, "r") as input_file:
                    msg_lines = input_file.read().splitlines()

                # Process each request line in the file
                for request in msg_lines:
                    request_parts = self.parse_request(request)
                    if request_parts is not None:
                        if not self.send_request(request_parts):
                            return
            except FileNotFoundError:
                print(f"Error: The file '{input_file_path}' was not found. Please enter a valid file path.")
            except Exception as e:
                print(f"Error: {e}")


# Instantiate and run the client
client = Client()
client.run()
