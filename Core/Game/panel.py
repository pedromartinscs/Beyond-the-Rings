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
        self.speed = 10  # Animation speed
        self.cap_width = 60  # Width of the left and right caps
        self.arrow_width = 20  # Width of the arrow section

        # Load cap and middle images for panel
        self.left_cap = pygame.image.load(os.path.join('Images', 'left_horizontal_menu_cap.png'))
        self.left_cap = pygame.transform.scale(self.left_cap, (self.cap_width, self.height))
        self.right_cap = pygame.image.load(os.path.join('Images', 'right_horizontal_menu_cap.png'))
        self.right_cap = pygame.transform.scale(self.right_cap, (self.cap_width, self.height))
        self.middle = pygame.image.load(os.path.join('Images', 'middle_horizontal_menu.png'))
        self.middle = pygame.transform.scale(self.middle, (1, self.height))  # 1px wide, 200px tall

        # Load handle images
        self.handle_left_cap = pygame.image.load(os.path.join('Images', 'left_horizontal_handle_cap.png'))
        self.handle_left_cap = pygame.transform.scale(self.handle_left_cap, (self.cap_width, self.handle_height))
        self.handle_right_cap = pygame.image.load(os.path.join('Images', 'right_horizontal_handle_cap.png'))
        self.handle_right_cap = pygame.transform.scale(self.handle_right_cap, (self.cap_width, self.handle_height))
        self.handle_middle = pygame.image.load(os.path.join('Images', 'middle_horizontal_handle.png'))
        self.handle_middle = pygame.transform.scale(self.handle_middle, (1, self.handle_height))  # 1px wide, 20px tall
        self.handle_arrow_open = pygame.image.load(os.path.join('Images', 'middle_horizontal_handle_open.png'))
        self.handle_arrow_open = pygame.transform.scale(self.handle_arrow_open, (self.arrow_width, self.handle_height))
        self.handle_arrow_close = pygame.image.load(os.path.join('Images', 'middle_horizontal_handle_close.png'))
        self.handle_arrow_close = pygame.transform.scale(self.handle_arrow_close, (self.arrow_width, self.handle_height))

        # Create cached surfaces
        self.create_cached_surfaces()

    def create_cached_surfaces(self):
        """Create and cache the panel and handle surfaces"""
        # Create the base panel surface
        self.base_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw left cap
        self.base_surface.blit(self.left_cap, (0, 0))
        
        # Draw right cap
        self.base_surface.blit(self.right_cap, (self.width - self.cap_width, 0))
        
        # Draw stretched middle
        middle_width = self.width - (self.cap_width * 2)  # 60px left + 60px right
        if middle_width > 0:
            stretched_middle = pygame.transform.scale(self.middle, (middle_width, self.height))
            self.base_surface.blit(stretched_middle, (self.cap_width, 0))

        # Create handle surfaces for open and closed states
        self.handle_open_surface = pygame.Surface((self.width, self.handle_height), pygame.SRCALPHA)
        self.handle_close_surface = pygame.Surface((self.width, self.handle_height), pygame.SRCALPHA)

        # Calculate the center position for the arrow
        center_x = (self.width - self.arrow_width) // 2

        # Draw handle for both states
        for surface, arrow_image in [(self.handle_open_surface, self.handle_arrow_open), 
                                   (self.handle_close_surface, self.handle_arrow_close)]:
            # Draw left cap
            surface.blit(self.handle_left_cap, (0, 0))
            
            # Draw left stretch
            left_stretch_width = center_x - self.cap_width
            if left_stretch_width > 0:
                left_stretch = pygame.transform.scale(self.handle_middle, (left_stretch_width, self.handle_height))
                surface.blit(left_stretch, (self.cap_width, 0))
            
            # Draw arrow
            surface.blit(arrow_image, (center_x, 0))
            
            # Draw right stretch
            right_stretch_x = center_x + self.arrow_width
            right_stretch_width = self.width - right_stretch_x - self.cap_width
            if right_stretch_width > 0:
                right_stretch = pygame.transform.scale(self.handle_middle, (right_stretch_width, self.handle_height))
                surface.blit(right_stretch, (right_stretch_x, 0))
            
            # Draw right cap
            surface.blit(self.handle_right_cap, (self.width - self.cap_width, 0))

    def show(self):
        # Show the panel (slide it in)
        self.visible = True

    def hide(self):
        # Hide the panel (slide it out)
        self.visible = False

    def is_handle_clicked(self, pos):
        # Calculate handle position
        if self.visible:
            # When panel is visible, handle is on top of panel
            handle_y = self.current_y - self.handle_height
        else:
            # When panel is hidden, handle touches bottom of screen
            handle_y = self.screen.get_height() - self.handle_height
            
        # Check if the click is within the handle area
        handle_rect = pygame.Rect(0, handle_y, self.width, self.handle_height)
        return handle_rect.collidepoint(pos)

    def animate_panel(self, target_y):
        # Smoothly animate the panel's Y position to the target Y position
        if self.visible:
            self.current_y = max(target_y, self.current_y - self.speed)
        else:
            self.current_y = min(target_y, self.current_y + self.speed)

    def render(self):
        # Calculate target positions
        if self.visible:
            target_y = self.screen.get_height() - self.height
        else:
            target_y = self.screen.get_height() - self.handle_height

        # Animate the panel
        self.animate_panel(target_y)
        
        # Render the panel if visible or animating
        if self.visible or self.current_y < self.screen.get_height() - self.handle_height:
            self.screen.blit(self.base_surface, (0, self.current_y))
        
        # Calculate handle position
        if self.visible or self.current_y < self.screen.get_height() - self.handle_height:
            # When panel is visible or animating, handle follows panel
            handle_y = self.current_y - self.handle_height
        else:
            # When panel is fully hidden, handle touches bottom of screen
            handle_y = self.screen.get_height() - self.handle_height
            
        # Render the handle
        handle_image = self.handle_close_surface if self.visible else self.handle_open_surface
        self.screen.blit(handle_image, (0, handle_y))
