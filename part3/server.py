
"""
Part 3: FCFS Server that handles multiple clients including greedy ones
"""

import socket
import threading
import json
import time
import queue
import sys
from datetime import datetime

class FCFSServer:
    def __init__(self, config_file='config.json'):
        # Load configuration
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        self.host = self.config['server_ip']
        self.port = self.config['server_port']
        self.filename = self.config['filename']
        
        # Load words from file
        self.load_words()
        
        # Request queue for FCFS scheduling
        self.request_queue = queue.Queue()
        self.client_counter = 0
        self.client_ids = {}  # Map socket to client ID
        
        # Statistics
        self.stats_lock = threading.Lock()
        self.client_stats = {}
        
    def load_words(self):
        """Load words from the specified file"""
        try:
            with open(self.filename, 'r') as f:
                content = f.read().strip()
                self.words = content.split(',')
                print(f"Loaded {len(self.words)} words from {self.filename}")
        except FileNotFoundError:
            print(f"Error: {self.filename} not found. Creating sample file...")
            # Create a sample words.txt file
            sample_words = ['apple', 'banana', 'cat', 'dog', 'elephant'] * 100
            with open(self.filename, 'w') as f:
                f.write(','.join(sample_words))
            self.words = sample_words
    
    def handle_client(self, client_socket, client_address):
        """Handle individual client connection"""
        with self.stats_lock:
            self.client_counter += 1
            client_id = self.client_counter
            self.client_ids[client_socket] = client_id
            print(f"Client {client_id} connected from {client_address}")
        
        try:
            while True:
                # Receive request
                request = client_socket.recv(1024).decode('utf-8').strip()
                if not request:
                    break
                
                # Add request to queue with client info
                self.request_queue.put((client_socket, request, client_id, time.time()))
                
        except Exception as e:
            print(f"Error handling client {client_id}: {e}")
        finally:
            client_socket.close()
            print(f"Client {client_id} disconnected")
    
    def process_requests(self):
        """Process requests from queue in FCFS order"""
        while True:
            try:
                # Get next request from queue
                client_socket, request, client_id, enqueue_time = self.request_queue.get(timeout=1)
                
                # Process the request
                wait_time = time.time() - enqueue_time
                print(f"Processing request from Client {client_id}: {request} (waited {wait_time:.3f}s)")
                
                # Parse request
                parts = request.split(',')
                if len(parts) == 2:
                    try:
                        offset = int(parts[0])
                        count = int(parts[1])
                        
                        # Get words
                        response = self.get_words(offset, count)
                        
                        # Send response
                        client_socket.send((response + '\n').encode('utf-8'))
                        
                        # Log statistics
                        with self.stats_lock:
                            if client_id not in self.client_stats:
                                self.client_stats[client_id] = {
                                    'requests': 0,
                                    'total_wait': 0
                                }
                            self.client_stats[client_id]['requests'] += 1
                            self.client_stats[client_id]['total_wait'] += wait_time
                        
                    except ValueError:
                        client_socket.send(b"ERROR: Invalid request format\n")
                else:
                    client_socket.send(b"ERROR: Invalid request format\n")
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing request: {e}")
    
    def get_words(self, offset, count):
        """Get words from the file"""
        if offset >= len(self.words):
            return "EOF"
        
        end_index = min(offset + count, len(self.words))
        selected_words = self.words[offset:end_index]
        
        if end_index >= len(self.words):
            selected_words.append("EOF")
        
        return ','.join(selected_words)
    
    def print_statistics(self):
        """Print server statistics"""
        with self.stats_lock:
            print("\n=== Server Statistics ===")
            for client_id, stats in self.client_stats.items():
                avg_wait = stats['total_wait'] / stats['requests'] if stats['requests'] > 0 else 0
                print(f"Client {client_id}: {stats['requests']} requests, avg wait: {avg_wait:.3f}s")
    
    def start(self):
        """Start the server"""
        # Create server socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(50)
        
        print(f"FCFS Server listening on {self.host}:{self.port}")
        
        # Start request processor thread
        processor_thread = threading.Thread(target=self.process_requests, daemon=True)
        processor_thread.start()
        
        # Start statistics printer thread
        def print_stats_periodically():
            while True:
                time.sleep(10)
                self.print_statistics()
        
        stats_thread = threading.Thread(target=print_stats_periodically, daemon=True)
        stats_thread.start()
        
        try:
            while True:
                client_socket, client_address = server_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address),
                    daemon=True
                )
                client_thread.start()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            self.print_statistics()
        finally:
            server_socket.close()

if __name__ == "__main__":
    server = FCFSServer()
    server.start()