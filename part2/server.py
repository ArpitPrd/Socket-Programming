import select
import socket
import json

# Create the default selector
sel = selectors.DefaultSelector()

def accept_connection(sock):
    conn, addr = sock.accept()  # Accept the connection
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)     # Non-blocking mode
    sel.register(conn, selectors.EVENT_READ, handle_client)

def handle_client(conn):
    try:
        data = conn.recv(1024)
        if data:
            message = data.decode()
            print(f"Received: {message} from {conn.getpeername()}")
            conn.sendall(f"Echo: {message}".encode())
        else:
            # No data means client closed connection
            print(f"Closing connection to {conn.getpeername()}")
            sel.unregister(conn)
            conn.close()
    except ConnectionResetError:
        print("Client disconnected abruptly")
        sel.unregister(conn)
        conn.close()

def clear_connection(sock, sockets_list, clients):
    sockets_list.remove(sock)
    del clients[sock]
    sock.close()
    return

def handle_request(message:str, words:list[str]):

    p = eval(message.split(",")[0])
    k = eval(message.split(",")[-1][:-1])
    end_token = ""
    if p > len(words):
        end_token = "EOF\n"
    if p+k>=len(words):
        end_token = ",EOF\n"
    
    ret_message = ",".join(words[p:p+k]) + end_token
    return ret_message

def main(config):
    host = config["server_ip"]
    port = config["server_port"]
    words_file = config["filename"]
    with open(words_file) as f:
        words = f.readline()

    # Create listening socket
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((host, port))
    server_sock.listen()
    print(f"Server listening on {host}:{port}")

    sockets_list = [server_sock]

    clients = {}

    while True:
        read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
        for read_socket in read_sockets:
            
            if read_socket is server_sock:
                # New connection
                client_socket, client_address = server_sock.accept()
                sockets_list.append(client_socket)
                clients[client_socket] = client_address
                print(f"Accepted connection from {client_address}")
            else:
                # Existing client sent data
                try:
                    recv_data = read_socket.recv(1024)
                    if recv_data:
                        message = recv_data.decode()
                        if message=="STOP":
                            clear_connection(read_socket, sockets_list, clients)
                        
                        send_message = handle_request(message, words)
                        read_socket.sendall(send_message.encode())
                    else:
                        # Client disconnected
                        print(f"Closed connection from {clients[read_socket]}")
                        clear_connection(read_socket, sockets_list, clients)
                
                except ConnectionResetError:
                    print(f"Connection reset by {clients[read_socket]}")
                    clear_connection(read_socket)

        # Handle exceptions
        for read_socket in exception_sockets:
            sockets_list.remove(read_socket)
            if read_socket in clients:
                del clients[read_socket]
            read_socket.close()


def read_json(filename) -> dict:
    with open(filename) as f:
        data = json.load(f)
    
    return data

if __name__ == "__main__":
    config = read_json("config.json")
    
    main()
