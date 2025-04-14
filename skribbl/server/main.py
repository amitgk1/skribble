import socket
from threading import Thread

from skribbl.actions.protocol import ActionProtocol
from skribbl.config import SERVER_PORT

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "0.0.0.0"
port = SERVER_PORT
MAX_CLIENTS = 10

server_socket.bind((host, port))
server_socket.listen(MAX_CLIENTS)

clients: list[socket.socket] = []


def handle_client(client_sock: socket.socket, addr):
    try:
        while True:
            size, data = ActionProtocol.recv_batch_raw(client_sock)
            for c in clients:
                if c != client_sock:
                    c.sendall(size + data)
            
                
    except socket.error as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        client_sock.close()
        print(f"Connection closed from {addr}")


print("Server started!")
print("Waiting for clients...")

while True:
    c, addr = server_socket.accept()
    print("Got connection from", addr)
    clients.append(c)
    t = Thread(target=handle_client, args=(c, addr))
    t.start()
s.close()
