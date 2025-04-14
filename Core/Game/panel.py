import pygame

class Panel:
    def __init__(self, screen):
        self.screen = screen
        self.width = screen.get_width()
        self.height = 200  # Height of the panel
        self.color = (50, 50, 50)  # Color of the panel
        self.visible = False  # Start with the panel hidden
        self.current_y = self.screen.get_height()  # Panel starts off-screen (at the bottom)
        self.handle_height = 20  # Height of the visible handle when hidden

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
            # Draw the panel at the current Y position
            self.animate_panel(self.screen.get_height() - self.height)
        else:
            self.animate_panel(self.screen.get_height() - self.handle_height)
        pygame.draw.rect(self.screen, self.color, (0, self.current_y, self.width, self.height))
