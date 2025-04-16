import pygame
from shared.action import Action


class DrawAction(Action):
    def __init__(
        self, start_pos: float, end_pos: float, color: pygame.color, brush_size: int
    ):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.color = color
        self.brush_size = brush_size
        self.color = color
        self.brush_size = brush_size
