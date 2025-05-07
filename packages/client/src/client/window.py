import pygame
from shared.actions import Action


class Window:
    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        pass

    def on_action(self, action: Action) -> None:
        pass
