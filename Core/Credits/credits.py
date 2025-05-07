import pygame
from Core.UI.base_screen import BaseScreen
from Core.UI.button import Button

class CreditsScreen(BaseScreen):
    def __init__(self, screen):
        super().__init__(screen)
        self.screen_height = screen.get_height()
        self.screen_width = screen.get_width()
        self.panel_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)

        # Load background image based on screen width
        if self.screen_width <= 1024:
            self.background = pygame.image.load("Images/credits_background.jpg")
        else:
            self.background = pygame.image.load("Images/credits_background_x4.jpg")

        # Create back button
        button_width = 200
        button_height = 50
        start_x = (self.screen.get_width() - button_width) // 2
        start_y = self.screen.get_height() - button_height - 50  # 50 pixels from bottom

        self.back_button = Button(start_x, start_y, 1, 0, button_width, button_height, "Back", self.go_back, "Images/menu_button.png", "Images/menu_button_glow.png")

        # Load hover sound effect
        self.hover_sound = pygame.mixer.Sound("Sounds/hover.wav")
        self.hovered_button = None

    def go_back(self):
        from Core.Menu.main_menu import MainMenu
        return MainMenu(self.screen)

    def handle_events(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        # First handle cursor state through base class
        super().handle_events(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.is_clicked():
                self.next_action = self.go_back

        # Handle mouse hover and play sound
        if event.type == pygame.MOUSEMOTION:
            if self.back_button.rect.collidepoint(event.pos):
                if not self.hovered_button:
                    self.hovered_button = self.back_button
                    self.hover_sound.play()
            else:
                self.hovered_button = None

    def draw_background(self):
        # Get the screen dimensions
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        # Get the dimensions of the background image
        bg_width, bg_height = self.background.get_width(), self.background.get_height()

        # Calculate the aspect ratios
        screen_ratio = screen_width / screen_height
        bg_ratio = bg_width / bg_height

        # Scale the image based on the screen ratio
        if screen_ratio > bg_ratio:  # If the screen is wider than the background image
            # Scale image to fill the width, and add black bars on top and bottom
            new_height = int(screen_width / bg_ratio)
            background_scaled = pygame.transform.scale(self.background, (screen_width, new_height))
            # Calculate position to center the image vertically
            y_offset = (screen_height - new_height) // 2
            self.screen.fill((0, 0, 0))  # Fill the screen with black (bars top and bottom)
            self.screen.blit(background_scaled, (0, y_offset))  # Draw image centered vertically
        else:  # If the screen is taller than the background image
            # Scale image to fill the height, and add black bars on the sides
            new_width = int(screen_height * bg_ratio)
            background_scaled = pygame.transform.scale(self.background, (new_width, screen_height))
            # Calculate position to center the image horizontally
            x_offset = (screen_width - new_width) // 2
            self.screen.fill((0, 0, 0))  # Fill the screen with black (bars left and right)
            self.screen.blit(background_scaled, (x_offset, 0))  # Draw image centered horizontally

    def render(self):
        self.draw_background()
        self.back_button.draw(self.screen)
