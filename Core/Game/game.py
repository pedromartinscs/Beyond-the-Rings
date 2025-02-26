import pygame
import sys

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Define the tile size (32x32 pixels)
        self.tile_size = 32

        # Define the map size (for now we create a large map for testing)
        self.map_width = 100  # 100 tiles wide
        self.map_height = 100  # 100 tiles tall

        # Load the tile images
        self.tile_image1 = pygame.image.load("Maps\Common\Tiles\Tile1.png")
        self.tile_image1 = pygame.transform.scale(self.tile_image1, (self.tile_size, self.tile_size))
        self.tile_image2 = pygame.image.load("Maps\Common\Tiles\Tile2.png")
        self.tile_image2 = pygame.transform.scale(self.tile_image2, (self.tile_size, self.tile_size))

        # Create a 2D array representing the map (you can later load this from a file or random generation)
        self.map = [[(x + y) % 2 for x in range(self.map_width)] for y in range(self.map_height)]  # Simple checkerboard pattern for testing

        # Camera variables
        self.camera_x = 0
        self.camera_y = 0
        self.camera_speed = 5  # Speed of camera movement when moving by mouse edge
        self.camera_width = self.screen_width
        self.camera_height = self.screen_height

    def render(self):
        print("camera: " + str(self.camera_x) + ", " + str(self.camera_y))
        print
        # Clear the screen before rendering
        self.screen.fill((0, 0, 0))  # Black background (or any color you prefer)

        # Render only the visible portion of the map based on the camera position
        for y in range(self.screen_height // self.tile_size + 1):  # Loop through the vertical tiles that fit
            for x in range(self.screen_width // self.tile_size + 1):  # Loop through the horizontal tiles that fit
                # Calculate the position of the tile relative to the camera
                map_x = (x + self.camera_x // self.tile_size)
                map_y = (y + self.camera_y // self.tile_size)

                # Ensure the tile is inside the map bounds
                if map_x < self.map_width and map_y < self.map_height:
                    # Calculate the screen position for the tile
                    screen_x = x * self.tile_size - self.camera_x
                    screen_y = y * self.tile_size - self.camera_y

                    # Draw the tile using the correct image for the checkerboard pattern
                    if (map_x + map_y) % 2 == 0:
                        self.screen.blit(self.tile_image1, (screen_x, screen_y))
                    else:
                        self.screen.blit(self.tile_image2, (screen_x, screen_y))

    def handle_events(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    def update(self):
        # Update the camera position based on mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Check if the mouse is at the edge of the screen
        if mouse_x < 10:  # Left edge
            self.camera_x -= self.camera_speed
        elif mouse_x > self.screen_width - 10:  # Right edge
            self.camera_x += self.camera_speed

        if mouse_y < 10:  # Top edge
            self.camera_y -= self.camera_speed
        elif mouse_y > self.screen_height - 10:  # Bottom edge
            self.camera_y += self.camera_speed

        # Ensure the camera doesn't move out of bounds (clamping the camera within the map)
        self.camera_x = max(0, min(self.camera_x, self.map_width * self.tile_size - self.camera_width))
        self.camera_y = max(0, min(self.camera_y, self.map_height * self.tile_size - self.camera_height))
