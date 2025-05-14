import logging
import queue
import socket
import time
from threading import Thread
from typing import Callable

from shared.actions import Action
from shared.config import SERVER_ADDRESS, SERVER_PORT
from shared.protocol import ActionProtocol

BATCH_SIZE = 50
SEND_INTERVAL = 0.05  # Send batch every 50ms


class ClientSocket:
    def __init__(self, on_action: Callable[[Action], None]):
        """
        Initializes a TCP socket and starts batching and receiving threads
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((SERVER_ADDRESS, SERVER_PORT))

        self.batch_thread = BatchThread(self.socket)
        self.recv_thread = ReceiverThread(self.socket, on_action)

    def send_action_to_server(self, action: Action, immediate=False):
        """
        Sends an action immediately or queues it for batch sending
        """
        if immediate:
            ActionProtocol.send_batch(self.socket, action)
        else:
            self.batch_thread.add_to_queue(action)

    def close_client(self):
        """
        Stops the batch thread and cleanly shuts down the socket
        """
        self.batch_thread.stop()
        self.socket.shutdown(socket.SHUT_RDWR)


class BatchThread:
    def __init__(self, socket: socket.socket):
        """
        Initializes the batch thread with a socket and starts it
        """
        self.socket = socket
        self.queue = queue.Queue()
        self.batch_thread_running = True
        # must be last
        self.t = Thread(target=self.batch_thread)
        self.t.start()

    def add_to_queue(self, action: Action):
        """
        Adds an action to the sending queue
        """
        self.queue.put(action)

    def stop(self):
        """
        Stops the batch thread by setting its running flag to False
        """
        self.batch_thread_running = False

    def batch_thread(self):
        """
        Continuously batches and sends queued actions at intervals or when the batch size is reached
        """
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
            except socket.error:
                logging.exception("Failed to send batch to server")


class ReceiverThread:
    def __init__(self, socket: socket.socket, on_action: Callable[[Action], None]):
        """
        Initializes the receiver thread with a socket and callback, then starts it
        """
        self.on_action = on_action
        self.socket = socket

        # must be last
        self.t = Thread(target=self.recv_thread_main)
        self.t.start()

    def recv_thread_main(self):
        """
        Continuously receives action batches and calls the handler until the connection ends
        """
        logging.debug("client thread started")
        while True:
            actions = ActionProtocol.recv_batch(self.socket)
            if actions:
                for action in actions:
                    self.on_action(action)
            else:
                logging.debug("ending client receiver thread")
                break
