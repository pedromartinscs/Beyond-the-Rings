import pygame
from Core.Menu.main_menu import MainMenu


class GameContext:
    def __init__(self, screen):
        self.screen = screen
        self.current_state_screen = MainMenu(screen)

    def handle_events(self, event):
        self.current_state_screen.handle_events(event)

    def update(self):
        next_screen = self.current_state_screen.update()
        if next_screen:
            self.current_state_screen = next_screen

    def render(self):
        self.current_state_screen.render()