from typing import Callable, Tuple

import pygame
from client.colors import BLACK, DARK_GRAY
from client.fonts import FONT_MD


class Button:
    """Interactive button with hover effects"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        color: Tuple[int, int, int],
        hover_color: Tuple[int, int, int],
        text: str = None,
        text_color: Tuple[int, int, int] = None,
        on_click: Callable[[], None] = None,
        on_right_click: Callable[[], None] = None,
        disabled: bool = False,
        border_radius: int = -1,
        border: bool = True,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = pygame.color.Color(color)
        self.hover_color = hover_color
        self.text_color = text_color
        self.disabled = disabled
        self.on_click = on_click
        self.on_right_click = on_right_click
        self.hover = False
        self.border = border
        self.border_radius = border_radius

    def draw(self, surface: pygame.Surface):
        # Determine the color based on disabled/hover state
        current_color = (
            self.color.grayscale()
            if self.disabled
            else (self.hover_color if self.hover else self.color)
        )

        pygame.draw.rect(
            surface, current_color, self.rect, border_radius=self.border_radius
        )
        if self.border:
            pygame.draw.rect(
                surface, BLACK, self.rect, 2, border_radius=self.border_radius
            )

        if self.text:
            text_surf = FONT_MD.render(
                self.text, True, DARK_GRAY if self.disabled else self.text_color
            )
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

    def handle_event(self, event: pygame.event.Event):
        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and self.rect.collidepoint(event.pos)
            and not self.disabled
        ):
            if event.button == 1 and self.on_click:
                self.on_click()
            elif event.button == 3 and self.on_right_click:
                self.on_right_click()

        elif event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
