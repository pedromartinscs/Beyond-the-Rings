import pygame
import sys

from ..Menu.button import Button

class CreditsScreen:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.next_action = None

        # Load background image based on screen width
        if self.screen_width <= 1024:
            self.background = pygame.image.load("Images/credits_background.jpg")
        else:
            self.background = pygame.image.load("Images/credits_background_x4.jpg")

        # Create the back button
        self.back_button = Button(
            x=(self.screen_width - 200) // 2, 
            y=self.screen_height - 200, 
            number=1, 
            spacing=20, 
            width=200, 
            height=50, 
            text="Back", 
            action=self.go_back
        )

        # Load hover sound effect
        self.hover_sound = pygame.mixer.Sound("Sounds/hover.wav")  # Replace with your hover sound file
        self.hovered_button = None  # Initialize to track hover state

    def go_back(self):
        print("Going back to main menu...")
        # Code to switch to the main menu, you could return the new screen here (e.g., MainMenu)
        from Core.Menu.main_menu import MainMenu  # Import here to avoid circular imports
        return MainMenu(self.screen)  # Return the credits screen to switch to it

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
            new_height = int(screen_width / bg_ratio)
            background_scaled = pygame.transform.scale(self.background, (screen_width, new_height))
            y_offset = (screen_height - new_height) // 2
            self.screen.fill((0, 0, 0))  # Fill the screen with black (bars top and bottom)
            self.screen.blit(background_scaled, (0, y_offset))  # Draw image centered vertically
        else:  # If the screen is taller than the background image
            new_width = int(screen_height * bg_ratio)
            background_scaled = pygame.transform.scale(self.background, (new_width, screen_height))
            x_offset = (screen_width - new_width) // 2
            self.screen.fill((0, 0, 0))  # Fill the screen with black (bars left and right)
            self.screen.blit(background_scaled, (x_offset, 0))  # Draw image centered horizontally

    def handle_events(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Handle events for buttons (clicking)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.is_clicked():
                self.next_action = self.back_button.action

        # Handle mouse hover and play sound for the back button
        if event.type == pygame.MOUSEMOTION:
            # Check if the mouse is hovering over the back button
            if self.back_button.rect.collidepoint(event.pos):
                if self.hovered_button != self.back_button:
                    self.hovered_button = self.back_button
                    self.hover_sound.play()  # Play the hover sound effect
            else:
                # If no button is being hovered, reset hovered_button
                self.hovered_button = None

    def update(self):
        if self.next_action:
            next_screen = self.next_action()  # Executes button action and checks if it returns a screen
            self.next_action = None
            if next_screen:
                return next_screen

    def render(self):
        self.draw_background()

        # Draw the back button
        self.back_button.draw(self.screen)
