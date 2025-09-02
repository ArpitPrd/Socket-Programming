import socket
import argparse
import json
import time

def main(config):
    host = config["server_ip"]
    k = config["k"]
    p = 0
    port = config["server_port"]

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        print("Connected to server.")

        download_time = 0
        while True:
            message = f"{p},{k}\n"
            send_time = time.time()
            s.send(message.encode())
            data = s.recv(1024)
            recv_time = time.time()
            download_time += recv_time - send_time
            print("Server replied:", data.decode())

            if "EOF\n" in data.split(",") or "EOF" in data.split(","):
                break
        
        print(f"ELAPSED_MS:{download_time*1000}")

def read_json(filename) -> dict:
    with open(filename) as f:
        data = json.load(f)
    
    return data

if __name__ == "__main__":
    
    filename = "config.json"
    config = read_json(filename)

    main(config)