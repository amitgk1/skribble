# game_object.py - Base class for all game objects

import pygame


class GameObject:
    def __init__(self, x: int, y: int, width: float, height: float):
        """
        Initializes a rectangular object with position and size.
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def handle_event(self, event: pygame.event.Event):
        """
        Provides a default event handler that does nothing
        """
        pass

    def draw(self, surface: pygame.Surface):
        """
        Provides a default draw method that does nothing.
        """
        pass
