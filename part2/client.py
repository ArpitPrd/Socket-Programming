import socket
import argparse
import json

def main(config):
    host = config["server_ip"]
    k = config["k"]
    p = 0
    port = config["server_port"]

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        print("Connected to server.")

        while True:
            message = f"{p},{k}\n"
            s.send(message.encode())
            data = s.recv(1024)
            print("Server replied:", data.decode())

            if "EOF" in data.split(","):
                break
        
        message = "STOP"
        s.send(message.encode())

def read_json(filename) -> dict:
    with open(filename) as f:
        data = json.load(f)
    
    return data

if __name__ == "__main__":
    
    filename = "config.json"
    config = read_json(filename)

    main(config)