import socket
import threading
from dataclasses import dataclass, field

from shared.actions.draw_action import DrawAction


@dataclass
class Turn:
    timer: threading.Timer
    word: str = None
    active_player: socket.socket = None
    draw_actions: list[DrawAction] = field(default_factory=list)
    player_score_update: dict[socket.socket, int] = field(default_factory=dict)
    start_time: float = None
