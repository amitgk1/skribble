import pygame
from client.colors import (
    DARK_GRAY,
    GREEN,
    LIGHT_BLUE,
    ORANGE,
    PINK,
    PURPLE,
    RED,
    YELLOW,
)
from client.fonts import FONT_TITLE

colors = [YELLOW, ORANGE, PINK, PURPLE, GREEN, LIGHT_BLUE, RED]


class Title:
    @staticmethod
    def draw_title(
        surface: pygame.Surface,
        x: int,
        y: int,
        text="Scribbl.io!",
        with_shadow=True,
        background: pygame.Color = None,
    ):
        """Draw the title with a shadow effect"""
        chars_width = [FONT_TITLE.size(char)[0] for char in text]
        text_width = sum(chars_width)
        start_x = x - text_width // 2

        for i, char in enumerate(text):
            color = colors[i % len(colors)]
            char_surf = FONT_TITLE.render(char, True, color, background)
            if with_shadow:
                shadow_surf = FONT_TITLE.render(char, True, DARK_GRAY)
                surface.blit(
                    shadow_surf, (start_x + 5, y - shadow_surf.get_height() // 2 + 5)
                )
            surface.blit(char_surf, (start_x, y - char_surf.get_height() // 2))
            start_x += chars_width[i]
