from typing import override
import pygame

from skribbl.actions.draw_action import DrawAction
from skribbl.client.game_object import GameObject


class DrawingSurface(GameObject):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.surface = pygame.Surface((width, height))
        self.surface.fill(color=(255, 255, 255))
        self.last_pos = None
        self.is_drawing = False

    @override
    def is_mouse_over(self, mouse_pos):
        return self.surface.get_rect(topleft=(self.x, self.y)).collidepoint(mouse_pos)

    @override
    def handle_event(self, event):
        action = None
        if self.is_mouse_over(event.pos):
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    self.is_drawing = True
                    self.last_pos = self._normalizeCoordinates(event.pos)

            elif event.type == pygame.MOUSEMOTION:
                if self.is_drawing:
                    current_pos = self._normalizeCoordinates(event.pos)
                    if self.last_pos:
                        # color = (255, 255, 255) if self.is_eraser else self.selected_color
                        action = DrawAction(self.last_pos, current_pos, (0, 0, 0), 5)
                    self.last_pos = current_pos
                else:
                    self.last_pos = None

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                self.is_drawing = False
                self.last_pos = None

        return action

    @override
    def draw(self, surface):
        surface.blit(self.surface, (self.x, self.y))

    def _normalizeCoordinates(self, pos):
        return (pos[0] - self.x, pos[1] - self.y)
