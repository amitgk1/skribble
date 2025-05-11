from typing import Callable

import pygame
from client.game_state import GameState
from client.items.button import BaseButton, Button
from shared.colors import (
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

BRUSH_SIZES = [2, 5, 10, 15, 20]


class Toolbar:
    def __init__(
        self, state: GameState, rect: pygame.Rect, on_clear: Callable[[], None]
    ):
        self.state = state
        self.rect = rect
        self.buttons = self._generate_buttons()
        self.clear_button = self._generate_clear_button(on_clear)
        self.eraser_button = self._generate_eraser_button()
        self.brush_size_buttons = self._generate_brush_size_selector()

    def draw(self, surface: pygame.Surface):
        for i, triangle in enumerate(self._generate_current_color_polygon()):
            pygame.draw.polygon(
                surface,
                self.state.primary_color if i == 0 else self.state.secondary_color,
                triangle,
            )

        for btn in self.buttons:
            btn.draw(surface)

        self.clear_button.draw(surface)
        self.eraser_button.draw(surface)

        for i, btn in enumerate(self.brush_size_buttons):
            btn.surf.fill((*WHITE, 0))
            pygame.draw.circle(
                btn.surf, BLACK, btn.surf.get_rect().center, BRUSH_SIZES[i]
            )
            if self.state.brush_size == BRUSH_SIZES[i]:
                pygame.draw.rect(btn.surf, RED, btn.surf.get_rect(), 1, border_radius=2)
            btn.draw(surface)

    def update(self):
        # Because update runs after handle_event we can force the button into hover mode so the color would stick
        if self.state.is_eraser:
            self.eraser_button.hover = True

    def handle_event(self, event: pygame.event.Event):
        for btn in self.buttons:
            btn.handle_event(event)
        self.clear_button.handle_event(event)
        self.eraser_button.handle_event(event)
        for brush_size_btn in self.brush_size_buttons:
            brush_size_btn.handle_event(event)

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
                (*color, 240),
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

    def _generate_clear_button(self, on_clear: Callable[[], None]):
        return Button(
            self.rect.right - 50,
            self.rect.y,
            50,
            self.rect.height,
            LIGHT_BLUE,
            DARK_BLUE,
            image_path="assets/trash-can.png",
            on_click=on_clear,
        )

    def _generate_eraser_button(self):
        return Button(
            self.rect.right - 110,
            self.rect.y,
            50,
            self.rect.height,
            LIGHT_BLUE,
            DARK_BLUE,
            image_path="assets/eraser.png",
            on_click=self._on_eraser,
        )

    def _generate_brush_size_selector(self):
        start_x = self.buttons[-1].x + self.buttons[-1].width + 10
        start_y = self.rect.y
        brush_size_btns = [
            BaseButton(
                start_x + i * 55,
                start_y,
                50,
                50,
                on_click=lambda size=size: self._update_brush_size(size),
            )
            for i, size in enumerate(BRUSH_SIZES)
        ]
        return brush_size_btns

    def _update_brush_size(self, size: int):
        self.state.brush_size = size

    def _on_eraser(self):
        self.state.is_eraser = not self.state.is_eraser
