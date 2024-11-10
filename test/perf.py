import threading
import time
import socket
import statistics
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt

class LoadTester:
    def __init__(self, host='127.0.0.1', port=8000):
        self.host = host
        self.port = port
        self.results = []
        
    # Connecting clients to only one socket
    def create_persistent_connection(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.port))
            return sock
        except Exception as e:
            print(f"Error creating connection: {e}")
            return None
        
    def make_request(self, sock, request_type='GET'):
        try:
            if request_type == 'GET':
                request = "GET test.txt HTTP/1.1\r\nConnection: keep-alive\r\n\r\n"
            else:  
                content = "Test content"
                request = (
                    f"POST test.txt HTTP/1.1\r\n"
                    f"Connection: keep-alive\r\n"
                    f"Content-Length: {len(content)}\r\n\r\n"
                    f"{content}"
                )
            
            start_time = time.time()
            
            # Send request
            sock.send(request.encode())
            
            # Read response headers first
            response = b""
            while b"\r\n\r\n" not in response:
                chunk = sock.recv(1024)
                if not chunk:
                    raise Exception("Connection closed while reading headers")
                response += chunk
            
            # Find Content-Length if present
            headers = response.split(b"\r\n\r\n")[0].decode('utf-8')
            content_length = None
            for line in headers.split('\r\n'):
                if line.lower().startswith('content-length:'):
                    content_length = int(line.split(':')[1].strip())
                    break
            
            # Read remaining body if Content-Length is known
            if content_length:
                body = response.split(b"\r\n\r\n", 1)[1]
                remaining = content_length - len(body)
                while remaining > 0:
                    chunk = sock.recv(min(remaining, 1024))
                    if not chunk:
                        raise Exception("Connection closed while reading body")
                    response += chunk
                    remaining -= len(chunk)
            
            end_time = time.time()
            
            return {
                'success': True,
                'response_time': end_time - start_time
            }
            
        except Exception as e:
            return {
                'success': False,
                'response_time': None,
                'error': str(e)
            }

    def run_load_test(self, num_clients, requests_per_client):
        """Run load test with persistent connections per client"""
        client_results = []
        
        def client_session():
            session_results = []
            sock = self.create_persistent_connection()
            if sock:
                try:
                    for _ in range(requests_per_client):
                        result = self.make_request(sock)
                        if result['success']:
                            session_results.append(result['response_time'])
                finally:
                    sock.close()
            return session_results
        
        with ThreadPoolExecutor(max_workers=num_clients) as executor:
            futures = [executor.submit(client_session) for _ in range(num_clients)]
            for future in futures:
                try:
                    results = future.result()
                    client_results.extend(results)
                except Exception as e:
                    print(f"Error in client session: {e}")
        
        return client_results

def main():
    # Test parameters
    client_counts = [1, 50, 100, 200, 300, 400, 500]
    requests_per_client = 100
    
    # Results storage
    avg_response_times = []
    throughputs = []
    success_rates = []
    
    tester = LoadTester()
    
    print("Starting load test with persistent connections...")
    print("Clients | Avg Response Time (s) | Throughput (req/s) | Success Rate (%)")
    print("-" * 70)
    
    for num_clients in client_counts:
        start_time = time.time()
        results = tester.run_load_test(num_clients, requests_per_client)
        total_time = time.time() - start_time
        
        # Calculate metrics
        if results:
            avg_response_time = statistics.mean(results)
            throughput = (num_clients * requests_per_client) / total_time
            success_rate = (len(results) / (num_clients * requests_per_client)) * 100
            
            avg_response_times.append(avg_response_time)
            throughputs.append(throughput)
            success_rates.append(success_rate)
            
            print(f"{num_clients:7d} | {avg_response_time:18.3f} | {throughput:18.2f} | {success_rate:14.2f}")
    
    # Create visualization
    plt.figure(figsize=(15, 5))
    
    # Response Time Plot
    plt.subplot(1, 3, 1)
    plt.plot(client_counts, avg_response_times, marker='o')
    plt.title('Average Response Time vs Clients')
    plt.xlabel('Number of Concurrent Clients')
    plt.ylabel('Average Response Time (seconds)')
    plt.grid(True)
    
    # Throughput Plot
    plt.subplot(1, 3, 2)
    plt.plot(client_counts, throughputs, marker='o', color='green')
    plt.title('Throughput vs Clients')
    plt.xlabel('Number of Concurrent Clients')
    plt.ylabel('Throughput (requests/second)')
    plt.grid(True)
    
    # Success Rate Plot
    plt.subplot(1, 3, 3)
    plt.plot(client_counts, success_rates, marker='o', color='red')
    plt.title('Success Rate vs Clients')
    plt.xlabel('Number of Concurrent Clients')
    plt.ylabel('Success Rate (%)')
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('server_performance.png')
    print("\nPerformance plots saved as 'server_performance.png'")

if __name__ == '__main__':
    main()