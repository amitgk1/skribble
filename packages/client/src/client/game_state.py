import queue
from uuid import UUID

import pygame
from shared.chat_message import ChatMessage
from shared.player import Player


class GameState:
    def __init__(self):
        self.running = True
        self.pending_draw_lines = queue.Queue()
        self.players_info: list[Player] = []
        self.my_player_id: UUID
        self.current_word: str = None
        self.brush_size: int = 5
        self.is_eraser: bool = False
        self.primary_color: pygame.Color = pygame.Color("black")
        self.secondary_color: pygame.Color = pygame.Color("white")
        self.chat_messages: list[ChatMessage] = []

    def get_player_by_id(self, id: UUID):
        return next((p for p in self.players_info if p.id == id), None)

    def me(self):
        return self.get_player_by_id(self.my_player_id)

    def ready_to_draw(self):
        return self.me().is_player_turn and self.current_word

    def active_player(self):
        return next(filter(lambda p: p.is_player_turn, self.players_info), None)
