# game_object.py - Base class for all game objects
from typing import Tuple

import pygame


class GameObject:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def handle_event(self, event: pygame.event.Event):
        # Default implementation: do nothing
        pass

    def draw(self, surface, offset=(0, 0)):
        # Default implementation: draw a simple rectangle
        pass

    def is_mouse_over(self, mouse_pos: Tuple[float, float]) -> bool:
        pass
