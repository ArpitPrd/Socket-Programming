
"""
Part 4: Round-Robin Server that enforces fairness among clients
"""

import socket
import threading
import json
import time
import queue
import sys
from collections import deque, defaultdict
from datetime import datetime

class RoundRobinServer:
    def __init__(self, config_file='config.json'):
        # Load configuration
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        self.host = self.config['server_ip']
        self.port = self.config['server_port']
        self.filename = self.config['filename']
        
        # Load words from file
        self.load_words()
        
        # Round-robin scheduling structures
        self.client_queues = {}  # client_id -> queue of requests
        self.client_order = deque()  # Order of clients for round-robin
        self.clients_lock = threading.Lock()
        self.client_counter = 0
        self.client_sockets = {}  # client_id -> socket
        
        # Statistics
        self.stats_lock = threading.Lock()
        self.client_stats = defaultdict(lambda: {
            'requests': 0,
            'total_wait': 0,
            'requests_processed': 0
        })
        
    def load_words(self):
        """Load words from the specified file"""
        try:
            with open(self.filename, 'r') as f:
                content = f.read().strip()
                self.words = content.split(',')
                print(f"Loaded {len(self.words)} words from {self.filename}")
        except FileNotFoundError:
            print(f"Error: {self.filename} not found. Creating sample file...")
            sample_words = ['apple', 'banana', 'cat', 'dog', 'elephant'] * 100
            with open(self.filename, 'w') as f:
                f.write(','.join(sample_words))
            self.words = sample_words
    
    def handle_client(self, client_socket, client_address):
        """Handle individual client connection"""
        with self.clients_lock:
            self.client_counter += 1
            client_id = self.client_counter
            self.client_sockets[client_id] = client_socket
            self.client_queues[client_id] = queue.Queue()
            self.client_order.append(client_id)
            print(f"Client {client_id} connected from {client_address} (Total clients: {len(self.client_order)})")
        
        try:
            while True:
                # Receive request
                request = client_socket.recv(1024).decode('utf-8').strip()
                if not request:
                    break
                
                # Add request to client's queue
                with self.clients_lock:
                    if client_id in self.client_queues:
                        self.client_queues[client_id].put((request, time.time()))
                        with self.stats_lock:
                            self.client_stats[client_id]['requests'] += 1
                        print(f"Client {client_id}: Queued request '{request}' (Queue size: {self.client_queues[client_id].qsize()})")
                
        except Exception as e:
            print(f"Error handling client {client_id}: {e}")
        finally:
            # Clean up client
            with self.clients_lock:
                if client_id in self.client_order:
                    self.client_order.remove(client_id)
                if client_id in self.client_queues:
                    del self.client_queues[client_id]
                if client_id in self.client_sockets:
                    del self.client_sockets[client_id]
            client_socket.close()
            print(f"Client {client_id} disconnected")
    
    def round_robin_scheduler(self):
        """Process requests using round-robin scheduling"""
        print("Round-robin scheduler started")
        consecutive_empty_rounds = 0
        
        while True:
            try:
                with self.clients_lock:
                    if not self.client_order:
                        time.sleep(0.1)
                        continue
                    
                    # Create a copy of current client order
                    current_clients = list(self.client_order)
                
                requests_processed = False
                
                # Process one request from each client in order
                for client_id in current_clients:
                    with self.clients_lock:
                        if client_id not in self.client_queues:
                            continue
                        
                        client_queue = self.client_queues[client_id]
                        client_socket = self.client_sockets.get(client_id)
                        
                        if not client_socket:
                            continue
                        
                        try:
                            # Try to get one request from this client
                            request, enqueue_time = client_queue.get_nowait()
                            requests_processed = True
                            
                        except queue.Empty:
                            continue
                    
                    # Process the request (outside the lock)
                    wait_time = time.time() - enqueue_time
                    print(f"RR: Processing request from Client {client_id}: {request} (waited {wait_time:.3f}s)")
                    
                    try:
                        # Parse request
                        parts = request.split(',')
                        if len(parts) == 2:
                            offset = int(parts[0])
                            count = int(parts[1])
                            
                            # Get words
                            response = self.get_words(offset, count)
                            
                            # Send response
                            client_socket.send((response + '\n').encode('utf-8'))
                            
                            # Update statistics
                            with self.stats_lock:
                                self.client_stats[client_id]['requests_processed'] += 1
                                self.client_stats[client_id]['total_wait'] += wait_time
                        else:
                            client_socket.send(b"ERROR: Invalid request format\n")
                            
                    except Exception as e:
                        print(f"Error processing request for client {client_id}: {e}")
                
                # If no requests were processed, add a small delay
                if not requests_processed:
                    consecutive_empty_rounds += 1
                    if consecutive_empty_rounds > 10:
                        time.sleep(0.01)  # Small delay to avoid busy waiting
                else:
                    consecutive_empty_rounds = 0
                    
            except Exception as e:
                print(f"Error in round-robin scheduler: {e}")
                time.sleep(0.1)
    
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
            print("\n=== Round-Robin Server Statistics ===")
            for client_id, stats in self.client_stats.items():
                if stats['requests_processed'] > 0:
                    avg_wait = stats['total_wait'] / stats['requests_processed']
                else:
                    avg_wait = 0
                print(f"Client {client_id}: {stats['requests']} requests queued, "
                      f"{stats['requests_processed']} processed, avg wait: {avg_wait:.3f}s")
    
    def start(self):
        """Start the server"""
        # Create server socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(50)
        
        print(f"Round-Robin Server listening on {self.host}:{self.port}")
        
        # Start round-robin scheduler thread
        scheduler_thread = threading.Thread(target=self.round_robin_scheduler, daemon=True)
        scheduler_thread.start()
        
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
    server = RoundRobinServer()
    server.start()