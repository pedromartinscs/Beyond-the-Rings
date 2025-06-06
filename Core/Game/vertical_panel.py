import pygame
import os
import math
import sys
from Core.UI.button import Button
from Core.UI.cursor_manager import CursorManager
from config import VERTICAL_PANEL, COLORS, FONT_SIZES
from typing import List, Optional, Tuple, Dict, Any

class VerticalPanel:
    """
    A vertical panel that slides in from the right side of the screen.
    Contains buttons for various actions and can be toggled with a handle.
    """
    
    def __init__(self, screen: pygame.Surface, game: Any = None):
        """
        Initialize the vertical panel.
        
        Args:
            screen: The pygame surface to draw on
            game: Optional game instance for accessing game state
        """
        self.screen = screen
        self.game = game
        self.width = VERTICAL_PANEL['width']
        self.height = VERTICAL_PANEL['height']
        self.handle_width = VERTICAL_PANEL['handle_width']
        self.animation_speed = VERTICAL_PANEL['animation_speed']
        
        # Panel state
        self.is_open = False
        self.target_x = -self.width  # Start off-screen to the left
        self.current_x = -self.width  # Start off-screen to the left
        
        # Calculate vertical position to center the panel, but 20px higher
        screen_height = screen.get_height()
        self.y = ((screen_height - self.height) // 2) - 20  # Center vertically and move up 20px
        
        # Create panel surface
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.surface.fill((0, 0, 0, 0))
        
        # Create handle surface
        self.handle_surface = pygame.Surface((self.handle_width, self.height), pygame.SRCALPHA)
        self.handle_surface.fill((0, 0, 0, 0))
        
        # Create buttons
        self.buttons: List[Button] = []
        self._create_buttons()
        
        # Cursor manager for hover effects
        self.cursor_manager = CursorManager()
        
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

        # Create small font for the hint text
        self.hint_font = pygame.font.Font(None, 16)  # Small font size
        self.hint_text = "press esc to toggle"
        self.hint_surface = self.hint_font.render(self.hint_text, True, (200, 200, 200))  # Light gray color
        self.hint_rect = self.hint_surface.get_rect(centerx=self.width // 2, y=17)  # Increased from 15 to 17

        # Load hover sound effect
        try:
            sound_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'Sounds', 'hover.wav')
            self.hover_sound = pygame.mixer.Sound(sound_path)
        except Exception as e:
            print("Error loading hover sound:", e)
        self.hovered_button = None  # Initialize to track hover state

        # Create cached surfaces
        self.create_cached_surfaces()

    def _create_buttons(self) -> None:
        """Create and initialize the panel buttons."""
        button_config = VERTICAL_PANEL['button']
        x = button_config['start_x']
        y = button_config['start_y']
        
        # Default button images
        default_button = "Images/menu_button.png"
        default_button_hover = "Images/menu_button_glow.png"
        
        # Create menu buttons with proper actions
        self.buttons = [
            Button(x, y, 0, button_config['spacing'], button_config['width'], button_config['height'], 
                  "Main Menu", self.return_to_menu, default_button, default_button_hover, glow_behind=True),
            Button(x, y, 1, button_config['spacing'], button_config['width'], button_config['height'], 
                  "Options", self.show_options, default_button, default_button_hover, glow_behind=True),
            Button(x, y, 2, button_config['spacing'], button_config['width'], button_config['height'], 
                  "Quit Game", self.quit_game, default_button, default_button_hover, glow_behind=True)
        ]

    def return_to_menu(self) -> None:
        """Return to the main menu."""
        print("Returning to main menu...")  # Debug print
        if self.game:
            self.game.next_action = "main_menu"

    def show_options(self) -> None:
        """Show the options menu."""
        print("Showing options...")  # Debug print
        if self.game:
            self.game.next_action = "options"

    def quit_game(self) -> None:
        """Quit the game."""
        print("Quitting game...")  # Debug print
        if self.game:
            self.game.next_action = "quit"

    def show(self) -> None:
        """Show the panel by setting it to open state."""
        self.is_open = True
        self.target_x = 0  # Slide to visible position (left side)

    def hide(self) -> None:
        """Hide the panel by setting it to closed state."""
        self.is_open = False
        self.target_x = -self.width  # Slide off-screen to the left

    def toggle(self) -> None:
        """Toggle the panel open/closed state."""
        self.is_open = not self.is_open
        self.target_x = 0 if self.is_open else -self.width
        
    def update(self) -> None:
        """Update panel position and glow effect."""
        # Update position
        if self.current_x < self.target_x:
            self.current_x = min(self.current_x + self.animation_speed, self.target_x)
        elif self.current_x > self.target_x:
            self.current_x = max(self.current_x - self.animation_speed, self.target_x)
            
    def render(self):
        # Calculate handle position - attach to right side of panel
        # When panel is closed, handle should be at x=0
        # When panel is open, handle should be at panel's right edge
        # It finds the handle position as the same as the handle (current) plus the handle width, plus the 20 pixels of the handle
        handle_x = self.panel_rect.width + self.current_x - self.handle_width
        
        # Always render the handle first
        handle_image = self.handle_close_cached if self.is_open else self.handle_open_cached
        self.screen.blit(handle_image, (handle_x, self.y))

        # Only render the panel if visible or animating
        if not (self.is_open or self.current_x != self.target_x):
            return

        # Calculate current rect for dirty rectangle rendering
        current_rect = self.panel_rect.copy()
        current_rect.x = self.current_x
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
        self.screen.blit(panel_surface, (self.current_x, self.y))

        # Store the current rect for next frame's dirty rectangle calculation
        self.last_rect = current_rect

    def handle_events(self, event: pygame.event.Event) -> Optional[str]:
        """
        Handle pygame events for the panel.
        
        Args:
            event: The pygame event to handle
            
        Returns:
            Optional[str]: Action string if an event was handled, None otherwise
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.toggle()
                return "panel_toggled"
                
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check if handle was clicked
            if self.is_handle_clicked(mouse_pos):
                self.toggle()
                return "panel_toggled"
                
            # Check button clicks - adjust mouse position relative to panel
            if self.is_open or self.current_x != self.target_x:
                rel_mouse_x = mouse_pos[0] - self.current_x
                rel_mouse_y = mouse_pos[1] - self.y
                rel_mouse_pos = (rel_mouse_x, rel_mouse_y)
                
                for button in self.buttons:
                    if button.rect.collidepoint(rel_mouse_pos):
                        # Execute the button's action
                        if button.action:
                            button.action()
                        return f"button_{self.buttons.index(button)}_clicked"
                    
        # Handle hover sound and state
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            
            # Only check for hover if panel is visible
            if self.is_open or self.current_x != self.target_x:
                rel_mouse_x = mouse_pos[0] - self.current_x
                rel_mouse_y = mouse_pos[1] - self.y
                rel_mouse_pos = (rel_mouse_x, rel_mouse_y)
                
                for button in self.buttons:
                    if button.rect.collidepoint(rel_mouse_pos):
                        if not button.is_hovered:  # Only play sound when first hovering
                            if hasattr(self, 'hover_sound'):
                                self.hover_sound.play()
                        button.is_hovered = True
                    else:
                        button.is_hovered = False
            else:
                # Reset hover state when panel is not visible
                for button in self.buttons:
                    button.is_hovered = False
                    
        return None

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

        # Cache handle states with proper alpha
        self.handle_open_cached = self.handle_open.copy()
        self.handle_close_cached = self.handle_close.copy()
        self.handle_open_cached.set_alpha(255)  # Ensure full opacity
        self.handle_close_cached.set_alpha(255)  # Ensure full opacity

        # Cache the panel rect for dirty rectangle rendering
        self.panel_rect = pygame.Rect(0, 0, self.width + self.handle_width, self.height)
        self.last_rect = None

    @property
    def x(self) -> int:
        """Get the current x position of the panel."""
        return self.current_x

    def is_handle_clicked(self, pos: Tuple[int, int]) -> bool:
        """
        Check if the click position is within the handle area.
        
        Args:
            pos: The (x, y) position to check
            
        Returns:
            bool: True if the position is within the handle area, False otherwise
        """
        # Handle is attached to the right side of the panel
        handle_x = self.panel_rect.width + self.target_x - self.handle_width
        handle_rect = pygame.Rect(handle_x, self.y, self.handle_width, self.height)
        return handle_rect.collidepoint(pos) 