import queue
from uuid import UUID

from shared.player import Player


class GameState:
    def __init__(self):
        self.running = True
        self.pending_draw_lines = queue.Queue()
        self.players_info: list[Player] = None
        self.my_player_id: UUID
