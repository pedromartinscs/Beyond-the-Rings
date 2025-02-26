import pygame
from Core.game_context import GameContext


# Initialize Pygame
pygame.init()

# Screen configuration
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
game_context = GameContext(screen)
pygame.display.set_caption("Beyond the Rings")

# Main game function
def main():
    running = True

    while running:
        game_context.handle_events()
        game_context.update()
        game_context.render()
        pygame.display.flip()
        pygame.time.Clock().tick(60)  # Maintain 60 FPS

    pygame.quit()

if __name__ == "__main__":
    main()
