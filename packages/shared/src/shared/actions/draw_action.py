from dataclasses import dataclass

import pygame

from shared.actions import Action


@dataclass
class DrawAction(Action):
    start: pygame.Vector2
    end: pygame.Vector2
    color: pygame.color
    brush_size: int
