import select
import socket
import json

def clear_connection(sock, sockets_list, clients):
    sockets_list.remove(sock)
    if sock in clients:
        del clients[sock]
    sock.close()
    return

def handle_request(message: str, words: list[str]) -> str:
    try:
        parts = message.strip().split(",")
        p = int(parts[0])
        k = int(parts[1])
    except (ValueError, IndexError):
        return "ERROR: Invalid request\n"

    # print(f"{p},{k}")
    if p >= len(words):
        return "EOF\n"
    elif p + k > len(words):
        return ",".join(words[p:]) + ",EOF\n"
    else:
        return ",".join(words[p:p+k]) + "\n"


def main(config):
    host = config["server_ip"]
    port = config["server_port"]
    words_file = config["filename"]
    print(f"[server] Starting server on {host}:{port}, words_file={words_file}", flush=True)
    with open(words_file) as f:
        words = f.read().split(",")
        words = [w.split("\n")[0] for w in words]

    # Create listening socket same as C
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen()

    # list sockets to work on
    sockets_list = [server_socket]

    clients = {}

    while True:
        read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
        # iterate over notified sockets
        for read_socket in read_sockets:
            
            if read_socket is server_socket:
                # New connection
                client_socket, client_address = server_socket.accept()
                sockets_list.append(client_socket)
                clients[client_socket] = client_address
                print(f"[server] Accepted connection from {client_address}")
            else:
                # Existing client sent data
                try:
                    recv_data = read_socket.recv(1024)
                    if recv_data:
                        message = recv_data.decode()
                        
                        send_message = handle_request(message, words)
                        read_socket.sendall(send_message.encode())
                    else:
                        # Client disconnected
                        print(f"[server] Closed connection from {clients[read_socket]}")
                        clear_connection(read_socket, sockets_list, clients)
                
                except ConnectionResetError:
                    print(f"[server] Connection reset by {clients[read_socket]}")
                    clear_connection(read_socket, sockets_list, clients)

        # Handle exceptions
        for read_socket in exception_sockets:
            clear_connection(read_socket, sockets_list, clients)


def read_json(filename) -> dict:
    with open(filename) as f:
        data = json.load(f)
    
    return data

if __name__ == "__main__":
    config = read_json("config.json")
    
    main(config)
