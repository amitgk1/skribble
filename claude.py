import random
import time
from collections import deque

import pygame
import pygame.freetype

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1000, 600
DRAWING_AREA_WIDTH, DRAWING_AREA_HEIGHT = 700, 500
DRAWING_AREA_LEFT = 20
DRAWING_AREA_TOP = 80
SIDEBAR_LEFT = DRAWING_AREA_LEFT + DRAWING_AREA_WIDTH + 20
SIDEBAR_WIDTH = WIDTH - SIDEBAR_LEFT - 20
SIDEBAR_HEIGHT = HEIGHT - 100
CHAT_HEIGHT = 300
PLAYERS_HEIGHT = 200
WORD_DISPLAY_TOP = 20
TOOLBAR_HEIGHT = 40
TOOLBAR_TOP = DRAWING_AREA_TOP + DRAWING_AREA_HEIGHT + 10
COLOR_PALETTE = [
    (0, 0, 0),  # Black
    (255, 255, 255),  # White
    (128, 128, 128),  # Gray
    (255, 0, 0),  # Red
    (0, 255, 0),  # Green
    (0, 0, 255),  # Blue
    (255, 255, 0),  # Yellow
    (255, 0, 255),  # Pink
    (0, 255, 255),  # Cyan
    (165, 42, 42),  # Brown
    (255, 165, 0),  # Orange
    (128, 0, 128),  # Purple
]
BRUSH_SIZES = [2, 5, 10, 15, 20]
WORDS = [
    "apple",
    "banana",
    "car",
    "dog",
    "elephant",
    "flower",
    "guitar",
    "house",
    "igloo",
    "jacket",
    "kite",
    "lemon",
    "mountain",
    "notebook",
    "ocean",
    "pizza",
    "queen",
    "rainbow",
    "sun",
    "tree",
    "umbrella",
    "violin",
    "watermelon",
    "xylophone",
    "yacht",
    "zebra",
]

# Set up the window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Skribbl.io Clone")
clock = pygame.time.Clock()

# Fonts
font_small = pygame.freetype.SysFont("Arial", 14)
font_medium = pygame.freetype.SysFont("Arial", 20)
font_large = pygame.freetype.SysFont("Arial", 28)


class Player:
    def __init__(
        self,
        name,
        color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
    ):
        self.name = name
        self.score = 0
        self.color = color
        self.is_drawing = False
        self.guessed_correctly = False

    def add_score(self, points):
        self.score += points


class DrawAction:
    def __init__(self, start_pos, end_pos, color, brush_size):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.color = color
        self.brush_size = brush_size


class Game:
    def __init__(self):
        # Game state
        self.state = "lobby"  # "lobby", "playing", "end_round", "end_game"
        self.round = 0
        self.total_rounds = 3
        self.players = [Player("You", (0, 128, 255))]
        self.current_player_index = 0
        self.current_word = ""
        self.displayed_word = ""
        self.word_hints_revealed = 0
        self.round_time = 60  # seconds
        self.round_start_time = 0
        self.chat_messages = deque(maxlen=10)

        # Drawing state
        self.drawing_surface = pygame.Surface((DRAWING_AREA_WIDTH, DRAWING_AREA_HEIGHT))
        self.drawing_surface.fill((255, 255, 255))
        self.is_drawing = False
        self.last_pos = None
        self.selected_color = COLOR_PALETTE[0]
        self.selected_brush_size = BRUSH_SIZES[1]
        self.drawing_enabled = False
        self.pending_draw_actions = []  # Store drawing actions to apply during update

        # Game controls
        self.can_clear = True
        self.is_eraser = False
        self.should_clear_canvas = False
        self.guess_input = ""

        # Start the game
        self.start_game()

    def start_game(self):
        self.state = "playing"
        self.round = 1
        self.players[0].is_drawing = True  # Player is drawing
        self.current_player_index = 0
        self.select_word()
        self.round_start_time = time.time()
        self.drawing_enabled = True  # Enable drawing
        self.add_system_message("Game started! You are drawing.")
        self.add_system_message(f"Your word is: {self.current_word}")

    def select_word(self):
        self.current_word = random.choice(WORDS)
        self.displayed_word = (
            self.current_word
        )  # Display the full word since we have only one player
        self.word_hints_revealed = 0

    def next_round(self):
        if self.round < self.total_rounds:
            self.round += 1
            # Reset player states
            for player in self.players:
                player.is_drawing = False
                player.guessed_correctly = False

            # Player draws again
            self.players[0].is_drawing = True

            # Clear the drawing area
            self.should_clear_canvas = True

            # Select a new word
            self.select_word()

            # Reset round timer
            self.round_start_time = time.time()

            # Enable drawing
            self.drawing_enabled = True

            # Add messages
            self.add_system_message(f"Round {self.round} started!")
            self.add_system_message(f"Your word is: {self.current_word}")
        else:
            self.end_game()

    def end_game(self):
        self.state = "end_game"
        self.add_system_message("Game over!")
        self.add_system_message(f"Final score: {self.players[0].score} points!")

    def add_system_message(self, message):
        self.chat_messages.append(("SYSTEM", message))

    def add_player_message(self, player_name, message):
        self.chat_messages.append((player_name, message))

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_pos = event.pos

                    # Check if clicking in the drawing area
                    if (
                        DRAWING_AREA_LEFT
                        <= mouse_pos[0]
                        <= DRAWING_AREA_LEFT + DRAWING_AREA_WIDTH
                        and DRAWING_AREA_TOP
                        <= mouse_pos[1]
                        <= DRAWING_AREA_TOP + DRAWING_AREA_HEIGHT
                        and self.drawing_enabled
                    ):
                        self.is_drawing = True
                        self.last_pos = (
                            mouse_pos[0] - DRAWING_AREA_LEFT,
                            mouse_pos[1] - DRAWING_AREA_TOP,
                        )

                    # Check if clicking on color palette
                    elif TOOLBAR_TOP <= mouse_pos[1] <= TOOLBAR_TOP + TOOLBAR_HEIGHT:
                        col_width = min(30, (WIDTH - 200) // len(COLOR_PALETTE))
                        for i, color in enumerate(COLOR_PALETTE):
                            if (
                                DRAWING_AREA_LEFT + i * col_width
                                <= mouse_pos[0]
                                <= DRAWING_AREA_LEFT + (i + 1) * col_width
                            ):
                                self.selected_color = color
                                self.is_eraser = False

                    # Check if clicking on brush sizes
                    brush_area_left = DRAWING_AREA_LEFT + len(COLOR_PALETTE) * 30 + 20
                    if (
                        brush_area_left <= mouse_pos[0] <= brush_area_left + 150
                        and TOOLBAR_TOP <= mouse_pos[1] <= TOOLBAR_TOP + TOOLBAR_HEIGHT
                    ):
                        for i, size in enumerate(BRUSH_SIZES):
                            if (
                                brush_area_left + i * 30
                                <= mouse_pos[0]
                                <= brush_area_left + (i + 1) * 30
                            ):
                                self.selected_brush_size = size

                    # Check if clicking on eraser button
                    eraser_left = brush_area_left + 160
                    if (
                        eraser_left <= mouse_pos[0] <= eraser_left + 80
                        and TOOLBAR_TOP <= mouse_pos[1] <= TOOLBAR_TOP + TOOLBAR_HEIGHT
                    ):
                        self.is_eraser = not self.is_eraser

                    # Check if clicking on clear button
                    clear_left = eraser_left + 90
                    if (
                        clear_left <= mouse_pos[0] <= clear_left + 80
                        and TOOLBAR_TOP <= mouse_pos[1] <= TOOLBAR_TOP + TOOLBAR_HEIGHT
                        and self.can_clear
                        and self.drawing_enabled
                    ):
                        self.should_clear_canvas = True

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    self.is_drawing = False
                    self.last_pos = None

            elif event.type == pygame.MOUSEMOTION:
                if self.is_drawing and self.drawing_enabled:
                    mouse_pos = pygame.mouse.get_pos()
                    # Check if within drawing area
                    if (
                        DRAWING_AREA_LEFT
                        <= mouse_pos[0]
                        <= DRAWING_AREA_LEFT + DRAWING_AREA_WIDTH
                        and DRAWING_AREA_TOP
                        <= mouse_pos[1]
                        <= DRAWING_AREA_TOP + DRAWING_AREA_HEIGHT
                    ):
                        current_pos = (
                            mouse_pos[0] - DRAWING_AREA_LEFT,
                            mouse_pos[1] - DRAWING_AREA_TOP,
                        )
                        if self.last_pos:
                            color = (
                                (255, 255, 255)
                                if self.is_eraser
                                else self.selected_color
                            )
                            # Instead of drawing directly, add a draw action to the list
                            self.pending_draw_actions.append(
                                DrawAction(
                                    self.last_pos,
                                    current_pos,
                                    color,
                                    self.selected_brush_size,
                                )
                            )
                        self.last_pos = current_pos
                    else:
                        self.last_pos = None

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.guess_input.strip():
                        self.add_player_message("You", self.guess_input)
                        self.guess_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    self.guess_input = self.guess_input[:-1]
                else:
                    if len(self.guess_input) < 20:  # Limit input length
                        self.guess_input += event.unicode

        return True

    def update(self):
        # Apply all pending draw actions to the drawing surface
        for action in self.pending_draw_actions:
            pygame.draw.line(
                self.drawing_surface,
                action.color,
                action.start_pos,
                action.end_pos,
                action.brush_size,
            )
        # Clear the pending actions after they've been applied
        self.pending_draw_actions = []

        # Clear the canvas if requested
        if self.should_clear_canvas:
            self.drawing_surface.fill((255, 255, 255))
            self.should_clear_canvas = False

        # Calculate remaining time
        elapsed_time = time.time() - self.round_start_time
        remaining_time = max(0, self.round_time - elapsed_time)

        # Check if round has ended
        if remaining_time <= 0 and self.state == "playing":
            # End of round
            self.add_system_message(f"Round {self.round} ended!")
            self.state = "end_round"
            self.round_transition_time = time.time()

        # Start next round after a short delay
        if self.state == "end_round" and time.time() - self.round_transition_time >= 3:
            self.next_round()
            self.state = "playing"

    def draw(self, screen):
        # Clear the screen
        screen.fill((240, 240, 240))

        # Draw the main drawing area background
        pygame.draw.rect(
            screen,
            (255, 255, 255),
            (
                DRAWING_AREA_LEFT,
                DRAWING_AREA_TOP,
                DRAWING_AREA_WIDTH,
                DRAWING_AREA_HEIGHT,
            ),
        )
        pygame.draw.rect(
            screen,
            (0, 0, 0),
            (
                DRAWING_AREA_LEFT,
                DRAWING_AREA_TOP,
                DRAWING_AREA_WIDTH,
                DRAWING_AREA_HEIGHT,
            ),
            2,
        )

        # Draw the current drawing
        screen.blit(self.drawing_surface, (DRAWING_AREA_LEFT, DRAWING_AREA_TOP))

        # Draw the word display area
        pygame.draw.rect(
            screen,
            (220, 220, 220),
            (DRAWING_AREA_LEFT, WORD_DISPLAY_TOP, DRAWING_AREA_WIDTH, 40),
        )

        # Draw the word
        word_text = self.current_word

        font_large.render_to(
            screen,
            (
                DRAWING_AREA_LEFT + DRAWING_AREA_WIDTH // 2 - len(word_text) * 7,
                WORD_DISPLAY_TOP + 10,
            ),
            word_text,
            (0, 0, 0),
        )

        # Draw round info
        round_text = f"Round {self.round}/{self.total_rounds}"
        font_medium.render_to(
            screen, (WIDTH - 150, WORD_DISPLAY_TOP + 10), round_text, (0, 0, 0)
        )

        # Draw timer
        elapsed_time = time.time() - self.round_start_time
        remaining_time = max(0, self.round_time - elapsed_time)
        timer_text = f"Time: {int(remaining_time)}s"
        font_medium.render_to(
            screen, (WIDTH - 300, WORD_DISPLAY_TOP + 10), timer_text, (0, 0, 0)
        )

        # Draw toolbar
        pygame.draw.rect(
            screen,
            (200, 200, 200),
            (DRAWING_AREA_LEFT, TOOLBAR_TOP, DRAWING_AREA_WIDTH, TOOLBAR_HEIGHT),
        )

        # Draw color palette
        col_width = min(30, (WIDTH - 200) // len(COLOR_PALETTE))
        for i, color in enumerate(COLOR_PALETTE):
            pygame.draw.rect(
                screen,
                color,
                (
                    DRAWING_AREA_LEFT + i * col_width,
                    TOOLBAR_TOP + 5,
                    col_width - 2,
                    TOOLBAR_HEIGHT - 10,
                ),
            )
            # Highlight selected color
            if color == self.selected_color and not self.is_eraser:
                pygame.draw.rect(
                    screen,
                    (255, 255, 255),
                    (
                        DRAWING_AREA_LEFT + i * col_width - 2,
                        TOOLBAR_TOP + 3,
                        col_width + 2,
                        TOOLBAR_HEIGHT - 6,
                    ),
                    2,
                )

        # Draw brush sizes
        brush_area_left = DRAWING_AREA_LEFT + len(COLOR_PALETTE) * col_width + 20
        for i, size in enumerate(BRUSH_SIZES):
            center_x = brush_area_left + i * 30 + 15
            center_y = TOOLBAR_TOP + TOOLBAR_HEIGHT // 2
            pygame.draw.circle(screen, (0, 0, 0), (center_x, center_y), size // 2)
            # Highlight selected brush size
            if size == self.selected_brush_size:
                pygame.draw.circle(
                    screen, (255, 0, 0), (center_x, center_y), size // 2 + 2, 2
                )

        # Draw eraser button
        eraser_left = brush_area_left + 160
        pygame.draw.rect(
            screen,
            (220, 220, 220) if self.is_eraser else (200, 200, 200),
            (eraser_left, TOOLBAR_TOP + 5, 80, TOOLBAR_HEIGHT - 10),
        )
        font_small.render_to(
            screen, (eraser_left + 15, TOOLBAR_TOP + 12), "Eraser", (0, 0, 0)
        )

        # Draw clear button
        clear_left = eraser_left + 90
        clear_color = (200, 200, 200) if self.drawing_enabled else (150, 150, 150)
        pygame.draw.rect(
            screen, clear_color, (clear_left, TOOLBAR_TOP + 5, 80, TOOLBAR_HEIGHT - 10)
        )
        font_small.render_to(
            screen, (clear_left + 20, TOOLBAR_TOP + 12), "Clear", (0, 0, 0)
        )

        # Draw sidebar
        pygame.draw.rect(
            screen,
            (220, 220, 220),
            (SIDEBAR_LEFT, DRAWING_AREA_TOP, SIDEBAR_WIDTH, SIDEBAR_HEIGHT),
        )

        # Draw players section
        pygame.draw.rect(
            screen,
            (240, 240, 240),
            (SIDEBAR_LEFT, DRAWING_AREA_TOP, SIDEBAR_WIDTH, PLAYERS_HEIGHT),
        )
        font_medium.render_to(
            screen, (SIDEBAR_LEFT + 10, DRAWING_AREA_TOP + 10), "Player", (0, 0, 0)
        )

        # Draw player info
        player = self.players[0]
        y_pos = DRAWING_AREA_TOP + 40
        # Player background
        bg_color = (200, 255, 200) if player.is_drawing else (240, 240, 240)
        pygame.draw.rect(
            screen, bg_color, (SIDEBAR_LEFT + 5, y_pos, SIDEBAR_WIDTH - 10, 35)
        )

        # Player color indicator
        pygame.draw.circle(screen, player.color, (SIDEBAR_LEFT + 20, y_pos + 17), 8)

        # Player name
        font_small.render_to(
            screen, (SIDEBAR_LEFT + 35, y_pos + 10), player.name, (0, 0, 0)
        )

        # Player score
        font_small.render_to(
            screen,
            (SIDEBAR_LEFT + SIDEBAR_WIDTH - 50, y_pos + 10),
            f"{player.score}",
            (0, 0, 0),
        )

        # Draw chat section
        chat_top = DRAWING_AREA_TOP + PLAYERS_HEIGHT + 10
        pygame.draw.rect(
            screen,
            (255, 255, 255),
            (SIDEBAR_LEFT, chat_top, SIDEBAR_WIDTH, CHAT_HEIGHT),
        )
        font_medium.render_to(
            screen, (SIDEBAR_LEFT + 10, chat_top + 10), "Chat", (0, 0, 0)
        )

        # Draw chat messages
        for i, (sender, message) in enumerate(self.chat_messages):
            y_pos = chat_top + 40 + i * 20
            if sender == "SYSTEM":
                # System messages in gray
                font_small.render_to(
                    screen, (SIDEBAR_LEFT + 10, y_pos), message, (100, 100, 100)
                )
            else:
                # Player messages with their name
                font_small.render_to(
                    screen,
                    (SIDEBAR_LEFT + 10, y_pos),
                    f"{sender}: {message}",
                    (0, 0, 0),
                )

        # Draw chat input box
        input_top = chat_top + CHAT_HEIGHT + 10
        pygame.draw.rect(
            screen, (255, 255, 255), (SIDEBAR_LEFT, input_top, SIDEBAR_WIDTH, 30)
        )
        font_small.render_to(
            screen,
            (SIDEBAR_LEFT + 10, input_top + 7),
            f"Message: {self.guess_input}",
            (0, 0, 0),
        )

        # Draw game state messages
        if self.state == "end_game":
            # Display final score
            center_x, center_y = WIDTH // 2, HEIGHT // 2
            pygame.draw.rect(
                screen, (0, 0, 0, 180), (center_x - 200, center_y - 100, 400, 200)
            )
            font_large.render_to(
                screen, (center_x - 100, center_y - 70), "Game Over!", (255, 255, 255)
            )

            font_medium.render_to(
                screen,
                (center_x - 150, center_y - 20),
                f"Final score: {self.players[0].score} points",
                (255, 255, 255),
            )

            font_medium.render_to(
                screen,
                (center_x - 150, center_y + 120),
                "Press any key to restart",
                (255, 255, 255),
            )


# Main game loop
def main():
    game = Game()
    running = True

    while running:
        # Handle events
        events = pygame.event.get()
        running = game.handle_events(events)

        # Update game state
        game.update()

        # Draw the game
        game.draw(screen)

        # Update the display
        pygame.display.flip()

        # Cap the framerate
        clock.tick(60)


if __name__ == "__main__":
    main()
    pygame.quit()
