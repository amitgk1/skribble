import socket
from dataclasses import dataclass, field

from shared.chat_message import ChatMessage
from shared.player import Player


@dataclass
class ServerState:
    """
    Manages the game state, including whether the game is playing, a dictionary of players, and a list of chat messages. It also provides a method to get the list of players
    """

    is_playing: bool = False
    players: dict[socket.socket, Player] = field(default_factory=dict)
    chat_messages: list[ChatMessage] = field(default_factory=list)

    def get_player_list(self):
        return list(self.players.values())
