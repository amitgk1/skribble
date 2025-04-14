import pygame

# Initialize pygame
pygame.init()


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
