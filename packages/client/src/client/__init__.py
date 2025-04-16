import pygame
from client.game import Game

# Initialize pygame
pygame.init()

clock = pygame.time.Clock()


# Main game loop
def main():
    game = Game()

    while game.state.running:
        # Handle events
        events = pygame.event.get()
        game.handle_events(events)

        # Draw the game
        game.draw()

        # Update the display
        pygame.display.flip()

        # Cap the framerate
        clock.tick(60)


if __name__ == "__main__":
    main()
    pygame.quit()
    pygame.quit()
