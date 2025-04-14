import socket
from threading import Thread

from skribbl.actions.action import Action
from skribbl.actions.draw_action import DrawAction
from skribbl.config import SERVER_PORT

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "0.0.0.0"
port = SERVER_PORT
MAX_CLIENTS = 10

server_socket.bind((host, port))
server_socket.listen(MAX_CLIENTS)

clients: list[socket.socket] = []


def on_new_client(client_socket: socket.socket, addr):
    print("inside thead")
    while True:
        msg = client_socket.recv(1024)
        action = Action.deserialize(msg)
        print(action)
        if isinstance(action, DrawAction):
            for c in clients:
                print("current client: ", addr, " other client: ", c.getsockname())
                if c != client_socket:
                    c.sendall(msg)
        # break

    client_socket.close()
    clients.remove(client_socket)


print("Server started!")
print("Waiting for clients...")

while True:
    c, addr = server_socket.accept()
    print("Got connection from", addr)
    clients.append(c)
    t = Thread(target=on_new_client, args=(c, addr))
    t.start()
s.close()
