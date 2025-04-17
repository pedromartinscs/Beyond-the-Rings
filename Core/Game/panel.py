import pygame
import os

class Panel:
    def __init__(self, screen):
        self.screen = screen
        self.width = screen.get_width()
        self.height = 200  # Height of the panel
        self.color = (50, 50, 50)  # Color of the panel
        self.visible = False  # Start with the panel hidden
        self.current_y = self.screen.get_height()  # Panel starts off-screen (at the bottom)
        self.handle_height = 20  # Height of the visible handle when hidden

        # Load cap and middle images
        self.left_cap = pygame.image.load(os.path.join('Images', 'left_horizontal_menu_cap.png'))
        self.left_cap = pygame.transform.scale(self.left_cap, (41, self.height))
        self.right_cap = pygame.image.load(os.path.join('Images', 'right_horizontal_menu_cap.png'))
        self.right_cap = pygame.transform.scale(self.right_cap, (41, self.height))
        self.middle = pygame.image.load(os.path.join('Images', 'middle_horizontal_menu.png'))
        self.middle = pygame.transform.scale(self.middle, (1, self.height))  # 1px wide, 200px tall

        # Create cached surfaces
        self.create_cached_surfaces()

    def create_cached_surfaces(self):
        """Create and cache the panel surfaces"""
        # Create the base panel surface
        self.base_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw left cap
        self.base_surface.blit(self.left_cap, (0, 0))
        
        # Draw right cap
        self.base_surface.blit(self.right_cap, (self.width - 41, 0))
        
        # Draw stretched middle
        middle_width = self.width - 82  # 41px left + 41px right
        if middle_width > 0:
            stretched_middle = pygame.transform.scale(self.middle, (middle_width, self.height))
            self.base_surface.blit(stretched_middle, (41, 0))

    def show(self):
        # Show the panel (slide it in)
        self.visible = True

    def hide(self):
        # Hide the panel (slide it out)
        self.visible = False

    def is_handle_clicked(self, pos):
        # Check if the click is within the handle area (top 20 pixels of the panel)
        handle_rect = pygame.Rect(0, self.current_y, self.width, self.handle_height)
        return handle_rect.collidepoint(pos)

    def animate_panel(self, target_y):
        # Smoothly animate the panel's Y position to the target Y position
        # This will create a sliding effect
        speed = 20  # Speed of the panel animation
        if self.visible:
            self.current_y = max(target_y, self.current_y - speed)
        else:
            self.current_y = min(target_y, self.current_y + speed)

    def render(self):
        if self.visible:  # Only render if the panel is visible
            self.animate_panel(self.screen.get_height() - self.height)
        else:
            self.animate_panel(self.screen.get_height() - self.handle_height)
        
        # Draw the cached panel surface at the current position
        self.screen.blit(self.base_surface, (0, self.current_y))
