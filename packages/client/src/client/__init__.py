import logging

import pygame
from shared.actions import Action
from shared.actions.init_game_state_action import InitGameStateAction
from shared.actions.player_list_action import PlayerListAction
from shared.actions.start_game_action import StartGameAction

from client.client_socket import ClientSocket
from client.game import Game
from client.game_state import GameState
from client.menu import Menu
from client.window import Window

WIDTH, HEIGHT = 1200, 800
BACKGROUND_COLOR = (240, 240, 255)


class UserInterface:
    def __init__(self):
        """
        Initializes Pygame, game state, UI windows, and the network client
        """
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Skribbl.io Clone by Noam Genish")
        self.clock = pygame.time.Clock()
        self.state = GameState()
        self.windows: tuple[Window] = (Menu(self), Game(self))
        self.active_window_idx = 0
        self.client = ClientSocket(on_action=self.on_action)

    @property
    def active_window(self):
        """
        Returns the currently active UI window.
        """
        return self.windows[self.active_window_idx]

    def on_action(self, action: Action):
        """
        Handles incoming actions by updating game state or UI based on their type
        """
        if isinstance(action, InitGameStateAction):
            self.state.my_player_id = action.you
            self.state.players_info = action.players_list
            self.state.chat_messages = action.chat_messages
            self.state.max_rounds = action.max_rounds
        elif isinstance(action, StartGameAction):
            self.show_game()
        elif isinstance(action, PlayerListAction):
            self.state.players_info = action.players_list
        self.active_window.on_action(action)

    def show_menu(self):
        """
        Sets the active window to the menu
        """
        self.active_window_idx = 0

    def show_game(self):
        """
        Sets the active window to the game.
        """
        self.active_window_idx = 1

    def quit_game(self):
        """
        Stops the game and closes the client connection
        """
        self.state.running = False
        self.client.close_client()

    def run(self):
        """
        Runs the game loop, handling events, updating, and drawing the active window at 60 FPS
        """
        while self.state.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()
                    return None

                self.active_window.handle_event(event)

            self.active_window.update()

            # Draw the game
            self.screen.fill(BACKGROUND_COLOR)
            self.active_window.draw(self.screen)

            # Update the display
            pygame.display.update()

            # Cap the framerate
            self.clock.tick(60)


def main():
    """
    Starts the user interface, handling any unexpected errors, and ensures Pygame quits afterward
    """
    ui = UserInterface()
    try:
        ui.run()
    except Exception:
        logging.exception("Unexpected Error")
        ui.quit_game()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
