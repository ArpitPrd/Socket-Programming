import socket
import json
import time
import sys
import argparse
import os
from collections import defaultdict

class WordCountClient:
    def __init__(self, config_file='config.json', client_id=1, is_greedy=False, greedy_requests=1):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        self.server_ip = self.config.get('server_ip', '10.0.0.100')
        self.server_port = self.config.get('server_port', 8887)
        self.k = self.config.get('k', 5)
        self.client_id = client_id
        self.is_greedy = is_greedy
        self.window_size = greedy_requests 
        self.word_count = defaultdict(int)
        self.start_time = None
        self.end_time = None

    def download_file(self):
        self.start_time = time.time()
        all_words = []
        words_to_get = 200 

        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((self.server_ip, self.server_port))

            requests_sent = 0
            
           
            for i in range(self.window_size):
                request = f"{requests_sent * self.k},{self.k}\n"
                client_socket.sendall(request.encode('utf-8'))
                requests_sent += 1
            
            response_buffer = ""
            while len(all_words) < words_to_get:
                
                while '\n' not in response_buffer:
                    data = client_socket.recv(1024).decode('utf-8')
                    if not data: 
                        break
                    response_buffer += data
                
                if not response_buffer:
                    break

                response, response_buffer = response_buffer.split('\n', 1)
                print(response)
                if "EOF" in response:
                    words = [w for w in response.split(',') if w and w != 'EOF']
                    all_words.extend(words)
                    break 
                
                words = [w for w in response.split(',') if w]
                all_words.extend(words)

                if requests_sent * self.k < words_to_get:
                    request = f"{requests_sent * self.k},{self.k}\n"
                    client_socket.sendall(request.encode('utf-8'))
                    requests_sent += 1

            client_socket.close()
        except Exception as e:
            return False
        
        self.end_time = time.time()
        for word in all_words:
            self.word_count[word] += 1
        return True

    def get_completion_time(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None

    def log_results(self):
        completion_time = self.get_completion_time()
        if completion_time is not None:
            log_dir = 'logs'
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            with open(f"{log_dir}/{self.client_id}.log", "w") as f:
                f.write(str(completion_time))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Word Count Client")
    parser.add_argument('--client-id', type=str, default='client1')
    parser.add_argument('--batch-size', type=int, default=1)
    args = parser.parse_args()
    client = WordCountClient(
        client_id=args.client_id,
        is_greedy=True, 
        greedy_requests=args.batch_size 
    )
    if client.download_file():
        client.log_results()