import queue
import socket
import time
from threading import Thread
from typing import Callable

from shared.action import Action
from shared.config import SERVER_ADDRESS, SERVER_PORT
from shared.protocol import ActionProtocol

BATCH_SIZE = 50
SEND_INTERVAL = 0.05  # Send batch every 50ms


class ClientSocket:
    def __init__(self, on_action: Callable[[Action], None]):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((SERVER_ADDRESS, SERVER_PORT))

        self.batch_thread = BatchThread(self.socket)
        self.recv_thread = ReceiverThread(self.socket, on_action)

    def send_action_to_server(self, action: Action):
        self.batch_thread.add_to_queue(action)

    def close_client(self):
        self.batch_thread.stop()
        self.socket.shutdown(socket.SHUT_RDWR)


class BatchThread:
    def __init__(self, socket: socket.socket):
        self.socket = socket
        self.queue = queue.Queue()
        self.batch_thread_running = True
        # must be last
        self.t = Thread(target=self.batch_thread)
        self.t.start()

    def add_to_queue(self, action: Action):
        self.queue.put(action)

    def stop(self):
        self.batch_thread_running = False

    def batch_thread(self):
        data_batch = []
        last_send_time = time.time()

        while self.batch_thread_running:
            try:
                data_item = self.queue.get(timeout=SEND_INTERVAL)
                data_batch.append(data_item)

                if (
                    len(data_batch) >= BATCH_SIZE
                    or time.time() - last_send_time >= SEND_INTERVAL
                ):
                    ActionProtocol.send_batch(self.socket, data_batch)
                    data_batch = []
                    last_send_time = time.time()
            except queue.Empty:
                # Timeout occurred: send any remaining data
                if data_batch:
                    ActionProtocol.send_batch(self.socket, data_batch)
                    data_batch = []
                    last_send_time = time.time()
            except socket.error as e:
                print("Failed to send batch to server", e)


class ReceiverThread:
    def __init__(self, socket: socket.socket, on_action: Callable[[Action], None]):
        self.on_action = on_action
        self.socket = socket

        # must be last
        self.t = Thread(target=self.recv_thread_main)
        self.t.start()

    def recv_thread_main(self):
        print("inside client thread", self)
        while True:
            actions = ActionProtocol.recv_batch(self.socket)
            if actions:
                for action in actions:
                    self.on_action(action)
            else:
                print("ending thread")
                break
