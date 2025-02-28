import pygame
import sys
from Core.Game.panel import Panel

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Define the tile size (32x32 pixels)
        self.tile_size = 32

        # Define the map size
        self.map_width = 120  # 100 tiles wide
        self.map_height = 120  # 100 tiles tall

        # Load tile images (assuming you have tile images in the Maps folder)
        self.tile_image1 = pygame.image.load("Maps\Common\Tiles\Tile1.png")
        self.tile_image1 = pygame.transform.scale(self.tile_image1, (self.tile_size, self.tile_size))
        self.tile_image2 = pygame.image.load("Maps\Common\Tiles\Tile2.png")
        self.tile_image2 = pygame.transform.scale(self.tile_image2, (self.tile_size, self.tile_size))

        # Create a 2D array representing the map
        self.map = [[(x + y) % 2 for x in range(self.map_width)] for y in range(self.map_height)]

        # Create a surface to hold the entire map
        self.map_surface = pygame.Surface((self.map_width * self.tile_size, self.map_height * self.tile_size))

        # Pre-render the map onto the map_surface
        for y in range(self.map_height):
            for x in range(self.map_width):
                tile = self.tile_image1 if self.map[x][y] == 0 else self.tile_image2
                self.map_surface.blit(tile, (x * self.tile_size, y * self.tile_size))

        # Camera variables
        self.camera_x = 0
        self.camera_y = 0
        self.camera_speed = 5
        self.camera_width = self.screen_width
        self.camera_height = self.screen_height

        # Panel variables
        self.panel = Panel(self.screen)
        self.panel_visible = False  # Track panel visibility

    def render(self):
        # Clear the screen before rendering
        self.screen.fill((0, 0, 0))  # Black background

        # Render only the visible portion of the map (by blitting map_surface with camera offset)
        camera_rect = pygame.Rect(self.camera_x, self.camera_y, self.camera_width, self.camera_height)
        self.screen.blit(self.map_surface, (0, 0), camera_rect)

        # Render the panel (if visible)
        self.panel.render()

    def handle_events(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Toggle the panel visibility when space is pressed
                if self.panel_visible:
                    self.panel.hide()  # Hide the panel
                else:
                    self.panel.show()  # Show the panel
                self.panel_visible = not self.panel_visible

    def update(self):
        # Update the camera position based on mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Check if the mouse is at the edge of the screen
        if mouse_x < 10:
            self.camera_x -= self.camera_speed
        elif mouse_x > self.screen_width - 10:
            self.camera_x += self.camera_speed

        if mouse_y < 10:
            self.camera_y -= self.camera_speed
        elif mouse_y > self.screen_height - 10:
            self.camera_y += self.camera_speed

        # Ensure the camera doesn't move out of bounds
        self.camera_x = max(0, min(self.camera_x, self.map_width * self.tile_size - self.camera_width))
        self.camera_y = max(0, min(self.camera_y, self.map_height * self.tile_size - self.camera_height))
