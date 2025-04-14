import pickle
import socket
from skribbl.actions.action import Action


class ActionProtocol:
    @staticmethod
    def send_batch(sock: socket.socket, batch: list[Action]):
        if not batch:
            return
            
        serialized = pickle.dumps(batch)
        
        # First send the length of the pickled data as a fixed-length (4-byte) integer
        message_length = len(serialized)
        size = message_length.to_bytes(4, byteorder='big')

        # Then send the actual data
        try:
            sock.sendall(size + serialized)
        except sock.error as e:
            print(f"Failed to send batch: {e}")

    @staticmethod
    def recv_batch_raw(sock: socket.socket):
        # First read the 4-byte message length header
        header = sock.recv(4)
        if not header or len(header) < 4:
            return None
        
        # Unpack the message length
        message_length = int.from_bytes(header, byteorder='big')
        
        # Read the actual message data
        data = b""
        while len(data) < message_length:
            chunk = sock.recv(min(4096, message_length - len(data)))
            if not chunk:
                raise RuntimeError("Socket connection broken")
            data += chunk

        return (header,data)

    @staticmethod
    def recv_batch(sock: socket.socket) -> list[Action]:
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
        except pickle.UnpicklingError as e:
                print(f"Error unpickling data: {e}")