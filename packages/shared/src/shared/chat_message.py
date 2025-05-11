from dataclasses import dataclass


@dataclass
class ChatMessage:
    player_name: str
    text: str
    color: tuple[int, int, int]
