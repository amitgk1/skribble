from itertools import groupby
from typing import TYPE_CHECKING, Callable, override

import pygame
from shared.actions import Action
from shared.actions.chat_message_action import ChatMessageAction
from shared.actions.choose_word_action import ChooseWordAction
from shared.actions.clear_canvas_action import ClearCanvasAction
from shared.actions.draw_action import DrawAction
from shared.actions.game_over_action import GameOverAction
from shared.actions.turn_end_action import TurnEndAction
from shared.actions.turn_start_action import TurnStartAction
from shared.actions.work_picked_action import WordPickedAction
from shared.chat_message import ChatMessage
from shared.colors import BLACK, DARK_GRAY, LIGHT_GRAY, WHITE, RED

from client.fonts import FONT_LG, FONT_MD, FONT_TITLE
from client.game_state import GameState
from client.items.bubble import Bubble
from client.items.button import Button
from client.items.chat import Chat
from client.items.players_list import PlayersList
from client.items.popup import Popup
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
            if word_text.get_height() > self.rect.height:
                word_text = pygame.transform.smoothscale(word_text, (word_text.get_width(), self.rect.height))
            if word_text.get_width() > self.rect.width:
                word_text = pygame.transform.smoothscale(word_text, (self.rect.width, word_text.get_height()))

        if word_text:
            surface.blit(
                word_text,
                word_text.get_rect(center=self.rect.center)
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


class Timer:
    TIMER_EVENT = pygame.event.custom_type()

    def __init__(self, rect: pygame.Rect):
        self.image = pygame.transform.scale(
            pygame.image.load("assets/clock.gif"), rect.size
        )
        self.rect = rect
        self.current_time = 0

    def start_timer(self, timeout: int):
        self.current_time = timeout
        pygame.time.set_timer(Timer.TIMER_EVENT, 1000, timeout)

    def stop_timer(self):
        pygame.time.set_timer(Timer.TIMER_EVENT, 0)
        self.current_time = 0

    def handle_event(self, event: pygame.event.Event):
        if event.type == Timer.TIMER_EVENT:
            self.current_time -= 1

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.image.get_rect(center=self.rect.center))
        time_text = FONT_MD.render(str(self.current_time), True, BLACK)
        time_rect = time_text.get_rect(
            center=(self.rect.centerx, self.rect.centery + 5)
        )
        surface.blit(time_text, time_rect)


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
        self.timer = Timer(pygame.Rect(self.word_display.rect.right + 50, 10, 65, 60))
        self.popup = None
        self.bubbles = [Bubble(self.ui.screen.get_rect()) for _ in range(50)]

    @override
    def handle_event(self, event):
        if self.popup:
            self.popup.handle_event(event)
        else:
            self.timer.handle_event(event)
            if self.ui.state.ready_to_draw():
                self.canvas.handle_event(event)
                self.toolbar.handle_event(event)
        self.chat.handle_event(event)

    @override
    def update(self):
        if self.ui.state.ready_to_draw():
            self.canvas.update()
            self.toolbar.update()
        self.chat.update()
        if self.ui.state.am_i_a_winner():
            for bubble in self.bubbles:
                bubble.update()

    @override
    def on_action(self, action: Action):
        if isinstance(action, DrawAction):
            self.ui.state.pending_draw_lines.put(action)
        elif isinstance(action, ClearCanvasAction):
            self.canvas.clear_canvas()
        elif isinstance(action, ChooseWordAction):
            self.popup = PickWordPopUp(
                self.canvas.surface.get_rect(topleft=(self.canvas.x, self.canvas.y)),
                action.options,
                self._on_pick_word,
            )
        elif isinstance(action, TurnStartAction):
            self.popup = None
            self.ui.state.round = action.round
            self.ui.state.current_word = action.word
            self.timer.start_timer(action.time)
        elif isinstance(action, TurnEndAction):
            self.timer.stop_timer()
            self.popup = Popup(
                action.reason,
                [
                    f"word was {action.word}",
                    *[
                        f"{self.ui.state.get_player_by_id(id).get_player_name(self.ui.state.my_player_id)} gained {score} points"
                        for id, score in action.player_score_update.items()
                    ],
                ],
                self.canvas.surface.get_rect(topleft=(self.canvas.x, self.canvas.y)),
                closable=False,
            )
            self.ui.state.current_word = None
            self.canvas.clear_canvas()
        elif isinstance(action, GameOverAction):
            self.ui.state.current_word = "game over!"
            for p in self.ui.state.players_info:
                p.is_player_turn = False

            # dealing with multiple winners using groupby
            score, players = next(
                groupby(self.ui.state.players_info, key=lambda p: p.score)
            )
            self.ui.state.winners = list(players)
            self.popup = Popup(
                "Game Over!",
                [
                    "And the winner(s) are:",
                    *[
                        p.get_player_name(self.ui.state.my_player_id)
                        for p in self.ui.state.winners
                    ],
                    f"with {score} points!",
                ],
                self.canvas.surface.get_rect(topleft=(self.canvas.x, self.canvas.y)),
                closable=False,
            )

        elif isinstance(action, ChatMessageAction):
            self.ui.state.chat_messages.append(action.message)

    @override
    def draw(self, surface):
        # Header
        pygame.draw.rect(
            surface, HEADER_COLOR, (0, 0, surface.get_width(), HEADER_HEIGHT)
        )
        Title.draw_title(
            surface, 160, HEADER_HEIGHT - FONT_TITLE.get_height() // 2, with_shadow=False, background=HEADER_COLOR
        )
        rounds_title = FONT_LG.render(
            f"Round {self.ui.state.round}/{self.ui.state.max_rounds}", True, BLACK
        )
        surface.blit(
            rounds_title,
            (
                self.ui.screen.get_width() - rounds_title.get_width() - 10,
                HEADER_HEIGHT // 2 - rounds_title.get_height() // 2,
            ),
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
        self.timer.draw(surface)

        if self.popup:
            self.popup.draw(surface)

        if self.ui.state.am_i_a_winner():
            for bubble in self.bubbles:
                bubble.draw(surface)

    def _on_draw(self, draw_action: DrawAction):
        self.on_action(draw_action)
        self.ui.client.send_action_to_server(draw_action)

    def _on_clear(self):
        self.canvas.clear_canvas()
        self.ui.client.send_action_to_server(ClearCanvasAction(), immediate=True)

    def _on_pick_word(self, word: str):
        self.ui.client.send_action_to_server(WordPickedAction(word), immediate=True)
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
