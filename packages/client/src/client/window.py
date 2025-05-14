import pygame
from shared.actions import Action


class Window:
    def handle_event(self, event: pygame.event.Event) -> None:
        """
        process pygame events like mouse movement or keyboard user input
        """
        pass

    def update(self) -> None:
        """
        update the internal class properties or the game state - on each frame
        """
        pass

    def draw(self, surface: pygame.Surface) -> None:
        """
        actually render the objects to the surface (usually the screen)
        """
        pass

    def on_action(self, action: Action) -> None:
        """
        when the server sends an action to the client, we can process it here
        """
        pass
