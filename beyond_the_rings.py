import pygame
import sys
import os
from Core.game_context import GameContext


# Initialize Pygame
pygame.init()

def is_debug_mode():
    """Check if the game is running in debug mode"""
    # Check if a debugger is attached (will be True when running with debugger)
    return sys.gettrace() is not None

# Screen configuration
if is_debug_mode():
    # Windowed mode for debug
    screen = pygame.display.set_mode((1024, 768))
    pygame.display.set_caption("Beyond the Rings (Debug Mode)")
else:
    # Fullscreen for release
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Beyond the Rings")

game_context = GameContext(screen)

# Main game function
def main():
    running = True

    while running:
        game_context.handle_events()
        game_context.update()
        game_context.render()
        pygame.display.update()
        pygame.time.Clock().tick(60)  # Maintain 60 FPS

    pygame.quit()

if __name__ == "__main__":
    main()
