import pygame

class VerticalPanel:
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.width = 200
        self.height = 350
        self.visible = False
        self.x = -self.width  # Start completely hidden
        self.y = (screen.get_height() - self.height) // 2  # Center vertically
        self.speed = 10  # Animation speed
        self.target_x = self.x
        self.handle_width = 20  # Width of the visible handle when hidden

        # Create the panel surface
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.surface.fill((50, 50, 50, 230))  # Less transparent background

        # Create the handle surface
        self.handle_surface = pygame.Surface((self.handle_width, self.height), pygame.SRCALPHA)
        self.handle_surface.fill((70, 70, 70, 230))  # Slightly lighter handle, less transparent

    def show(self):
        self.visible = True
        self.target_x = 0  # Show completely

    def hide(self):
        self.visible = False
        self.target_x = -self.width  # Hide completely

    def is_handle_clicked(self, pos):
        # When hidden, only the handle is visible at x=0
        handle_x = 0 if not self.visible else self.x
        handle_rect = pygame.Rect(handle_x, self.y, self.handle_width, self.height)
        return handle_rect.collidepoint(pos)

    def is_panel_clicked(self, pos):
        if not self.visible:
            return False
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return panel_rect.collidepoint(pos)

    def update(self):
        # Smooth animation
        if self.x < self.target_x:
            self.x = min(self.x + self.speed, self.target_x)
        elif self.x > self.target_x:
            self.x = max(self.x - self.speed, self.target_x)

    def render(self):
        # Draw the handle
        handle_x = 0 if not self.visible else self.x
        self.screen.blit(self.handle_surface, (handle_x, self.y))
        
        # Draw the panel if visible
        if self.visible:
            # Clear the panel surface
            self.surface.fill((50, 50, 50, 230))
            
            # Draw the panel
            self.screen.blit(self.surface, (self.x + self.handle_width, self.y)) 