from typing import Callable

import pygame
from client.colors import BLACK, DARK_GRAY, LIGHT_BLUE, WHITE
from client.fonts import FONT_MD


class TextInput:
    """Text input field for player name"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        on_input: Callable[[str], None],
        max_length: int = 20,
        placeholder: str = "Enter your name...",
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.active = False
        self.placeholder = placeholder
        self.cursor_visible = True
        self.cursor_timer = 0
        self.max_length = max_length
        self.on_input = on_input

    def draw(self, surface: pygame.Surface):
        # Draw the input box with a slight shadow effect
        shadow_rect = self.rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        pygame.draw.rect(surface, DARK_GRAY, shadow_rect, border_radius=8)

        # Main input box
        box_color = LIGHT_BLUE if self.active else WHITE
        pygame.draw.rect(surface, box_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=8)  # Border

        # Render text or placeholder
        if self.text:
            text_surf = FONT_MD.render(self.text, True, BLACK)
        else:
            text_surf = FONT_MD.render(self.placeholder, True, DARK_GRAY)

        # Position the text
        text_rect = text_surf.get_rect(midleft=(self.rect.left + 10, self.rect.centery))
        surface.blit(text_surf, text_rect)

        # Draw cursor when active
        if self.active:
            # Update cursor blink timer
            self.cursor_timer += 1
            if self.cursor_timer >= 30:  # Toggle every 30 frames
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0

            if self.cursor_visible:
                if self.text:
                    cursor_x = text_rect.right + 2
                else:
                    cursor_x = text_rect.left

                cursor_height = text_rect.height - 6
                pygame.draw.line(
                    surface,
                    BLACK,
                    (cursor_x, self.rect.centery - cursor_height // 2),
                    (cursor_x, self.rect.centery + cursor_height // 2),
                    2,
                )

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                self.on_input(self.text)
            elif event.key == pygame.K_RETURN:
                self.active = False
            elif len(self.text) < self.max_length:
                # Only allow valid characters (alphanumeric and common symbols)
                if event.unicode.isprintable():
                    self.text += event.unicode
                    self.on_input(self.text)
