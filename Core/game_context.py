import pygame
from Core.Menu.main_menu import MainMenu


class GameContext:
    def __init__(self, screen):
        self.screen = screen
        self.current_state_screen = None
        self.set_state_screen(MainMenu(screen))

    def set_state_screen(self, state_screen):
        self.current_state_screen = state_screen

    def handle_events(self):
        for event in pygame.event.get():
            self.current_state_screen.handle_events(event)
            
    def update(self):
        next_screen = self.current_state_screen.update()
        if next_screen:  # If there's a next screen, set it
            self.set_state_screen(next_screen)

    def render(self):
        self.current_state_screen.render()