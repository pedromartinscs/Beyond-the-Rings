import pygame

class Minimap:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.size = 150  # Size of the minimap in pixels
        self.x = screen_width - self.size - 20  # 20 pixels from right edge
        self.y = 20  # 20 pixels from top edge
        self.surface = pygame.Surface((self.size, self.size))
        self.surface.fill((0, 0, 0))  # Black background
        self.scale = 1.0  # Will be set when map is loaded
        self.map_surface = None  # Will store the scaled map surface

    def set_map(self, map_surface, map_width, map_height):
        """Set the map surface and calculate the scale"""
        self.scale = min(self.size / map_width, self.size / map_height)
        scaled_width = int(map_width * self.scale)
        scaled_height = int(map_height * self.scale)
        self.map_surface = pygame.transform.scale(map_surface, (scaled_width, scaled_height))

    def handle_event(self, event):
        """Handle events for the minimap"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.is_clicked(event.pos):
                    return True
        return False

    def is_clicked(self, pos):
        """Check if a position is within the minimap"""
        return pygame.Rect(self.x, self.y, self.size, self.size).collidepoint(pos)

    def render(self, screen, camera_x, camera_y, camera_width, camera_height):
        """Render the minimap on the screen"""
        # Clear the minimap surface
        self.surface.fill((0, 0, 0))
        
        if self.map_surface:
            # Calculate the position to center the minimap
            minimap_x = (self.size - self.map_surface.get_width()) // 2
            minimap_y = (self.size - self.map_surface.get_height()) // 2
            
            # Draw the minimap
            self.surface.blit(self.map_surface, (minimap_x, minimap_y))
            
            # Draw the viewport rectangle
            viewport_rect = pygame.Rect(
                minimap_x + camera_x * self.scale,
                minimap_y + camera_y * self.scale,
                camera_width * self.scale,
                camera_height * self.scale
            )
            pygame.draw.rect(self.surface, (255, 255, 255), viewport_rect, 2)
        
        # Draw the minimap on the screen
        screen.blit(self.surface, (self.x, self.y)) 