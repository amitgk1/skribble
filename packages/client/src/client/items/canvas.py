from typing import Callable, Tuple, override

import pygame
from client.colors import BLACK, WHITE
from client.constants import LEFT_CLICK, MOUSE_BUTTONS_TUPLE
from client.game_object import GameObject
from client.game_state import GameState
from shared.actions.draw_action import DrawAction


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
        self.cursor_surface = pygame.Surface((100, 100))
        self.cursor_surface.set_colorkey(WHITE)
        self.cursor_surf_center = (50, 50)
        self.cursor = pygame.cursors.Cursor(
            self.cursor_surf_center,
            self.cursor_surface,
        )

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
                self._set_cursor_as_brush()
                if self.is_drawing:
                    self._create_draw_action(event.pos, event.buttons.index(1) + 1)
                else:
                    self.last_pos = None
            else:
                self._set_cursor_as_default()
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

    @override
    def draw(self, surface):
        surface.blit(self.surface, (self.x, self.y))
        # Border
        pygame.draw.rect(
            surface, BLACK, self.surface.get_rect(topleft=(self.x, self.y)), 2, 2
        )

    def update(self):
        self.cursor_surface.fill(WHITE)
        pygame.draw.circle(
            self.cursor_surface,
            self._get_drawing_color(LEFT_CLICK),
            self.cursor_surf_center,
            self.state.brush_size,
        )
        pygame.draw.circle(
            self.cursor_surface,
            BLACK,
            self.cursor_surf_center,
            self.state.brush_size,
            pygame.math.clamp(self.state.brush_size // 2, 1, 2),
        )

    def _get_drawing_color(self, button: int):
        return (
            pygame.Color(WHITE)
            if self.state.is_eraser
            else self.state.primary_color
            if button == LEFT_CLICK
            else self.state.secondary_color
        )

    def _set_cursor_as_brush(self):
        if pygame.mouse.get_cursor() != self.cursor:
            pygame.mouse.set_cursor(self.cursor)

    def _set_cursor_as_default(self):
        current = pygame.mouse.get_cursor()
        if current.type != "system" and current.data[0] != pygame.SYSTEM_CURSOR_ARROW:
            pygame.mouse.set_cursor(pygame.Cursor())

    def _create_draw_action(self, pos: Tuple[int, int], button: int):
        current_pos = self._normalizeCoordinates(pos)
        if self.last_pos:
            color = self._get_drawing_color(button)
            self.on_draw(
                DrawAction(self.last_pos, current_pos, color, self.state.brush_size)
            )
        self.last_pos = current_pos

    def clear_canvas(self):
        self.surface.fill(WHITE)

    def _normalizeCoordinates(self, pos: Tuple[int, int]):
        return pygame.Vector2(pos[0] - self.x, pos[1] - self.y)
