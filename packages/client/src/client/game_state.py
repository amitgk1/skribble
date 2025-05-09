import queue
from uuid import UUID

import pygame
from shared.player import Player


class GameState:
    def __init__(self):
        self.running = True
        self.pending_draw_lines = queue.Queue()
        self.players_info: list[Player] = None
        self.my_player_id: UUID
        self.current_word: str
        self.brush_size: int = 5
        self.is_eraser: bool = False
        self.primary_color: pygame.Color = pygame.Color("black")
        self.secondary_color: pygame.Color = pygame.Color("white")

    def me(self):
        return next(p for p in self.players_info if p.id == self.my_player_id)
