# game_object.py - Base class for all game objects

import pygame


class GameObject:
    def __init__(self, x: int, y: int, width: float, height: float):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def handle_event(self, event: pygame.event.Event):
        # Default implementation: do nothing
        pass

    def draw(self, surface: pygame.Surface):
        # Default implementation: draw a simple rectangle
        pass
