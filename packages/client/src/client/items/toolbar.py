import pygame
from client.colors import (
    BLACK,
    DARK_BLUE,
    DARK_GRAY,
    GOLD,
    GRAY,
    GREEN,
    LIGHT_BLUE,
    LIGHT_GRAY,
    ORANGE,
    PINK,
    PURPLE,
    RED,
    WHITE,
    YELLOW,
)
from client.game_state import GameState
from client.items.button import Button

COLORS = [
    WHITE,
    BLACK,
    GRAY,
    DARK_GRAY,
    LIGHT_GRAY,
    LIGHT_BLUE,
    DARK_BLUE,
    YELLOW,
    ORANGE,
    PINK,
    PURPLE,
    GREEN,
    RED,
    GOLD,
]


class Toolbar:
    def __init__(self, state: GameState, rect: pygame.Rect):
        self.state = state
        self.rect = rect
        self.buttons = self._generate_buttons()

    def draw(self, surface: pygame.Surface):
        for i, triangle in enumerate(self._generate_current_color_polygon()):
            pygame.draw.polygon(
                surface,
                self.state.primary_color if i == 0 else self.state.secondary_color,
                triangle,
            )

        for btn in self.buttons:
            btn.draw(surface)

    def handle_event(self, event: pygame.event.Event):
        for btn in self.buttons:
            btn.handle_event(event)

    def _generate_buttons(self):
        color_rect_size = self.rect.height // 2
        start_x = self.rect.x + self.rect.height + 10
        start_y = self.rect.y
        return [
            Button(
                start_x + row * color_rect_size,
                start_y + col * color_rect_size,
                color_rect_size,
                color_rect_size,
                (*color, 120),
                color,
                on_click=lambda color=color: self.state.primary_color.update(*color),
                on_right_click=lambda color=color: self.state.secondary_color.update(
                    *color
                ),
                border=False,
                border_radius=2,
            )
            for i, color in enumerate(COLORS)
            if (row := i // 2, col := i % 2)
        ]

    def _generate_current_color_polygon(self):
        return (
            [
                self.rect.topleft,
                self.rect.bottomleft,
                (self.rect.left + self.rect.height, self.rect.top),
            ],
            [
                (self.rect.left + self.rect.height, self.rect.top),
                (self.rect.left + self.rect.height, self.rect.bottom),
                self.rect.bottomleft,
            ],
        )
