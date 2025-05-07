import logging
import socket

from shared.config import SERVER_PORT

from server.room import Room

global_room = Room()


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = "0.0.0.0"
    port = SERVER_PORT
    MAX_CLIENTS = 10

    server_socket.bind((host, port))
    server_socket.listen(MAX_CLIENTS)

    logging.info("Server started!")
    logging.info("Waiting for clients...")
    while True:
        c, addr = server_socket.accept()
        global_room.add_client(c, addr)
