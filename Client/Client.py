import socket
import sys
import re

def parse_request(request):
    splitted_request = request.split(' ')
    method = splitted_request[0]
    if method == 'client_get':
        method = 'GET'
    elif  method == 'client_post':
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

def run_client():
    # create a socket object
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # get input message from input file and send it to the server
        input_file = open("input.txt", "r")
        msg = input_file.read()
        input_file.close()
        msg_lines = msg.split('\n')
        for request in msg_lines:
            #Getting the ip address and the port number of the server
            #to establish a connection with.
            request_parts = parse_request(request)
            method = request_parts["method"]
            file_path = request_parts["path"]
            server_ip = request_parts["server_ip"]
            server_port = int(request_parts["port_number"])
            
            request = f"{method} {file_path}"
            print(f"Connecting to server {server_ip}:{server_port}")
            client.connect((server_ip, server_port))
            client.send(request.encode("utf-8")[:1024])
            
            # receive message from the server
            response = client.recv(1024)
            response = response.decode("utf-8")
            # if server sent us "closed" in the payload, we break out of
            # the loop and close our socket
            if response.lower() == "closed":
                break
            print(f"Received: {response}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # close client socket (connection to the server)
        client.close()
        print("Connection to server closed")



run_client()
