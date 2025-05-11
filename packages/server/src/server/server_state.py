import socket
from dataclasses import dataclass, field

from shared.chat_message import ChatMessage
from shared.player import Player


@dataclass
class ServerState:
    players: dict[socket.socket, Player] = field(default_factory=dict)
    chat_messages: list[ChatMessage] = field(default_factory=list)

    def get_player_list(self):
        return list(self.players.values())
