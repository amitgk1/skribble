from typing import TYPE_CHECKING, override

import pygame
from shared.actions import Action
from shared.actions.draw_action import DrawAction

from client.items.players_list import PlayersList
from client.items.title import Title
from client.window import Window

if TYPE_CHECKING:
    from client import UserInterface

from client.canvas import Canvas

DRAWING_AREA_WIDTH, DRAWING_AREA_HEIGHT = 700, 500
DRAWING_AREA_X = 20
DRAWING_AREA_Y = 100

HEADER_COLOR = (70, 130, 180)
HEADER_HEIGHT = 80


class Game(Window):
    def __init__(self, ui: "UserInterface"):
        self.ui = ui
        self.canvas = Canvas(
            self.ui.screen.get_width() // 2 - DRAWING_AREA_WIDTH // 2,
            HEADER_HEIGHT + 10,
            DRAWING_AREA_WIDTH,
            DRAWING_AREA_HEIGHT,
            on_draw=self._on_draw,
        )
        self.playersList = PlayersList(
            pygame.Rect(
                0,
                HEADER_HEIGHT + 10,
                self.ui.screen.get_width() // 2 - DRAWING_AREA_WIDTH // 2 - 5,
                self.ui.screen.get_height() // 2 - DRAWING_AREA_HEIGHT // 2,
            )
        )
        # TODO: pygame.event.set_allowed(
        #     [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]
        # )

    def _on_draw(self, draw_action: DrawAction):
        self.on_action(draw_action)
        self.ui.client.send_action_to_server(draw_action)

    @override
    def handle_event(self, event):
        self.canvas.handle_event(event)

    @override
    def on_action(self, action: Action):
        if isinstance(action, DrawAction):
            self.ui.state.pending_draw_lines.put(action)

    @override
    def draw(self, surface):
        # Header
        pygame.draw.rect(
            surface, HEADER_COLOR, (0, 0, surface.get_width(), HEADER_HEIGHT)
        )
        Title.draw_title(
            surface, 150, HEADER_HEIGHT // 2, with_shadow=False, background=HEADER_COLOR
        )

        while not self.ui.state.pending_draw_lines.empty():
            draw_action: DrawAction = self.ui.state.pending_draw_lines.get()
            self._draw_smooth_line(self.canvas.surface, draw_action)

        self.canvas.draw(surface)
        self.playersList.draw(self.ui.state, surface)

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
