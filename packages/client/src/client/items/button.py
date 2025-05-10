from typing import Callable, Tuple, override

import pygame
from client.colors import BLACK, DARK_GRAY, WHITE
from client.fonts import FONT_MD
from client.game_object import GameObject


class BaseButton(GameObject):
    def __init__(
        self,
        x,
        y,
        width,
        height,
        on_click: Callable[[], None] = None,
        on_right_click: Callable[[], None] = None,
        disabled=False,
        surface_flags=pygame.SRCALPHA,
    ):
        super().__init__(x, y, width, height)
        self.surf = pygame.Surface((width, height), flags=surface_flags)
        self.surf.fill(WHITE)
        self.disabled = disabled
        self.on_click = on_click
        self.on_right_click = on_right_click

    @override
    def draw(self, surface):
        surface.blit(self.surf, (self.x, self.y))

    @override
    def handle_event(self, event):
        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and self.is_mouse_over(event.pos)
            and not self.disabled
        ):
            if event.button == 1 and self.on_click:
                self.on_click()
            elif event.button == 3 and self.on_right_click:
                self.on_right_click()

    def is_mouse_over(self, mouse_pos):
        return self.surf.get_rect(topleft=(self.x, self.y)).collidepoint(mouse_pos)


class Button(BaseButton):
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
        image_path: str = None,
    ):
        super().__init__(x, y, width, height, on_click, on_right_click, disabled)
        self.text = text
        self.color = pygame.color.Color(color)
        self.hover_color = hover_color
        self.text_color = text_color
        self.hover = False
        self.border = border
        self.border_radius = border_radius
        self.image = None
        if image_path:
            try:
                self.image = pygame.image.load(image_path)
                self.image = pygame.transform.scale(
                    self.image, (width - 10, height - 10)
                )
            except pygame.error:
                print(f"Unable to load image {image_path}")

    @override
    def draw(self, surface: pygame.Surface):
        # Determine the color based on disabled/hover state
        current_color = (
            self.color.grayscale()
            if self.disabled
            else (self.hover_color if self.hover else self.color)
        )

        pygame.draw.rect(
            self.surf,
            current_color,
            self.surf.get_rect(),
            border_radius=self.border_radius,
        )
        if self.border:
            pygame.draw.rect(
                self.surf,
                BLACK,
                self.surf.get_rect(),
                2,
                border_radius=self.border_radius,
            )

        if self.text:
            text_surf = FONT_MD.render(
                self.text, True, DARK_GRAY if self.disabled else self.text_color
            )
            text_rect = text_surf.get_rect(center=self.surf.get_rect().center)
            self.surf.blit(text_surf, text_rect)
        elif self.image:
            self.surf.blit(self.image, (5, 5))

        super().draw(surface)

    @override
    def handle_event(self, event: pygame.event.Event):
        super().handle_event(event)
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.is_mouse_over(event.pos)
