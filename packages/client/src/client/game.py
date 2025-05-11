from typing import TYPE_CHECKING, Callable, override

import pygame
from shared.actions import Action
from shared.actions.chat_message_action import ChatMessageAction
from shared.actions.clear_canvas_action import ClearCanvasAction
from shared.actions.draw_action import DrawAction
from shared.actions.pick_word_action import PickWordAction
from shared.actions.update_word_action import UpdateWordAction
from shared.chat_message import ChatMessage
from shared.colors import BLACK, DARK_GRAY, LIGHT_GRAY, WHITE

from client.fonts import FONT_LG, FONT_MD, FONT_TITLE
from client.game_state import GameState
from client.items.button import Button
from client.items.chat import Chat
from client.items.players_list import PlayersList
from client.items.title import Title
from client.items.toolbar import Toolbar
from client.window import Window

if TYPE_CHECKING:
    from client import UserInterface

from client.items.canvas import Canvas

DRAWING_AREA_WIDTH, DRAWING_AREA_HEIGHT = 700, 500
DRAWING_AREA_X = 20
DRAWING_AREA_Y = 100

HEADER_COLOR = (70, 130, 180)
HEADER_HEIGHT = 80


class WordDisplay:
    def __init__(self, rect: pygame.Rect):
        self.rect = rect

    def draw(self, game_state: GameState, surface: pygame.Surface):
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=10)

        word_text = None
        if (
            not game_state.me().is_player_turn
            and not game_state.current_word
            and game_state.active_player()
        ):
            word_text = FONT_MD.render(
                f"{game_state.active_player().get_player_name(game_state.my_player_id)} is picking a word",
                True,
                DARK_GRAY,
            )
        elif game_state.current_word:
            word_text = FONT_TITLE.render(game_state.current_word, True, DARK_GRAY)

        if word_text:
            surface.blit(
                word_text,
                (
                    self.rect.x + (self.rect.width - word_text.get_width()) // 2,
                    self.rect.y + (self.rect.height - word_text.get_height()) // 2,
                ),
            )


class PickWordPopUp:
    def __init__(
        self,
        rect_bound: pygame.Rect,
        word_options: list[str],
        on_pick_word: Callable[[str], None],
    ):
        self.rect_bound = rect_bound
        self.on_pick_word = on_pick_word
        self.buttons = self._generate_word_options_buttons(word_options)

    def draw(self, surface: pygame.Surface):
        overlay = pygame.Surface(
            (self.rect_bound.width, self.rect_bound.height), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, self.rect_bound)

        title_surf = FONT_LG.render("Choose a word to draw:", True, WHITE)
        title_rect = title_surf.get_rect(
            center=(
                self.rect_bound.centerx,
                self.rect_bound.top + 10 + title_surf.get_height() // 2,
            )
        )
        surface.blit(title_surf, title_rect)

        for btn in self.buttons:
            btn.draw(surface)

    def handle_event(self, event):
        for btn in self.buttons:
            btn.handle_event(event)

    def _generate_word_options_buttons(self, word_options):
        width = 100
        spacing = 50
        height = 50
        y = self.rect_bound.centery - height // 2
        start_x = self.rect_bound.centerx - spacing - width * 1.5
        return [
            Button(
                x,
                y,
                width,
                height,
                WHITE,
                LIGHT_GRAY,
                word,
                BLACK,
                on_click=lambda word=word: self.on_pick_word(word),
            )
            for i, word in enumerate(word_options)
            if (x := start_x + i * (width + spacing))
        ]


class Game(Window):
    def __init__(self, ui: "UserInterface"):
        self.ui = ui

        # TODO: fix positioning to allow window resizing
        self.playersList = PlayersList(
            pygame.Rect(
                10,
                HEADER_HEIGHT + 20,
                self.ui.screen.get_width() // 2 - DRAWING_AREA_WIDTH // 2 - 5,
                DRAWING_AREA_HEIGHT,
            )
        )
        self.canvas = Canvas(
            self.playersList.player_list_rect.left
            + self.playersList.player_list_rect.width
            + 10,
            HEADER_HEIGHT + 20,
            DRAWING_AREA_WIDTH,
            DRAWING_AREA_HEIGHT,
            on_draw=self._on_draw,
            state=self.ui.state,
        )
        self.word_display = WordDisplay(
            pygame.Rect(
                self.canvas.x + self.canvas.width // 2 - self.canvas.width * 0.385,
                self.canvas.y - 60,
                self.canvas.width * 0.75,
                50,
            )
        )
        self.chat = Chat(
            pygame.Rect(
                self.canvas.x + self.canvas.width + 10,
                HEADER_HEIGHT + 20,
                200,
                DRAWING_AREA_HEIGHT,
            ),
            self.ui.state,
            self._on_chat_enter,
        )
        self.toolbar = Toolbar(
            self.ui.state,
            pygame.Rect(
                self.canvas.x,
                self.canvas.y + self.canvas.height + 5,
                DRAWING_AREA_WIDTH,
                50,
            ),
            on_clear=self._on_clear,
        )
        self.popup = None

    @override
    def handle_event(self, event):
        self.chat.handle_event(event)
        if self.ui.state.ready_to_draw():
            self.canvas.handle_event(event)
            self.toolbar.handle_event(event)
        if self.popup:
            self.popup.handle_event(event)

    @override
    def update(self):
        if self.ui.state.ready_to_draw():
            self.canvas.update()
            self.toolbar.update()
        self.chat.update()

    @override
    def on_action(self, action: Action):
        if isinstance(action, DrawAction):
            self.ui.state.pending_draw_lines.put(action)
        elif isinstance(action, ClearCanvasAction):
            self.canvas.clear_canvas()
        elif isinstance(action, PickWordAction):
            self.popup = PickWordPopUp(
                self.canvas.surface.get_rect(topleft=(self.canvas.x, self.canvas.y)),
                action.options,
                self._on_pick_word,
            )
        elif isinstance(action, UpdateWordAction):
            self.ui.state.current_word = action.word
        elif isinstance(action, ChatMessageAction):
            self.ui.state.chat_messages.append(action.message)

    @override
    def draw(self, surface):
        # Header
        pygame.draw.rect(
            surface, HEADER_COLOR, (0, 0, surface.get_width(), HEADER_HEIGHT)
        )
        Title.draw_title(
            surface, 125, HEADER_HEIGHT // 2, with_shadow=False, background=HEADER_COLOR
        )

        while not self.ui.state.pending_draw_lines.empty():
            draw_action: DrawAction = self.ui.state.pending_draw_lines.get()
            self._draw_smooth_line(self.canvas.surface, draw_action)

        if self.ui.state.ready_to_draw():
            self.toolbar.draw(surface)
        self.canvas.draw(surface)
        self.playersList.draw(self.ui.state, surface)
        self.word_display.draw(self.ui.state, surface)
        self.chat.draw(surface)

        if self.popup:
            self.popup.draw(surface)

    def _on_draw(self, draw_action: DrawAction):
        self.on_action(draw_action)
        self.ui.client.send_action_to_server(draw_action)

    def _on_clear(self):
        self.canvas.clear_canvas()
        self.ui.client.send_action_to_server(ClearCanvasAction(), immediate=True)

    def _on_pick_word(self, word: str):
        self.ui.state.current_word = word
        self.ui.client.send_action_to_server(UpdateWordAction(word), immediate=True)
        self.popup = None

    def _on_chat_enter(self, text: str):
        message = ChatMessage(self.ui.state.me().name, text, BLACK)
        self.ui.client.send_action_to_server(ChatMessageAction(message), immediate=True)

    def _draw_smooth_line(self, surf: pygame.surface, draw_action: DrawAction):
        distance = int(draw_action.start.distance_to(draw_action.end))

        if distance == 0:
            pygame.draw.circle(
                surf,
                draw_action.color,
                (int(draw_action.start.x), int(draw_action.start.y)),
                draw_action.brush_size,
            )
        else:
            for i in range(distance):
                point = draw_action.start.lerp(draw_action.end, i / distance)
                pygame.draw.circle(
                    surf,
                    draw_action.color,
                    (int(point.x), int(point.y)),
                    draw_action.brush_size,
                )
