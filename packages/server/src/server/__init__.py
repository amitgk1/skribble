import socket
import threading

from server.thread_safe_set import ThreadSafeSet
from shared.config import SERVER_PORT
from shared.protocol import ActionProtocol

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "0.0.0.0"
port = SERVER_PORT
MAX_CLIENTS = 10

server_socket.bind((host, port))
server_socket.listen(MAX_CLIENTS)

clients = ThreadSafeSet[socket.socket]()


def handle_client(client_sock: socket.socket, addr):
    try:
        while True:
            size_data_tuple = ActionProtocol.recv_batch_raw(client_sock)
            if not size_data_tuple:
                break

            size, data = size_data_tuple
            for c in clients:
                if c != client_sock:
                    c.sendall(size + data)
    except socket.error as e:
        print(f"Error handling client {addr}: {e}")
    except (ConnectionResetError, BrokenPipeError) as e:
        print("Client forcibly closed the connection:", e)
    finally:
        print(f"Connection closed from {addr}")
        close_socket(client_sock)


def close_socket(sock: socket.socket):
    clients.discard(sock)
    sock.close()


print("Server started!")
print("Waiting for clients...")

while True:
    c, addr = server_socket.accept()
    print("Got connection from", addr)
    clients.add(c)
    t = threading.Thread(target=handle_client, args=(c, addr))
    t.start()
