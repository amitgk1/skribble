from typing import Callable

import pygame
from client.fonts import FONT_SM
from client.game_state import GameState
from client.items.text_input import TextInput
from pygame_menu import locals
from pygame_menu._scrollarea import ScrollArea
from shared.colors import WHITE
from shared.constants import SYSTEM_PLAYER_ID

TEXT_INPUT_HEIGHT = 30


class Chat:
    def __init__(
        self, rect: pygame.Rect, state: GameState, on_enter: Callable[[str], None]
    ):
        self.state = state
        self.area = ScrollArea(
            rect.width,
            rect.height - TEXT_INPUT_HEIGHT,
            area_color=WHITE,
            border_width=1,
            scrollbars=(locals.POSITION_SOUTH, locals.POSITION_EAST),
        )
        self.inner_surface = pygame.Surface((1000, 1000))
        self.area.set_world(self.inner_surface)
        self.area.set_position(rect.x, rect.y)
        self.text_input = TextInput(
            rect.x,
            rect.bottom - TEXT_INPUT_HEIGHT,
            rect.width,
            TEXT_INPUT_HEIGHT,
            on_input=lambda x: None,
            on_enter=lambda text: self._on_text_input_enter(text, on_enter),
            placeholder="Type your guess here...",
        )

    def handle_event(self, event: pygame.event.Event):
        self.area.update([event])
        self.text_input.handle_event(event)

    def update(self):
        if self.inner_surface.get_height() < len(self.state.chat_messages) * (
            FONT_SM.get_height() + 5
        ):
            self.inner_surface = pygame.Surface(
                (self.inner_surface.get_width(), self.inner_surface.get_height() * 2)
            )
            self.area.set_world(self.inner_surface)

    def draw(self, surface: pygame.Surface):
        self.inner_surface.fill(WHITE)
        for i, chat_msg in enumerate(self.state.chat_messages):
            text = (
                chat_msg.text
                if chat_msg.player_name == SYSTEM_PLAYER_ID
                else f"{chat_msg.player_name}: {chat_msg.text}"
            )
            text_surf = FONT_SM.render(text, True, chat_msg.color)
            self.inner_surface.blit(text_surf, (5, i * (FONT_SM.get_height() + 5)))
        self.area.draw(surface)
        if (
            self.state.active_player()
            and self.state.active_player().id != self.state.my_player_id
        ):
            self.text_input.draw(surface)

    def _on_text_input_enter(self, text: str, on_enter: Callable[[str], None]):
        self.text_input.clear()
        on_enter(text)
