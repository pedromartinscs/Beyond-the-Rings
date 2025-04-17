import pygame
import os
import math
import sys
from Core.Menu.button import Button

class VerticalPanel:
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.width = 200
        self.height = 350
        self.visible = False
        self.x = -self.width  # Start off-screen to the left
        self.y = (screen.get_height() - self.height) // 2 - 10  # Center vertically and move up 10 pixels
        self.speed = 10  # Animation speed
        self.target_x = self.x
        self.handle_width = 20  # Width of the visible handle when hidden
        self.is_animating = False
        self.glow_speed = 10  # Speed of the pulsating effect, matching the buttons
        self.min_alpha = 150  # Minimum alpha value
        self.max_alpha = 255  # Maximum alpha value
        self.next_action = None  # Add next_action for screen transitions

        # Initialize the mixer for playing sound effects
        pygame.mixer.init()

        # Load and scale the background image
        self.background_image = pygame.image.load(os.path.join('Images', 'game_menu_vertical.png'))
        self.background_image = pygame.transform.scale(self.background_image, (self.width, self.height))

        # Load handle images
        self.handle_open = pygame.image.load(os.path.join('Images', 'game_menu_vertical_handle_open.png'))
        self.handle_close = pygame.image.load(os.path.join('Images', 'game_menu_vertical_handle_close.png'))
        
        # Scale handle images to match height
        self.handle_open = pygame.transform.scale(self.handle_open, (self.handle_width, self.height))
        self.handle_close = pygame.transform.scale(self.handle_close, (self.handle_width, self.height))

        # Create the panel surface
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Create small font for the hint text
        self.hint_font = pygame.font.Font(None, 16)  # Small font size
        self.hint_text = "press esc to toggle"
        self.hint_surface = self.hint_font.render(self.hint_text, True, (150, 150, 150))  # Light gray color
        self.hint_rect = self.hint_surface.get_rect(centerx=self.width // 2, y=10)  # Position at the top

        # Load hover sound effect
        try:
            sound_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'Sounds', 'hover.wav')
            self.hover_sound = pygame.mixer.Sound(sound_path)
        except Exception as e:
            print("Error loading hover sound:", e)
        self.hovered_button = None  # Initialize to track hover state

        # Create buttons
        self.create_buttons()

        # Create cached surfaces
        self.create_cached_surfaces()

    def create_buttons(self):
        button_width = 180  # Slightly smaller than panel width
        button_height = 40
        button_spacing = 12  # Reduced from 15 to 14
        start_x = 10  # Offset from left edge of panel
        start_y = 25  # Offset from top of panel

        # Create buttons with their respective actions
        self.buttons = [
            Button(start_x, start_y, 0, button_spacing, button_width, button_height, 
                  "Main Menu", self.main_menu, "Images/menu_button.png", "Images/menu_button_glow.png"),
            Button(start_x, start_y, 1, button_spacing, button_width, button_height, 
                  "Save Game", self.save_game, "Images/menu_button.png", "Images/menu_button_glow.png"),
            Button(start_x, start_y, 2, button_spacing, button_width, button_height, 
                  "Load Game", self.load_game, "Images/menu_button.png", "Images/menu_button_glow.png"),
            Button(start_x, start_y, 3, button_spacing, button_width, button_height, 
                  "Options", self.options, "Images/menu_button.png", "Images/menu_button_glow.png"),
            Button(start_x, start_y, 4, button_spacing, button_width, button_height, 
                  "Surrender", self.surrender, "Images/menu_button.png", "Images/menu_button_glow.png"),
            Button(start_x, start_y, 5, button_spacing, button_width, button_height, 
                  "Quit Game", self.quit_game, "Images/menu_button.png", "Images/menu_button_glow.png")
        ]

        # Store original button positions
        self.button_original_positions = []
        for button in self.buttons:
            self.button_original_positions.append((button.rect.x, button.rect.y))

    def main_menu(self):
        print("Returning to Main Menu...")
        # Stop the game's music
        pygame.mixer.music.stop()
        from Core.Menu.main_menu import MainMenu
        return MainMenu(self.screen)  # Return the main menu screen to switch to it

    def save_game(self):
        print("Saving game...")
        # TODO: Implement save game functionality

    def load_game(self):
        print("Loading game...")
        # TODO: Implement load game functionality

    def surrender(self):
        print("Surrendering...")
        # TODO: Implement surrender functionality

    def quit_game(self):
        print("Quitting game...")
        pygame.quit()
        sys.exit()

    def options(self):
        print("Opening Options...")
        # TODO: Implement options functionality

    def show(self):
        self.visible = True
        self.target_x = 0  # Show completely
        self.is_animating = True

    def hide(self):
        self.target_x = -self.width  # Hide completely
        self.is_animating = True

    def is_handle_clicked(self, pos):
        # Handle is always at the right of the panel
        handle_x = 0 if not self.visible else self.x + self.width
        handle_rect = pygame.Rect(handle_x, self.y, self.handle_width, self.height)
        return handle_rect.collidepoint(pos)

    def is_panel_clicked(self, pos):
        if not self.visible:
            return False
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return panel_rect.collidepoint(pos)

    def handle_events(self, event):
        if not self.visible:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if any button is clicked
            for button in self.buttons:
                # Adjust button position relative to panel for click detection
                button_rect = pygame.Rect(
                    button.rect.x + self.x,
                    button.rect.y + self.y,
                    button.rect.width,
                    button.rect.height
                )
                if button_rect.collidepoint(event.pos) and button.action:
                    self.next_action = button.action  # Store the action instead of executing it immediately

        # Handle mouse hover and play sound
        if event.type == pygame.MOUSEMOTION:
            hovered_button = None
            for button in self.buttons:
                # Adjust button position relative to panel for hover detection
                button_rect = pygame.Rect(
                    button.rect.x + self.x,
                    button.rect.y + self.y,
                    button.rect.width,
                    button.rect.height
                )
                button.is_hovered = button_rect.collidepoint(event.pos)
                if button.is_hovered:
                    hovered_button = button

            # If the hovered button is different from the previous one, play the hover sound
            if hovered_button and hovered_button != self.hovered_button:
                self.hovered_button = hovered_button
                try:
                    self.hover_sound.play()  # Play the hover sound effect
                except Exception as e:
                    print("Error playing sound:", e)
            elif not hovered_button:  # Reset the hovered button when no button is hovered
                self.hovered_button = None

    def update(self):
        # Smooth animation
        if self.x < self.target_x:
            self.x = min(self.x + self.speed, self.target_x)
        elif self.x > self.target_x:
            self.x = max(self.x - self.speed, self.target_x)
        
        # Check if animation is complete
        if self.x == self.target_x:
            self.is_animating = False
            if self.x == -self.width:  # If fully hidden
                self.visible = False

        # Handle screen transitions
        if self.next_action:
            next_screen = self.next_action()  # Execute the stored action
            self.next_action = None
            if next_screen:
                return next_screen

    def create_cached_surfaces(self):
        """Create and cache the static parts of the panel"""
        # Create the base panel surface (background + static button parts)
        self.base_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.base_surface.blit(self.background_image, (0, 0))
        self.base_surface.blit(self.hint_surface, self.hint_rect)

        # Pre-render button states
        self.button_states = {}
        for button in self.buttons:
            # Cache normal state
            normal_surface = pygame.Surface((button.rect.width, button.rect.height), pygame.SRCALPHA)
            normal_surface.blit(button.image, (0, 0))
            button.render_text(normal_surface)  # Add text to normal state

            # Cache glow state
            glow_surface = pygame.Surface((button.rect.width, button.rect.height), pygame.SRCALPHA)
            glow_surface.blit(button.glow_image, (0, 0))  # First draw glow image
            glow_surface.blit(button.image, (0, 0))  # Then draw button image on top
            button.render_text(glow_surface)  # Finally draw text on top of everything

            self.button_states[button] = {
                'normal': normal_surface,
                'glow': glow_surface
            }

        # Cache handle states
        self.handle_open_cached = self.handle_open.copy()
        self.handle_close_cached = self.handle_close.copy()

        # Cache the panel rect for dirty rectangle rendering
        self.panel_rect = pygame.Rect(0, 0, self.width + self.handle_width, self.height)
        self.last_rect = None

    def render(self):
        # Always render the handle, regardless of panel visibility
        handle_x = 0 if not self.visible else self.x + self.width
        handle_image = self.handle_close_cached if self.visible else self.handle_open_cached
        self.screen.blit(handle_image, (handle_x, self.y))

        # Only render the panel if visible or animating
        if not (self.visible or self.is_animating):
            return

        # Calculate current rect for dirty rectangle rendering
        current_rect = self.panel_rect.copy()
        current_rect.x = self.x
        current_rect.y = self.y

        # Start with a clean copy of the base surface
        panel_surface = self.base_surface.copy()
        
        # Draw buttons with appropriate state
        for button in self.buttons:
            # Get button states
            states = self.button_states[button]
            rel_x, rel_y = button.rect.x, button.rect.y
            
            # Use pre-rendered states
            surface = states['glow'] if button.is_hovered else states['normal']
            panel_surface.blit(surface, (rel_x, rel_y))
        
        # Draw the panel
        self.screen.blit(panel_surface, (self.x, self.y))

        # Update dirty rectangles
        if self.last_rect:
            pygame.display.update(self.last_rect)
        pygame.display.update(current_rect)
        self.last_rect = current_rect 