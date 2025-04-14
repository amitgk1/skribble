from threading import Thread
import socket
from typing import Callable

from skribbl.actions.action import Action
from skribbl.config import SERVER_ADDRESS, SERVER_PORT


class ClientSocket:
    def __init__(self, on_action: Callable[[Action], None]):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((SERVER_ADDRESS, SERVER_PORT))
        self.on_action = on_action
        self.thread = Thread(target=self.thread_main)
        self.thread.start()

    def send_action_to_server(self, action: Action):
        self.socket.sendall(action.serialize())

    def close_client(self):
        self.socket.shutdown(socket.SHUT_RDWR)

    def thread_main(self):
        print("inside client thread", self)
        while True:
            msg = self.socket.recv(1024)
            if msg:
                action = Action.deserialize(msg)
                print(action)
                self.on_action(action)
            else:
                print("ending thread")
                break
