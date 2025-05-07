import pygame
import sys
from Core.Credits.credits import CreditsScreen
from Core.Game.game import Game
from Core.UI.base_screen import BaseScreen
from ..UI.button import Button


# Define the main menu class
class MainMenu(BaseScreen):
    # region Constructor
    def __init__(self, screen):
        super().__init__(screen)
        self.screen_height = screen.get_height()
        self.screen_width = screen.get_width()
        self.buttons = []
        self.next_action = None
        self.create_buttons()
        self.panel_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)

        # Initialize the mixer for playing music and sound effects
        pygame.mixer.init()  # Initialize the pygame mixer
        self.music_file = "Music/672781__bertsz__cyberpunk_dump.flac"  # Path to the background music file
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load(self.music_file)  # Load the music
            pygame.mixer.music.play(-1, 6.0)  # Play the music in an infinite loop (-1 = loop forever)

        # Load background image based on screen width
        if self.screen_width <= 1024:
            self.background = pygame.image.load("Images/background_mainmenu.jpg")
        else:
            self.background = pygame.image.load("Images/background_mainmenu_x4.jpg")

        # Load hover sound effect
        self.hover_sound = pygame.mixer.Sound("Sounds/hover.wav")  # Replace with your hover sound file
        self.hovered_button = None  # Initialize hovered_button to track mouse hover

    # endregion

    # region Methods
    def create_buttons(self):
        # Create buttons for the menu
        button_width = 200
        button_height = 50
        button_spacing = 20  # Space between buttons
        start_x = (self.screen.get_width() - button_width) // 2
        start_y = (self.screen.get_height() - (button_height * 5 + button_spacing * 4)) // 5  # Adjust for 3 buttons

        self.buttons.append(Button(start_x, start_y, 1, button_spacing, button_width, button_height, "New Game", self.start_game, "Images/menu_button.png", "Images/menu_button_glow.png", glow_behind=True))
        self.buttons.append(Button(start_x, start_y, 2, button_spacing, button_width, button_height, "Load Game", self.options, "Images/menu_button.png", "Images/menu_button_glow.png", glow_behind=True))
        self.buttons.append(Button(start_x, start_y, 3, button_spacing, button_width, button_height, "Campaign", self.options, "Images/menu_button.png", "Images/menu_button_glow.png", glow_behind=True))
        self.buttons.append(Button(start_x, start_y, 4, button_spacing, button_width, button_height, "Options", self.options, "Images/menu_button.png", "Images/menu_button_glow.png", glow_behind=True))
        self.buttons.append(Button(start_x, start_y, 5, button_spacing, button_width, button_height, "Credits", self.credits, "Images/menu_button.png", "Images/menu_button_glow.png", glow_behind=True))
        self.buttons.append(Button(start_x, start_y, 6, button_spacing, button_width, button_height, "Exit", self.exit_game, "Images/menu_button.png", "Images/menu_button_glow.png", glow_behind=True))

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

    def start_game(self):
        print("Starting Game...")
        return Game(self.screen)  # Return the game screen to switch to it

    def options(self):
        print("Opening Options...")
        # Placeholder for the options menu
        pass

    def credits(self):
        print("Opening Credits...")
        return CreditsScreen(self.screen)  # Return the credits screen to switch to it

    def exit_game(self):
        print("Exiting Game...")
        pygame.quit()
        sys.exit()

    def handle_events(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        # First handle cursor state through base class
        super().handle_events(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Handle events for buttons (clicking)
            for button in self.buttons:
                if button.is_clicked() and button.action:
                    self.next_action = button.action

        # Handle mouse hover and play sound
        if event.type == pygame.MOUSEMOTION:
            hovered_button = None
            for button in self.buttons:
                if button.rect.collidepoint(event.pos):  # If the mouse is over the button
                    hovered_button = button
                    break

            # If the hovered button is different from the previous one, play the hover sound
            if hovered_button and hovered_button != self.hovered_button:
                self.hovered_button = hovered_button
                self.hover_sound.play()  # Play the hover sound effect
            elif not hovered_button:  # Reset the hovered button when no button is hovered
                self.hovered_button = None

    def update(self):
        if self.next_action:
            next_screen = self.next_action()  # Executes button action and checks if it returns a screen
            self.next_action = None
            if next_screen:
                return next_screen

    def render(self):
        # Draw the background
        self.draw_background()
        
        # Draw the buttons
        for button in self.buttons:
            button.draw(self.screen)
        
        # Update the display
        pygame.display.flip()

        # IMPORTANT: Call parent's render method to ensure cursor is rendered on top of everything
        # This is required because BaseScreen handles cursor rendering and we want the cursor
        # to always be visible on top of all menu elements
        super().render()
    # endregion
