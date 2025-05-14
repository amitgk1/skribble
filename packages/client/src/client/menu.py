from typing import TYPE_CHECKING, override

import pygame
from shared.actions.player_name_action import PlayerNameAction
from shared.actions.start_game_action import StartGameAction
from shared.colors import BLACK, DARK_BLUE, GREEN, ORANGE, PINK, RED, YELLOW
from shared.utils import debounce

from client.fonts import FONT_LG, FONT_MD
from client.items.bubble import Bubble
from client.items.button import Button
from client.items.players_list import PlayersList
from client.items.popup import Popup
from client.items.text_input import TextInput
from client.items.title import Title
from client.window import Window

if TYPE_CHECKING:
    from client import UserInterface


class Menu(Window):
    def __init__(self, ui: "UserInterface"):
        """
        Initializes the user interface with decorative bubbles, a start button, a "How to Play" button, and an "Exit" button, all positioned on the screen
        """
        self.ui = ui

        # Create decorative bubbles
        self.bubbles = [Bubble(self.ui.screen.get_rect()) for _ in range(30)]

        # Create buttons
        start_button_width = 200
        self.start_button = Button(
            self.ui.screen.get_width() // 2 - start_button_width // 2,
            self.ui.screen.get_height() - 120,
            start_button_width,
            60,
            GREEN,
            (120, 255, 120),
            "Start Game!",
            BLACK,
            disabled=True,
            on_click=self._on_start,
            border_radius=10,
        )

        # Create additional buttons
        button_width = 150
        button_height = 50
        button_spacing = 20

        # Button positions will be centered and evenly spaced
        buttons_start_x = self.ui.screen.get_width() // 2 - (
            2 * button_width + 1 * button_spacing
        )

        self.help_button = Button(
            buttons_start_x + button_width + button_spacing,
            self.ui.screen.get_height() - 200,
            button_width,
            button_height,
            YELLOW,
            ORANGE,
            "How to Play",
            BLACK,
            on_click=self._toggle_help,
            border_radius=10,
        )

        self.exit_button = Button(
            buttons_start_x + 2 * (button_width + button_spacing),
            self.ui.screen.get_height() - 200,
            button_width,
            button_height,
            PINK,
            RED,
            "Exit",
            BLACK,
            on_click=self.ui.quit_game,
            border_radius=10,
        )

        # Create text input for player name
        self.name_input = TextInput(
            self.ui.screen.get_width() // 2 - 150,
            self.ui.screen.get_height() // 2 - 20,
            300,
            50,
            on_input=self._update_player_name,
        )

        # Connected players section
        self.players_list = PlayersList(
            pygame.Rect(
                self.ui.screen.get_width() - 250,
                120,
                220,
                self.ui.screen.get_height() - 250,
            )
        )

        # Track if help popups are open
        self.popup: Popup = None

        # Logo bounce animation
        self.logo_y_offset = 0
        self.logo_direction = 1
        self.logo_speed = 0.5

        self.items = [
            self.name_input,
            self.start_button,
            self.help_button,
            self.exit_button,
        ]

    @override
    def handle_event(self, event):
        """Handle user input events"""

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if clicking outside popups to close them
            if self.popup and not self.popup.popup_rect.collidepoint(event.pos):
                self.popup = None

        if self.popup:
            self.popup.handle_event(event)

        for item in self.items:
            item.handle_event(event)

    @override
    def update(self):
        """Update all animated elements"""
        # Update decorative bubbles
        for bubble in self.bubbles:
            bubble.update()

        # Update logo bounce animation
        self.logo_y_offset += self.logo_direction * self.logo_speed
        if abs(self.logo_y_offset) > 10:
            self.logo_direction *= -1

        # updates the state of the start button, disabling it if there are fewer than 2 players or the current player is not the owner
        self.start_button.disabled = (
            len(self.ui.state.players_info) < 2 or not self.ui.state.me().is_owner
        )

    @override
    def draw(self, surface: pygame.Surface):
        """Draw the entire menu"""

        # Draw decorative elements
        for bubble in self.bubbles:
            bubble.draw(surface)

        # Draw title with shadow and bounce effect
        Title.draw_title(
            surface,
            self.ui.screen.get_width() // 2,
            80 + self.logo_y_offset,
        )

        # Draw subtitle
        subtitle = "Draw, Guess & Have Fun!"
        subtitle_surf = FONT_LG.render(subtitle, True, DARK_BLUE)
        subtitle_rect = subtitle_surf.get_rect(
            center=(self.ui.screen.get_width() // 2, 150 + self.logo_y_offset)
        )
        surface.blit(subtitle_surf, subtitle_rect)

        # Draw name input label
        name_label = FONT_MD.render("Enter Your Name:", True, BLACK)
        name_label_rect = name_label.get_rect(
            center=(
                self.ui.screen.get_width() // 2,
                self.ui.screen.get_height() // 2 - 60,
            )
        )
        surface.blit(name_label, name_label_rect)

        # TODO: use self.items instead after giving it a type
        # Draw name input box
        self.name_input.draw(surface)

        # Draw connected players section
        self.players_list.draw(self.ui.state, surface)

        # Draw buttons
        self.start_button.draw(surface)
        self.help_button.draw(surface)
        self.exit_button.draw(surface)

        # Draw popups if active
        if self.popup:
            self.popup.draw(surface)

    def _toggle_help(self):
        """
        method toggles the help popup on and off.
        If the popup is currently active, it closes it;
        if it's not active, it creates a new Popup object with instructions on how to play the game
        """
        if self.popup:
            self.popup = None
        else:
            self.popup = Popup(
                "How to Play",
                [
                    "1. One player draws a word",
                    "2. Others guess the word",
                    "3. Faster guesses get more points",
                    "4. Each round has a new artist",
                    "5. Have fun and be creative!",
                ],
                self.ui.screen.get_rect(),
                on_close=self._on_popup_close,
            )

    def _on_popup_close(self):
        self.popup = None

    @debounce(0.5)
    def _update_player_name(self, text: str):
        """
        Sends the player's updated name to the server using ClientSocket
        this function is debounced, meaning it will be called once there are no more calls to this function
        after 0.5sec
        this is used to only send the last keyboard input from the user when he types fast
        """
        self.ui.client.send_action_to_server(PlayerNameAction(text), immediate=True)

    def _on_start(self):
        """
        Sends a StartGameAction to the server to start the game and switches the UI to the game screen
        """
        self.ui.client.send_action_to_server(StartGameAction(), immediate=True)
        self.ui.show_game()
