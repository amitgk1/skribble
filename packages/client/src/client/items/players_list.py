import pygame
from client.fonts import FONT_MD, FONT_SM
from client.game_state import GameState
from pygame_emojis import load_emoji
from shared.colors import BLACK, DARK_BLUE, DARK_GRAY, GOLD, LIGHT_GRAY, WHITE

DRAWING_EMOJI = load_emoji("✏️", FONT_MD.get_height())
YOU_EMOJI = load_emoji("👤", FONT_MD.get_height())


class PlayersList:
    def __init__(self, player_list_rect: pygame.Rect):
        self.player_list_rect = player_list_rect

    def draw(self, gameState: GameState, surface: pygame.Surface):
        """Draw the connected players list"""

        pygame.draw.rect(
            surface,
            "gray99",
            self.player_list_rect,
            border_radius=10,
        )

        # Draw header
        header_surf = FONT_MD.render("Players", True, BLACK)
        header_rect = header_surf.get_rect(
            center=(self.player_list_rect.centerx, self.player_list_rect.top + 30)
        )
        surface.blit(header_surf, header_rect)

        # Draw players
        if gameState.players_info:
            for i, player in enumerate(
                sorted(gameState.players_info, key=lambda p: p.score)
            ):
                player_rect = pygame.Rect(
                    self.player_list_rect.x + 10,
                    self.player_list_rect.y + 40 + i * 40,
                    self.player_list_rect.width - 20,
                    35,
                )

                # Highlight active player and yourself
                if player.is_player_turn:
                    pygame.draw.rect(surface, GOLD, player_rect, 0, 5)
                    emoji_surf = DRAWING_EMOJI
                elif player.id == gameState.my_player_id:
                    pygame.draw.rect(surface, LIGHT_GRAY, player_rect, 0, 5)
                    emoji_surf = YOU_EMOJI
                else:
                    pygame.draw.rect(surface, WHITE, player_rect, 0, 5)
                    emoji_surf = None

                pygame.draw.rect(surface, DARK_GRAY, player_rect, 1, 5)

                text_start = player_rect.x + 10

                # Player name
                name_surf = FONT_SM.render(
                    player.get_player_name(gameState.my_player_id), True, BLACK
                )
                surface.blit(
                    name_surf,
                    (
                        text_start,
                        player_rect.centery - name_surf.get_height() // 2,
                    ),
                )

                # Player score
                score_text = FONT_MD.render(f"{player.score} pts", True, DARK_BLUE)
                surface.blit(
                    score_text,
                    (
                        player_rect.right - score_text.get_width() - 10,
                        player_rect.centery - score_text.get_height() // 2,
                    ),
                )

                # Icon for active player or you
                if emoji_surf:
                    surface.blit(
                        emoji_surf,
                        (
                            text_start + name_surf.get_width() + 5,
                            player_rect.centery - emoji_surf.get_height() // 2,
                        ),
                    )
