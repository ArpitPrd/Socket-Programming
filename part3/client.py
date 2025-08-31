
"""
Part 3: Client implementation with support for greedy behavior
"""

import socket
import json
import time
import sys
import threading
from collections import defaultdict

class WordCountClient:
    def __init__(self, config_file='config.json', client_id=1, is_greedy=False, greedy_requests=1):
        # Load configuration
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        self.server_ip = self.config['server_ip']
        self.server_port = self.config['server_port']
        self.k = self.config.get('k', 5)  # Words per request
        self.client_id = client_id
        self.is_greedy = is_greedy
        self.greedy_requests = greedy_requests
        
        # Statistics
        self.word_count = defaultdict(int)
        self.start_time = None
        self.end_time = None
        self.total_words = 0
        self.requests_sent = 0
        
    def download_file(self):
        """Download the entire file from server"""
        self.start_time = time.time()
        offset = 0
        all_words = []
        
        try:
            # Create socket connection
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((self.server_ip, self.server_port))
            
            if self.is_greedy:
                # Greedy client: Send multiple requests without waiting
                print(f"Client {self.client_id} (GREEDY): Sending {self.greedy_requests} requests back-to-back")
                
                # Send all requests first
                for i in range(self.greedy_requests):
                    request = f"{offset + i * self.k},{self.k}"
                    client_socket.send((request + '\n').encode('utf-8'))
                    self.requests_sent += 1
                    print(f"Client {self.client_id}: Sent request {i+1}/{self.greedy_requests}: {request}")
                
                # Then receive all responses
                for i in range(self.greedy_requests):
                    response = client_socket.recv(4096).decode('utf-8').strip()
                    words = response.split(',')
                    
                    # Check for EOF
                    if 'EOF' in words:
                        words = [w for w in words if w != 'EOF']
                        all_words.extend(words)
                        break
                    else:
                        all_words.extend(words)
                
                # Continue with normal downloading for remaining file
                offset = self.greedy_requests * self.k
                
            # Normal downloading (or continue after greedy requests)
            while True:
                request = f"{offset},{self.k}"
                client_socket.send((request + '\n').encode('utf-8'))
                self.requests_sent += 1
                
                response = client_socket.recv(4096).decode('utf-8').strip()
                
                if response == "EOF":
                    break
                
                words = response.split(',')
                
                # Check for EOF in the word list
                if 'EOF' in words:
                    words = [w for w in words if w != 'EOF']
                    all_words.extend(words)
                    break
                else:
                    all_words.extend(words)
                    offset += self.k
            
            client_socket.close()
            
        except Exception as e:
            print(f"Client {self.client_id}: Error during download: {e}")
            return False
        
        self.end_time = time.time()
        
        # Count word frequencies
        for word in all_words:
            if word:  # Skip empty strings
                self.word_count[word] += 1
                self.total_words += 1
        
        return True
    
    def get_completion_time(self):
        """Get the total completion time"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None
    
    def print_results(self):
        """Print word frequencies and statistics"""
        completion_time = self.get_completion_time()
        
        client_type = "GREEDY" if self.is_greedy else "NORMAL"
        print(f"\n=== Client {self.client_id} ({client_type}) Results ===")
        print(f"Total words downloaded: {self.total_words}")
        print(f"Unique words: {len(self.word_count)}")
        print(f"Requests sent: {self.requests_sent}")
        print(f"Completion time: {completion_time:.3f} seconds")
        
        if len(self.word_count) <= 10:  # Only print if small number of unique words
            print("\nWord frequencies:")
            for word, count in sorted(self.word_count.items()):
                print(f"{word}, {count}")
        
        return completion_time

def run_concurrent_clients(config_file='config.json'):
    """Run multiple clients concurrently with one greedy client"""
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    num_clients = config.get('num_clients', 10)
    c = config.get('c', 1)  # Number of greedy requests
    
    clients = []
    threads = []
    
    # Create clients (first one is greedy)
    for i in range(num_clients):
        is_greedy = (i == 0)  # First client is greedy
        client = WordCountClient(
            config_file=config_file,
            client_id=i+1,
            is_greedy=is_greedy,
            greedy_requests=c if is_greedy else 1
        )
        clients.append(client)
    
    # Start all clients concurrently
    print(f"Starting {num_clients} clients (Client 1 is greedy with c={c})")
    for client in clients:
        thread = threading.Thread(target=client.download_file)
        thread.start()
        threads.append(thread)
        time.sleep(0.1)  # Small delay to avoid overwhelming the server initially
    
    # Wait for all clients to complete
    for thread in threads:
        thread.join()
    
    # Collect and display results
    completion_times = []
    for client in clients:
        completion_time = client.print_results()
        if completion_time:
            completion_times.append(completion_time)
    
    # Calculate and display Jain's Fairness Index
    if completion_times:
        jfi = calculate_jains_fairness_index(completion_times)
        print(f"\n=== Fairness Metrics ===")
        print(f"Jain's Fairness Index: {jfi:.4f}")
        print(f"Average completion time: {sum(completion_times)/len(completion_times):.3f} seconds")
        print(f"Min completion time: {min(completion_times):.3f} seconds")
        print(f"Max completion time: {max(completion_times):.3f} seconds")
        
        return completion_times, jfi
    
    return [], 0

def calculate_jains_fairness_index(values):
    """Calculate Jain's Fairness Index"""
    if not values or len(values) == 0:
        return 0
    
    n = len(values)
    sum_values = sum(values)
    sum_squares = sum(v**2 for v in values)
    
    if sum_squares == 0:
        return 0
    
    jfi = (sum_values ** 2) / (n * sum_squares)
    return jfi

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "concurrent":
        run_concurrent_clients()
    else:
        # Run single client
        client = WordCountClient()
        if client.download_file():
            client.print_results()