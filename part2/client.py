import socket
import argparse
import json
import time

def main(config):
    host = config["server_ip"]
    k = config["k"]
    p = config["p"]
    port = config["server_port"]
    print(f"host={host}, port={port}, k={k}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        
        s.connect((host, port))
        print("[client] Connected to server.")

        download_time = 0
        while True:
            message = f"{p},{k}\n"
            send_time = time.time()
            s.send(message.encode())
            data = s.recv(1024)
            recv_time = time.time()
            download_time += recv_time - send_time
            print("[client] Server replied:", data.decode())
            decoded_data = data.decode()

            if "EOF\n" in decoded_data.split(",") or "EOF" in decoded_data.split(","):
                print(f"[client] Received EOF, exiting")
                break
            p += k
        
        print(f"ELAPSED_MS:{download_time*1000}")

def read_json(filename) -> dict:
    with open(filename) as f:
        data = json.load(f)
    
    return data

if __name__ == "__main__":
    
    filename = "config.json"
    config = read_json(filename)

    main(config)