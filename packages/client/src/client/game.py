import pygame
from client.client_socket import ClientSocket
from client.drawing_surface import DrawingSurface
from client.game_state import GameState
from shared.action import Action
from shared.draw_action import DrawAction

WIDTH, HEIGHT = 1000, 800
DRAWING_AREA_WIDTH, DRAWING_AREA_HEIGHT = 700, 500
DRAWING_AREA_X = 20
DRAWING_AREA_Y = 80


class Game:
    def __init__(self):
        self.state = GameState()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.drawing_surface = DrawingSurface(
            DRAWING_AREA_X, DRAWING_AREA_Y, DRAWING_AREA_WIDTH, DRAWING_AREA_HEIGHT
        )
        pygame.event.set_allowed(
            [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]
        )
        pygame.event.poll()
        self.client = ClientSocket(self.update)

    def handle_events(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.QUIT:
                self.state.running = False
                self.client.close_client()
                return None

            elif event.type in (
                pygame.MOUSEBUTTONDOWN,
                pygame.MOUSEBUTTONUP,
                pygame.MOUSEMOTION,
            ):
                # Find the object under the mouse
                action = self.drawing_surface.handle_event(event)
                if action:
                    self.update(action)
                    self.client.send_action_to_server(action)

    def update(self, action: Action):
        if isinstance(action, DrawAction):
            self.state.pending_draw_lines.put_nowait(action)

    def draw(self):
        while not self.state.pending_draw_lines.empty():
            line: DrawAction = self.state.pending_draw_lines.get()
            pygame.draw.line(
                self.drawing_surface.surface,
                line.color,
                line.start_pos,
                line.end_pos,
                line.brush_size,
            )

        self.drawing_surface.draw(self.screen)
