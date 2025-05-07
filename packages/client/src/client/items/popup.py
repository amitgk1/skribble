import pygame
from client.colors import BLACK, DARK_GRAY, LIGHT_BLUE, WHITE
from client.fonts import FONT_LG, FONT_MD


class Popup:
    def __init__(self, title: str, lines: list[str], rect_bound: pygame.Rect):
        self.title = title
        self.lines = lines
        self.rect_bound = rect_bound
        popup_width, popup_height = 400, 300
        self.popup_rect = pygame.Rect(
            self.rect_bound.width // 2 - popup_width // 2,
            self.rect_bound.height // 2 - popup_height // 2,
            popup_width,
            popup_height,
        )
        self.close_surf = FONT_MD.render("X", True, BLACK)
        self.close_rect = self.close_surf.get_rect(
            topright=(self.popup_rect.right - 20, self.popup_rect.top + 20)
        )

    def draw(self, surface: pygame.Surface):
        """Draw a generic popup with title and content lines"""
        # Create semi-transparent overlay
        overlay = pygame.Surface(
            (self.rect_bound.width, self.rect_bound.height), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        # Shadow
        shadow_rect = self.popup_rect.copy()
        shadow_rect.x += 5
        shadow_rect.y += 5
        pygame.draw.rect(surface, DARK_GRAY, shadow_rect, border_radius=15)

        # Main popup
        pygame.draw.rect(surface, WHITE, self.popup_rect, border_radius=15)
        pygame.draw.rect(surface, BLACK, self.popup_rect, 2, border_radius=15)

        # Title
        title_surf = FONT_LG.render(self.title, True, BLACK)
        title_rect = title_surf.get_rect(
            center=(self.popup_rect.centerx, self.popup_rect.top + 40)
        )
        surface.blit(title_surf, title_rect)

        # Horizontal line
        pygame.draw.line(
            surface,
            DARK_GRAY,
            (self.popup_rect.left + 30, self.popup_rect.top + 80),
            (self.popup_rect.right - 30, self.popup_rect.top + 80),
            2,
        )

        # Content lines
        for i, line in enumerate(self.lines):
            line_surf = FONT_MD.render(line, True, BLACK)
            line_rect = line_surf.get_rect(
                left=self.popup_rect.left + 50, top=self.popup_rect.top + 120 + i * 30
            )
            surface.blit(line_surf, line_rect)

        # Close button (X)
        pygame.draw.circle(surface, LIGHT_BLUE, self.close_rect.center, 15)
        pygame.draw.circle(surface, BLACK, self.close_rect.center, 15, 1)
        surface.blit(self.close_surf, self.close_rect)
