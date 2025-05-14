from dataclasses import dataclass


@dataclass
class ChatMessage:
    """
    A simple class to represent a chat message. it has the sending player name (or SYSTEM for server messages),
    the text the player sent, usually to guess the word drawn
    and the color the text should appear in the chat box
    """

    player_name: str
    text: str
    color: tuple[int, int, int]
