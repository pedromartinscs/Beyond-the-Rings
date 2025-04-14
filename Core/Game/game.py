import pygame
import sys
from Core.Game.panel import Panel
from Core.Game.vertical_panel import VerticalPanel

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Initialize the mixer for playing music
        pygame.mixer.init()  # Initialize the pygame mixer
        
        # Load and play the combined music file
        self.music_file = "Music/__bertsz__cyberpunk_MULTI.mp3"
        pygame.mixer.music.load(self.music_file)
        pygame.mixer.music.play(-1)  # Play in an infinite loop

        # Mouse state tracking
        self.is_dragging_minimap = False
        self.last_mouse_pos = None

        # Define the tile size (32x32 pixels)
        self.tile_size = 32

        # Load all tile images
        self.tiles = []
        for i in range(18):  # Load tiles 00000.png to 00017.png
            try:
                tile_path = f"Maps/Common/Tiles/{i:05d}.png"
                tile_image = pygame.image.load(tile_path)
                tile_image = pygame.transform.scale(tile_image, (self.tile_size, self.tile_size))
                self.tiles.append(tile_image)
            except pygame.error as e:
                print(f"Error loading tile {i:05d}.png: {e}")
                # If a tile fails to load, use a default colored surface
                default_tile = pygame.Surface((self.tile_size, self.tile_size))
                default_tile.fill((i * 10, i * 10, i * 10))  # Different shade for each missing tile
                self.tiles.append(default_tile)

        # Load the map from file
        self.map = self.load_map("C:\Projetos\Personal\Github\Beyond-the-Rings\Maps\Battle\map.txt")
        self.map_width = len(self.map[0]) if self.map else 120
        self.map_height = len(self.map) if self.map else 120

        # Create a surface to hold the entire map
        self.map_surface = pygame.Surface((self.map_width * self.tile_size, self.map_height * self.tile_size))

        # Pre-render the map onto the map_surface
        for y in range(self.map_height):
            for x in range(self.map_width):
                tile_index = self.map[y][x]
                if 0 <= tile_index < len(self.tiles):
                    self.map_surface.blit(self.tiles[tile_index], (x * self.tile_size, y * self.tile_size))
                else:
                    # If tile index is out of range, use the first tile
                    self.map_surface.blit(self.tiles[0], (x * self.tile_size, y * self.tile_size))

        # Create minimap
        self.minimap_size = 150  # Size of the minimap in pixels
        self.minimap_surface = pygame.Surface((self.minimap_size, self.minimap_size))
        self.minimap_scale = min(self.minimap_size / (self.map_width * self.tile_size),
                               self.minimap_size / (self.map_height * self.tile_size))
        
        # Create a scaled version of the map for the minimap
        self.minimap_map = pygame.transform.scale(self.map_surface, 
            (int(self.map_width * self.tile_size * self.minimap_scale),
             int(self.map_height * self.tile_size * self.minimap_scale)))

        # Calculate minimap position (top right corner)
        self.minimap_x = self.screen_width - self.minimap_size - 20  # 20 pixels from right edge
        self.minimap_y = 20  # 20 pixels from top edge

        # Camera variables
        self.camera_x = 0
        self.camera_y = 0
        self.camera_speed = 5
        self.camera_width = self.screen_width
        self.camera_height = self.screen_height

        # Panel variables
        self.panel = Panel(self.screen)
        self.vertical_panel = VerticalPanel(self.screen, self)  # Pass self to access minimap
        self.panel_visible = False  # Track bottom panel visibility
        self.vertical_panel_visible = False  # Track vertical panel visibility

    def load_map(self, file_path):
        try:
            with open(file_path, 'r') as file:
                # Read the first line to get map dimensions
                first_line = file.readline().strip()
                width, height = map(int, first_line.split())
                
                map_data = []
                for line in file:
                    # Extract tile numbers from [00000] format
                    tiles = []
                    i = 0
                    while i < len(line):
                        if line[i] == '[':
                            # Find the closing bracket
                            end = line.find(']', i)
                            if end != -1:
                                # Extract the number between brackets
                                tile_num = int(line[i+1:end])
                                tiles.append(tile_num)
                                i = end + 1
                            else:
                                i += 1
                        else:
                            i += 1
                    if tiles:  # Only add non-empty rows
                        map_data.append(tiles)
                
                # Verify map dimensions
                if len(map_data) != height or (map_data and len(map_data[0]) != width):
                    print(f"Warning: Map dimensions don't match header. Expected {width}x{height}, got {len(map_data[0]) if map_data else 0}x{len(map_data)}")
                
                return map_data
        except FileNotFoundError:
            print(f"Map file not found: {file_path}")
            return [[(x + y) % 2 for x in range(120)] for y in range(120)]  # Return default map if file not found
        except Exception as e:
            print(f"Error loading map: {e}")
            return [[(x + y) % 2 for x in range(120)] for y in range(120)]  # Return default map if error occurs

    def is_minimap_clicked(self, pos):
        minimap_rect = pygame.Rect(self.minimap_x, self.minimap_y, 
                                 self.minimap_size, self.minimap_size)
        return minimap_rect.collidepoint(pos)

    def handle_events(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Toggle the bottom panel visibility when space is pressed
                if self.panel_visible:
                    self.panel.hide()  # Hide the panel
                else:
                    self.panel.show()  # Show the panel
                self.panel_visible = not self.panel_visible
            elif event.key == pygame.K_ESCAPE:
                # Toggle the vertical panel visibility when escape is pressed
                if self.vertical_panel_visible:
                    self.vertical_panel.hide()
                else:
                    self.vertical_panel.show()
                self.vertical_panel_visible = not self.vertical_panel_visible

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check if minimap is clicked with left mouse button
            if event.button == 1 and self.is_minimap_clicked(mouse_pos):
                self.is_dragging_minimap = True
                self.last_mouse_pos = mouse_pos
                self.update_camera_from_minimap(mouse_pos)
            
            # Check if vertical panel handle is clicked
            elif self.vertical_panel.is_handle_clicked(mouse_pos):
                if self.vertical_panel_visible:
                    self.vertical_panel.hide()
                else:
                    self.vertical_panel.show()
                self.vertical_panel_visible = not self.vertical_panel_visible
            
            # Check if bottom panel handle is clicked
            elif self.panel.is_handle_clicked(mouse_pos):
                if self.panel_visible:
                    self.panel.hide()
                else:
                    self.panel.show()
                self.panel_visible = not self.panel_visible

        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_dragging_minimap = False
            self.last_mouse_pos = None

        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging_minimap:
                mouse_pos = pygame.mouse.get_pos()
                if self.is_minimap_clicked(mouse_pos):
                    self.update_camera_from_minimap(mouse_pos)
                self.last_mouse_pos = mouse_pos

    def update_camera_from_minimap(self, mouse_pos):
        # Calculate the click position relative to the minimap
        rel_x = mouse_pos[0] - self.minimap_x
        rel_y = mouse_pos[1] - self.minimap_y
        
        # Convert minimap coordinates to world coordinates
        world_x = int(rel_x / self.minimap_scale)
        world_y = int(rel_y / self.minimap_scale)
        
        # Center the camera on the clicked position
        self.camera_x = max(0, min(world_x - self.camera_width // 2, 
                                 self.map_width * self.tile_size - self.camera_width))
        self.camera_y = max(0, min(world_y - self.camera_height // 2,
                                 self.map_height * self.tile_size - self.camera_height))

    def render(self):
        # Clear the screen before rendering
        self.screen.fill((0, 0, 0))  # Black background

        # Render only the visible portion of the map (by blitting map_surface with camera offset)
        camera_rect = pygame.Rect(self.camera_x, self.camera_y, self.camera_width, self.camera_height)
        self.screen.blit(self.map_surface, (0, 0), camera_rect)

        # Render the minimap
        self.update_minimap()
        self.screen.blit(self.minimap_surface, (self.minimap_x, self.minimap_y))

        # Render the panels
        self.vertical_panel.render()
        self.panel.render()

    def update(self):
        # Update the camera position based on mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Define the edge detection area and speed
        edge_area = 10  # Pixels from the edge to start moving
        base_speed = self.camera_speed
        edge_speed = base_speed * 2  # Double speed at edges

        # Check if the mouse is at the edge of the screen and apply appropriate speed
        if mouse_x < edge_area:
            self.camera_x -= edge_speed
        elif mouse_x > self.screen_width - edge_area:
            self.camera_x += edge_speed
        else:
            # If mouse is near the edge but not at it, use base speed
            if mouse_x < edge_area * 2:
                self.camera_x -= base_speed
            elif mouse_x > self.screen_width - edge_area * 2:
                self.camera_x += base_speed

        if mouse_y < edge_area:
            self.camera_y -= edge_speed
        elif mouse_y > self.screen_height - edge_area:
            self.camera_y += edge_speed
        else:
            # If mouse is near the edge but not at it, use base speed
            if mouse_y < edge_area * 2:
                self.camera_y -= base_speed
            elif mouse_y > self.screen_height - edge_area * 2:
                self.camera_y += base_speed

        # Ensure the camera doesn't move out of bounds
        self.camera_x = max(0, min(self.camera_x, self.map_width * self.tile_size - self.camera_width))
        self.camera_y = max(0, min(self.camera_y, self.map_height * self.tile_size - self.camera_height))

        # Update panel animations
        self.vertical_panel.update()

    def update_minimap(self):
        # Clear the minimap surface
        self.minimap_surface.fill((0, 0, 0))
        
        # Calculate the position to center the minimap
        minimap_x = (self.minimap_size - self.minimap_map.get_width()) // 2
        minimap_y = (self.minimap_size - self.minimap_map.get_height()) // 2
        
        # Draw the minimap
        self.minimap_surface.blit(self.minimap_map, (minimap_x, minimap_y))
        
        # Draw the viewport rectangle
        viewport_rect = pygame.Rect(
            minimap_x + self.camera_x * self.minimap_scale,
            minimap_y + self.camera_y * self.minimap_scale,
            self.camera_width * self.minimap_scale,
            self.camera_height * self.minimap_scale
        )
        pygame.draw.rect(self.minimap_surface, (255, 255, 255), viewport_rect, 2)
