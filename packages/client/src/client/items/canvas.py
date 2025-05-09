from typing import Callable, Tuple, override

import pygame
from client.colors import BLACK, WHITE
from client.game_object import GameObject
from client.game_state import GameState
from shared.actions.draw_action import DrawAction

LEFT_CLICK = 1
RIGHT_CLICK = 3
MOUSE_BUTTONS_TUPLE = (1, 3)


class Canvas(GameObject):
    def __init__(
        self,
        x,
        y,
        width,
        height,
        on_draw: Callable[[DrawAction], None],
        state: GameState,
    ):
        super().__init__(x, y, width, height)
        self.on_draw = on_draw
        self.surface = pygame.Surface((width, height))
        self.surface.fill(WHITE)
        self.last_pos: pygame.Vector2 = None
        self.is_drawing = False
        self.state = state

    def is_mouse_over(self, mouse_pos):
        return self.surface.get_rect(topleft=(self.x, self.y)).collidepoint(mouse_pos)

    @override
    def handle_event(self, event):
        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and self.is_mouse_over(event.pos)
            and event.button in MOUSE_BUTTONS_TUPLE
        ):
            self.is_drawing = True
            self.last_pos = self._normalizeCoordinates(event.pos)

        elif event.type == pygame.MOUSEMOTION:
            if self.is_mouse_over(event.pos):
                if self.is_drawing:
                    self._create_draw_action(event.pos, event.buttons.index(1) + 1)
                else:
                    self.last_pos = None
            else:
                self.is_drawing = False
                self.last_pos = None

        elif (
            event.type == pygame.MOUSEBUTTONUP
            and self.is_mouse_over(event.pos)
            and event.button in MOUSE_BUTTONS_TUPLE
        ):
            self._create_draw_action(event.pos, event.button)
            self.is_drawing = False
            self.last_pos = None

    def _create_draw_action(self, pos: Tuple[int, int], button: int):
        current_pos = self._normalizeCoordinates(pos)
        if self.last_pos:
            color = (
                WHITE
                if self.state.is_eraser
                else self.state.primary_color
                if button == LEFT_CLICK
                else self.state.secondary_color
            )
            self.on_draw(
                DrawAction(self.last_pos, current_pos, color, self.state.brush_size)
            )
        self.last_pos = current_pos

    @override
    def draw(self, surface):
        surface.blit(self.surface, (self.x, self.y))
        pygame.draw.rect(
            surface, BLACK, self.surface.get_rect(topleft=(self.x, self.y)), 2, 2
        )

    def _normalizeCoordinates(self, pos: Tuple[int, int]):
        return pygame.Vector2(pos[0] - self.x, pos[1] - self.y)
