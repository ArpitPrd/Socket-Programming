import socket
import threading
import json
import time
import queue
import sys

class FCFSServer:
    def __init__(self, config_file='config.json'):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        self.host = '0.0.0.0'
        self.port = self.config.get('server_port', 8887)
        self.filename = self.config.get('filename', 'words.txt')
        self.load_words()
        self.request_queue = queue.Queue()

    def load_words(self):
        try:
            with open(self.filename, 'r') as f:
                self.words = f.read().strip().split(',')
                print(f"Loaded {len(self.words)} words.")
        except FileNotFoundError:
            print("words.txt not found.")
            self.words = []

    def handle_client(self, client_socket, client_address):
        print(f"Client connected from {client_address}")
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
                        self.request_queue.put((client_socket, request.strip()))
        except ConnectionResetError:
            pass 
            print(f"Client {client_address} disconnected.")
            client_socket.close()

    def process_requests(self):
        while True:
            client_socket, request = self.request_queue.get()
            try:
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
            except (ValueError, ConnectionResetError):
                pass

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(50)
        print(f"FCFS Server listening on port {self.port}")
        threading.Thread(target=self.process_requests, daemon=True).start()
        while True:
            client_socket, addr = server_socket.accept()
            threading.Thread(target=self.handle_client, args=(client_socket, addr), daemon=True).start()

if __name__ == "__main__":
    server = FCFSServer()
    server.start()