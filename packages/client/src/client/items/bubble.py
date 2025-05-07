import math
import random

import pygame
from client.colors import GREEN, LIGHT_BLUE, ORANGE, PINK, PURPLE, WHITE, YELLOW


class Bubble:
    """Decorative floating bubbles for the background"""

    def __init__(self, rect_bound: pygame.Rect):
        self.rect_bound = rect_bound
        self.radius = random.randint(5, 25)
        self.x = random.randint(0, self.rect_bound.width)
        self.y = random.randint(0, self.rect_bound.height)
        self.speed = random.uniform(0.2, 1.5)
        self.color = random.choice([LIGHT_BLUE, YELLOW, PINK, PURPLE, GREEN, ORANGE])
        self.alpha = random.randint(40, 180)
        self.direction = random.uniform(-0.5, 0.5)

    def update(self):
        self.y -= self.speed
        self.x += self.direction

        # Reset when off screen
        if self.y < -self.radius * 2:
            self.y = self.rect_bound.height + self.radius
            self.x = random.randint(0, self.rect_bound.width)

    def draw(self, surface: pygame.Surface):
        # Create a surface for the circle with alpha
        bubble_surface = pygame.Surface(
            (self.radius * 2, self.radius * 2), pygame.SRCALPHA
        )
        pygame.draw.circle(
            bubble_surface,
            (*self.color, self.alpha),
            (self.radius, self.radius),
            self.radius,
        )
        # Add a slight highlight effect
        pygame.draw.circle(
            bubble_surface,
            (*WHITE, min(255, self.alpha + 40)),
            (self.radius + 1, self.radius + 1),
            self.radius,
            width=math.floor(0.1 * self.radius),
            draw_bottom_right=True,
        )
        surface.blit(bubble_surface, (self.x - self.radius, self.y - self.radius))
