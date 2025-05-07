from typing import Callable, Tuple

import pygame
from client.colors import BLACK, DARK_GRAY
from client.fonts import FONT_MD

system_no_cursor = pygame.Cursor(pygame.SYSTEM_CURSOR_NO)


class Button:
    """Interactive button with hover effects"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        color: Tuple[int, int, int],
        hover_color: Tuple[int, int, int],
        text_color: Tuple[int, int, int],
        on_click: Callable[[], None],
        disabled: bool = False,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = pygame.color.Color(color)
        self.hover_color = pygame.color.Color(hover_color)
        self.text_color = pygame.color.Color(text_color)
        self.disabled = disabled
        self.on_click = on_click
        self.hover = False

    def draw(self, surface: pygame.Surface):
        # Determine the color based on disabled/hover state
        current_color = (
            self.color.grayscale()
            if self.disabled
            else (self.hover_color if self.hover else self.color)
        )

        # Draw button with rounded corners
        pygame.draw.rect(surface, current_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)  # Border

        # Draw text
        text_surf = FONT_MD.render(
            self.text, True, DARK_GRAY if self.disabled else self.text_color
        )
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event: pygame.event.Event):
        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
            and not self.disabled
        ):
            self.on_click()

        elif event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
