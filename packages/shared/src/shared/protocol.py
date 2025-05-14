import logging
import pickle
import socket

from shared.actions import Action

HEADER_SIZE = 4


class ActionProtocol:
    @staticmethod
    def send_batch(sock: socket.socket, batch: list[Action] | Action):
        """
        sends the batch form server to client and the opposite
        """
        if not batch:
            return

        serialized = pickle.dumps(batch)

        # First send the length of the pickled data as a fixed-length integer
        message_length = len(serialized)
        size = message_length.to_bytes(HEADER_SIZE, byteorder="big")

        sock.sendall(size + serialized)

    @staticmethod
    def recv_batch_raw(sock: socket.socket):
        """
        receive the batch from the client to the server and the opposite
        """
        # First read the message length header
        header = sock.recv(HEADER_SIZE)
        if not header or len(header) < HEADER_SIZE:
            return None

        # Unpack the message length
        message_length = int.from_bytes(header, byteorder="big")

        # Read the actual message data
        data = b""
        while len(data) < message_length:
            chunk = sock.recv(min(4096, message_length - len(data)))
            if not chunk:
                raise RuntimeError("Socket connection broken")
            data += chunk

        return (header, data)

    @staticmethod
    def recv_batch(sock: socket.socket) -> list[Action]:
        """
        This function receives raw data from a socket, attempts to unpickle it into a list of Action objects, and returns the list if successful.
        """
        size_plus_data = ActionProtocol.recv_batch_raw(sock)

        try:
            if size_plus_data:
                size, data = size_plus_data

                if data:
                    # Unpickle the batch
                    actions = pickle.loads(data)
                    if not isinstance(actions, list):
                        actions = [actions]
                    return actions
        except pickle.UnpicklingError:
            logging.exception("Error unpickling data")
