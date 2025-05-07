import pygame
from client.colors import WHITE
from client.items.text_input import TextInput


class Chat:
    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.text_input = TextInput(
            rect.x,
            rect.bottom - 30,
            rect.width,
            30,
            on_input=lambda x: None,
            on_enter=lambda x: self.text_input.clear(),
            placeholder="Type your guess here...",
        )

    def handle_event(self, event: pygame.event.Event):
        self.text_input.handle_event(event)

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=10)
        self.text_input.draw(surface)
