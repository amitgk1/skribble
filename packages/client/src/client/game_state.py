import queue
from uuid import UUID

import pygame
from shared.chat_message import ChatMessage
from shared.player import Player


class GameState:
    def __init__(self):
        """
        Initializes the game state with various attributes like player info, drawing settings, chat messages, and round details
        """
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
        self.round = 0
        self.max_rounds = 0
        self.winners: list[UUID] = None

    def get_player_by_id(self, id: UUID):
        """
        Finds and returns a player by their ID, or None if not found
        """
        return next((p for p in self.players_info if p.id == id), None)

    def me(self):
        """
        Returns the player object corresponding to the current player
        """
        return self.get_player_by_id(self.my_player_id)

    def ready_to_draw(self):
        """
        Checks if the current player is ready to draw (if it's their turn and a word is set).
        """
        return self.me().is_player_turn and self.current_word

    def active_player(self):
        """
        Finds and returns the player whose turn it is, or None if no player is currently active
        """
        return next(filter(lambda p: p.is_player_turn, self.players_info), None)

    def am_i_a_winner(self) -> bool:
        """
        Checks if the current player is among the winners.
        """
        return self.winners and self.my_player_id in self.winners
