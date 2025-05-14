import socket
import threading
from dataclasses import dataclass, field

from shared.actions.draw_action import DrawAction


@dataclass
class Turn:
    """
    Represents a single turn in the game, with a timer for timeouts, a word to be guessed, the active player, drawing actions, player score updates, and a timestamp for when the turn started. It manages the state and progress of the game during each turn
    """

    timer: threading.Timer
    word: str = None
    active_player: socket.socket = None
    draw_actions: list[DrawAction] = field(default_factory=list)
    player_score_update: dict[socket.socket, int] = field(default_factory=dict)
    start_time: float = None
