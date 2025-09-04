
import socket
import threading
import json
import time
import queue
import sys
from collections import deque

class RoundRobinServer:
    def __init__(self, config_file='config.json'):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        self.host = '0.0.0.0' 
        self.port = self.config.get('server_port', 12345)
        self.filename = self.config.get('filename', 'words.txt')
        self.load_words()

      
        self.client_queues = {}  
        self.client_order = deque()  
        self.clients_lock = threading.Lock()
        self.client_counter = 0
        self.client_sockets = {} 

    def load_words(self):
        try:
            with open(self.filename, 'r') as f:
                self.words = f.read().strip().split(',')
                print(f"Loaded {len(self.words)} words from {self.filename}")
        except FileNotFoundError:
            self.words = ['error'] * 100
            print(f"Warning: {self.filename} not found.")

    def handle_client(self, client_socket, client_address):
        with self.clients_lock:
            self.client_counter += 1
            client_id = self.client_counter
            self.client_sockets[client_id] = client_socket
            self.client_queues[client_id] = queue.Queue()
            self.client_order.append(client_id)
            print(f"Client {client_id} connected from {client_address}")

        buffer = ""
        try:
            while True:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                buffer += data
                while '\n' in buffer:
                    request, buffer = buffer.split('\n', 1)
                    if request:
                        with self.clients_lock:
                            if client_id in self.client_queues:
                                self.client_queues[client_id].put(request.strip())
        finally:
            with self.clients_lock:
                if client_id in self.client_queues:
                    del self.client_queues[client_id]
                if client_id in self.client_sockets:
                    del self.client_sockets[client_id]
                
                temp_order = list(self.client_order)
                if client_id in temp_order:
                    temp_order.remove(client_id)
                    self.client_order = deque(temp_order)
            client_socket.close()
            print(f"Client {client_id} disconnected.")

    def round_robin_scheduler(self):
        while True:
            with self.clients_lock:
                if not self.client_order:
                    time.sleep(0.01)
                    continue
                
                client_id = self.client_order.popleft()
                self.client_order.append(client_id)
            
            try:
                
                request = self.client_queues[client_id].get_nowait()
            except (queue.Empty, KeyError):
                continue
            
            try:
                client_socket = self.client_sockets[client_id]
                offset, count = map(int, request.split(','))
                
                if offset >= len(self.words):
                    response = "EOF\n"
                else:
                    end = min(offset + count, len(self.words))
                    selected = self.words[offset:end]
                    if end >= len(self.words):
                        selected.append("EOF")
                    response = ','.join(selected) + '\n'
                client_socket.sendall(response.encode('utf-8'))
            except (ValueError, KeyError, ConnectionResetError):
                continue

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(50)
        print(f"Round-Robin Server listening on port {self.port}")
        
        scheduler_thread = threading.Thread(target=self.round_robin_scheduler, daemon=True)
        scheduler_thread.start()
        
        try:
            while True:
                client_socket, addr = server_socket.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, addr), daemon=True)
                client_thread.start()
        except KeyboardInterrupt:
            print("\nShutting down server...")
        finally:
            server_socket.close()

if __name__ == "__main__":
    server = RoundRobinServer()
    server.start()