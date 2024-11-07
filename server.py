import socket
import threading

def handle_get(client_socket, path):
    """
    TODO: 
    Transmit contents of file (reads from the file and writes on the socket) (in case of GET) 
    If document is not available, return 404 Not Found
    ==>client_socket.send("HTTP/1.1 404 NOT FOUND\r\n".encode("utf-8"))
    """
    pass

def handle_post(client_socket, path):
    client_socket.send("HTTP/1.1 200 OK\r\n".encode("utf-8"))

def handle_error(client_socket, status_code, message):
    pass

def handle_client(client_socket, addr):
    try:
        while True:
            # receive and print client messages
            request = client_socket.recv(1024).decode("utf-8")

            if request.lower() == "close":
                client_socket.send("closed".encode("utf-8"))
                break
            print(f"Received: {request}")
            # convert and send accept response to the client
            response = "accepted"
            client_socket.send(response.encode("utf-8"))

            request_lines = request.split('\r\n')
            method,path,protocol = request_lines[0].split(' ')

            if method == 'GET':
                handle_get(client_socket, path)
            elif method == 'POST':
                handle_post(client_socket, path)
            else:
                handle_error(client_socket, 405, "Method Not Allowed")

            
    except Exception as e:
        print(f"Error when hanlding client: {e}")
    finally:
        client_socket.close()
        print(f"Connection to client ({addr[0]}:{addr[1]}) closed")

def run_server():
    server_ip = "127.0.0.1"  # server hostname or IP address
    port = 8000  # server port number
    # create a socket object
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind the socket to the host and port
        server.bind((server_ip, port))
        # listen for incoming connections
        server.listen()
        print(f"Listening on {server_ip}:{port}")

        while True:
            # accept a client connection
            client_socket, addr = server.accept()
            print(f"Accepted connection from {addr[0]}:{addr[1]}")
            # start a new thread to handle the client
            thread = threading.Thread(target=handle_client, args=(client_socket, addr,))
            thread.start()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        server.close()


