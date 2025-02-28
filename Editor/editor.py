import pygame
import sys
import tkinter as tk
from tkinter import filedialog

# Main class for the map editor
class Editor:
    # --- Initialization ---
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = screen.get_width() - 50      # Screen width with padding
        self.screen_height = screen.get_height() - 50    # Screen height with padding
        
        # Tile and map setup
        self.tile_size = 32                              # Size of each tile (32x32 pixels)
        self.map_width = 100                             # Map width in tiles
        self.map_height = 100                            # Map height in tiles
        
        # Load and scale tile images (4 selectable + transition tiles)
        self.tile_images = []                            # List to store tile images
        # Selectable tiles (0-3)
        grass1 = pygame.image.load("Maps/Common/Tiles/00000.png")  # Grass tile 1
        grass1 = pygame.transform.scale(grass1, (self.tile_size, self.tile_size))
        self.tile_images.append(grass1)
        grass2 = pygame.image.load("Maps/Common/Tiles/00001.png")  # Grass tile 2
        grass2 = pygame.transform.scale(grass2, (self.tile_size, self.tile_size))
        self.tile_images.append(grass2)
        water1 = pygame.image.load("Maps/Common/Tiles/00002.png")  # Water tile 1
        water1 = pygame.transform.scale(water1, (self.tile_size, self.tile_size))
        self.tile_images.append(water1)
        water2 = pygame.image.load("Maps/Common/Tiles/00003.png")  # Water tile 2
        water2 = pygame.transform.scale(water2, (self.tile_size, self.tile_size))
        self.tile_images.append(water2)
        # Transition tiles (4-15, not selectable)
        shore_top = pygame.image.load("Maps/Common/Tiles/00004.png")
        shore_top = pygame.transform.scale(shore_top, (self.tile_size, self.tile_size))
        self.tile_images.append(shore_top)
        shore_bottom = pygame.image.load("Maps/Common/Tiles/00005.png")
        shore_bottom = pygame.transform.scale(shore_bottom, (self.tile_size, self.tile_size))
        self.tile_images.append(shore_bottom)
        shore_left = pygame.image.load("Maps/Common/Tiles/00006.png")
        shore_left = pygame.transform.scale(shore_left, (self.tile_size, self.tile_size))
        self.tile_images.append(shore_left)
        shore_right = pygame.image.load("Maps/Common/Tiles/00007.png")
        shore_right = pygame.transform.scale(shore_right, (self.tile_size, self.tile_size))
        self.tile_images.append(shore_right)
        shore_topleft = pygame.image.load("Maps/Common/Tiles/00008.png")
        shore_topleft = pygame.transform.scale(shore_topleft, (self.tile_size, self.tile_size))
        self.tile_images.append(shore_topleft)
        shore_topright = pygame.image.load("Maps/Common/Tiles/00009.png")
        shore_topright = pygame.transform.scale(shore_topright, (self.tile_size, self.tile_size))
        self.tile_images.append(shore_topright)
        shore_bottomleft = pygame.image.load("Maps/Common/Tiles/00010.png")
        shore_bottomleft = pygame.transform.scale(shore_bottomleft, (self.tile_size, self.tile_size))
        self.tile_images.append(shore_bottomleft)
        shore_bottomright = pygame.image.load("Maps/Common/Tiles/00011.png")
        shore_bottomright = pygame.transform.scale(shore_bottomright, (self.tile_size, self.tile_size))
        self.tile_images.append(shore_bottomright)
        shore_top_tip_left = pygame.image.load("Maps/Common/Tiles/00012.png")
        shore_top_tip_left = pygame.transform.scale(shore_top_tip_left, (self.tile_size, self.tile_size))
        self.tile_images.append(shore_top_tip_left)
        shore_top_tip_right = pygame.image.load("Maps/Common/Tiles/00013.png")
        shore_top_tip_right = pygame.transform.scale(shore_top_tip_right, (self.tile_size, self.tile_size))
        self.tile_images.append(shore_top_tip_right)
        shore_bottom_tip_left = pygame.image.load("Maps/Common/Tiles/00014.png")
        shore_bottom_tip_left = pygame.transform.scale(shore_bottom_tip_left, (self.tile_size, self.tile_size))
        self.tile_images.append(shore_bottom_tip_left)
        shore_bottom_tip_right = pygame.image.load("Maps/Common/Tiles/00015.png")
        shore_bottom_tip_right = pygame.transform.scale(shore_bottom_tip_right, (self.tile_size, self.tile_size))
        self.tile_images.append(shore_bottom_tip_right)
        
        self.selectable_tiles = 4                        # Only first 4 tiles are selectable
        self.selected_tile = 0                           # Index of currently selected tile (default: 0)
        
        # Initialize map as a 2D array filled with grass (tile 0)
        self.map = [[0 for _ in range(self.map_width)] for _ in range(self.map_height)]
        
        # Palette setup (right side UI)
        self.palette_width = 150                         # Width reserved for palette
        self.palette_offset_x = 40                       # Horizontal offset for palette
        
        # Camera for map scrolling
        self.camera_x = 0                                # Camera X position (pixels)
        self.camera_y = 0                                # Camera Y position (pixels)
        self.camera_speed = 10                           # Speed of camera movement
        
        # Dragging state for right-click map movement
        self.dragging = False                            # Is the map being dragged?
        self.last_mouse_pos = None                       # Last mouse position during drag
        
        # Palette buttons (Exit, Save, Load)
        self.exit_button_rect = pygame.Rect(
            self.screen_width - self.palette_width + self.palette_offset_x,
            self.screen_height - 160,
            100, 30
        )
        self.save_button_rect = pygame.Rect(
            self.screen_width - self.palette_width + self.palette_offset_x,
            self.screen_height - 120,
            100, 30
        )
        self.load_button_rect = pygame.Rect(
            self.screen_width - self.palette_width + self.palette_offset_x,
            self.screen_height - 80,
            100, 30
        )
        
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)  # Set default cursor to arrow
    
    # --- Rendering ---
    def render(self):
        self.screen.fill((30, 30, 30))                   # Dark gray background
        
        # Define map area (grid on left side)
        map_margin_right = 20
        map_area_width = self.screen_width - self.palette_width - map_margin_right
        map_area_height = self.screen_height - 40
        map_area_rect = pygame.Rect(0, 0, map_area_width, map_area_height)
        
        # Create a subsurface for the map to enforce clipping
        map_surface = self.screen.subsurface(map_area_rect)
        map_surface.fill((30, 30, 30))
        
        # Calculate visible tiles
        start_tile_x = self.camera_x // self.tile_size
        start_tile_y = self.camera_y // self.tile_size
        tiles_visible_x = (map_area_width // self.tile_size) + 2
        tiles_visible_y = (map_area_height // self.tile_size) + 2
        
        # Render map tiles
        for y in range(tiles_visible_y):
            for x in range(tiles_visible_x):
                map_x = start_tile_x + x
                map_y = start_tile_y + y
                if 0 <= map_x < self.map_width and 0 <= map_y < self.map_height:
                    screen_x = (x * self.tile_size) - (self.camera_x % self.tile_size)
                    screen_y = (y * self.tile_size) - (self.camera_y % self.tile_size)
                    tile_index = self.map[map_y][map_x]
                    map_surface.blit(self.tile_images[tile_index], (screen_x, screen_y))
        
        # Draw grid lines
        start_x = -(self.camera_x % self.tile_size)
        start_y = -(self.camera_y % self.tile_size)
        for x in range(start_x, map_area_width, self.tile_size):
            pygame.draw.line(map_surface, (50, 50, 50), (x, 0), (x, map_area_height))
        for y in range(start_y, map_area_height, self.tile_size):
            pygame.draw.line(map_surface, (50, 50, 50), (0, y), (map_area_width, y))
        
        # Render palette (only selectable tiles)
        palette_x = self.screen_width - self.palette_width + self.palette_offset_x
        palette_y = 10
        for i in range(self.selectable_tiles):
            rect = pygame.Rect(palette_x, palette_y + i * (self.tile_size + 10), self.tile_size, self.tile_size)
            self.screen.blit(self.tile_images[i], rect.topleft)
            if i == self.selected_tile:
                pygame.draw.rect(self.screen, (255, 255, 0), rect, 3)
        
        # Draw palette buttons
        pygame.draw.rect(self.screen, (200, 0, 0), self.exit_button_rect)
        pygame.draw.rect(self.screen, (0, 200, 0), self.save_button_rect)
        pygame.draw.rect(self.screen, (0, 0, 200), self.load_button_rect)
        
        # Render button text
        font = pygame.font.Font(None, 24)
        exit_text = font.render("Exit", True, (255, 255, 255))
        save_text = font.render("Save Map", True, (255, 255, 255))
        load_text = font.render("Load Map", True, (255, 255, 255))
        self.screen.blit(exit_text, (self.exit_button_rect.x + 5, self.exit_button_rect.y + 5))
        self.screen.blit(save_text, (self.save_button_rect.x + 5, self.save_button_rect.y + 5))
        self.screen.blit(load_text, (self.load_button_rect.x + 5, self.load_button_rect.y + 5))
        
        # Display instructions
        instructions = "Left click: place tile; Right click: drag map; Click palette to select tile."
        inst_text = font.render(instructions, True, (255, 255, 255))
        self.screen.blit(inst_text, (10, map_area_height + 10))
    
    # --- Event Handling ---
    def handle_events(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # Define clickable palette areas
        palette_buttons = [self.exit_button_rect, self.save_button_rect, self.load_button_rect]
        for i in range(self.selectable_tiles):
            rect = pygame.Rect(
                self.screen_width - self.palette_width + self.palette_offset_x,
                10 + i * (self.tile_size + 10),
                self.tile_size,
                self.tile_size
            )
            palette_buttons.append(rect)
        
        # Mouse hover cursor change
        if event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
            over_button = any(rect.collidepoint(mouse_x, mouse_y) for rect in palette_buttons)
            if over_button:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        
        # Mouse button press
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_x, mouse_y = event.pos
                if mouse_x >= self.screen_width - self.palette_width:  # Palette area
                    palette_x = self.screen_width - self.palette_width + self.palette_offset_x
                    palette_y = 10
                    for i in range(self.selectable_tiles):
                        rect = pygame.Rect(palette_x, palette_y + i * (self.tile_size + 10), self.tile_size, self.tile_size)
                        if rect.collidepoint(event.pos):
                            self.selected_tile = i
                            break
                    if self.exit_button_rect.collidepoint(event.pos):
                        self.exit_editor()
                    if self.save_button_rect.collidepoint(event.pos):
                        self.save_map()
                    if self.load_button_rect.collidepoint(event.pos):
                        self.load_map()
                else:  # Map area
                    map_x = (mouse_x + self.camera_x) // self.tile_size
                    map_y = (mouse_y + self.camera_y) // self.tile_size
                    if 0 <= map_x < self.map_width and 0 <= map_y < self.map_height:
                        self.place_tile(map_x, map_y)
                    self.left_button_down = True
            elif event.button == 3:  # Right click (drag start)
                self.dragging = True
                self.last_mouse_pos = event.pos
        
        # Mouse button release
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.left_button_down = False
            if event.button == 3:
                self.dragging = False
                self.last_mouse_pos = None
        
        # Mouse movement (dragging or painting)
        if event.type == pygame.MOUSEMOTION:
            if hasattr(self, 'left_button_down') and self.left_button_down:
                mouse_x, mouse_y = event.pos
                if mouse_x < self.screen_width - self.palette_width:
                    map_x = (mouse_x + self.camera_x) // self.tile_size
                    map_y = (mouse_y + self.camera_y) // self.tile_size
                    if 0 <= map_x < self.map_width and 0 <= map_y < self.map_height:
                        self.place_tile(map_x, map_y)
            if self.dragging and self.last_mouse_pos is not None:
                dx = event.pos[0] - self.last_mouse_pos[0]
                dy = event.pos[1] - self.last_mouse_pos[1]
                self.camera_x -= dx
                self.camera_y -= dy
                max_camera_x = self.map_width * self.tile_size - (self.screen_width - self.palette_width)
                max_camera_y = self.map_height * self.tile_size - self.screen_height
                self.camera_x = max(0, min(self.camera_x, max_camera_x))
                self.camera_y = max(0, min(self.camera_y, max_camera_y))
                self.last_mouse_pos = event.pos
    
        # Keyboard camera movement
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.camera_x = max(0, self.camera_x - self.camera_speed)
            elif event.key == pygame.K_RIGHT:
                max_x = self.map_width * self.tile_size - (self.screen_width - self.palette_width)
                self.camera_x = min(max_x, self.camera_x + self.camera_speed)
            elif event.key == pygame.K_UP:
                self.camera_y = max(0, self.camera_y - self.camera_speed)
            elif event.key == pygame.K_DOWN:
                max_y = self.map_height * self.tile_size - self.screen_height
                self.camera_y = min(max_y, self.camera_y + self.camera_speed)
    
    # --- Tile Placement and Auto-Tiling ---
    def place_tile(self, map_x, map_y):
        # Check if placing grass would isolate it
        if self.selected_tile in [0, 1]:
            if self.is_isolated_grass(map_x, map_y):
                return  # Don't place grass if it would be surrounded
        
        # Place the selected tile
        old_tile = self.map[map_y][map_x]
        self.map[map_y][map_x] = self.selected_tile
        
        # Update the surrounding area if the tile type changed (water or grass placement)
        if old_tile != self.selected_tile:
            self.update_map_area(map_x, map_y)
    
    def is_isolated_grass(self, map_x, map_y):
        # Check if placing grass here would surround it with water or shore
        directions = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        all_surrounded = True
        has_water_or_shore = False
        for dx, dy in directions:
            new_x, new_y = map_x + dx, map_y + dy
            if 0 <= new_x < self.map_width and 0 <= new_y < self.map_height:
                tile = self.map[new_y][new_x]
                if tile in [0, 1]:  # Grass neighbor
                    all_surrounded = False
                if tile in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]:  # Water or shore
                    has_water_or_shore = True
            else:
                all_surrounded = False  # Edge counts as accessible
        return all_surrounded and has_water_or_shore

    def update_map_area(self, map_x, map_y):
        # Find all connected water tiles and ensure they are surrounded by shores
        water_tiles = self.find_water_region(map_x, map_y)
        for water_x, water_y in water_tiles:
            self.ensure_water_surrounded(water_x, water_y)
        # Refine shore tiles in the affected area with multiple passes
        for _ in range(2):  # Two passes to ensure convergence
            for y in range(max(0, map_y - 1), min(self.map_height, map_y + 2)):
                for x in range(max(0, map_x - 1), min(self.map_width, map_x + 2)):
                    if self.map[y][x] in [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]:
                        self.correct_shore_tile(x, y)
        # Check for and convert isolated shore tiles
        for y in range(max(0, map_y - 1), min(self.map_height, map_y + 2)):
            for x in range(max(0, map_x - 1), min(self.map_width, map_x + 2)):
                if self.map[y][x] in [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]:
                    if not self.has_adjacent_grass(x, y):
                        self.map[y][x] = 2  # Convert to water
                        self.ensure_water_surrounded(x, y)
                        self.update_map_area(x, y)  # Recursively update the area
        # Reset and re-detect shores in the affected area
        for y in range(max(0, map_y - 1), min(self.map_height, map_y + 2)):
            for x in range(max(0, map_x - 1), min(self.map_width, map_x + 2)):
                if self.has_adjacent_water(x, y) and self.map[y][x] in [4, 5, 6, 7, 8, 9, 10, 11]:
                    self.map[y][x] = 0  # Reset to grass
        # Re-run water surrounding and correction
        for water_x, water_y in water_tiles:
            self.ensure_water_surrounded(water_x, water_y)
        for y in range(max(0, map_y - 1), min(self.map_height, map_y + 2)):
            for x in range(max(0, map_x - 1), min(self.map_width, map_x + 2)):
                self.correct_shore_tile(x, y)

    def find_water_region(self, map_x, map_y):
        # Use flood fill to identify all connected water tiles
        if self.map[map_y][map_x] not in [2, 3]:
            return set()  # Only process if the starting tile is water
        water_set = set()
        stack = [(map_x, map_y)]
        while stack:
            x, y = stack.pop()
            if (x, y) in water_set or not (0 <= x < self.map_width and 0 <= y < self.map_height):
                continue
            if self.map[y][x] in [2, 3]:  # Water tile
                water_set.add((x, y))
                # Check adjacent tiles
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # Cardinal directions
                    stack.append((x + dx, y + dy))
        return water_set

    def ensure_water_surrounded(self, map_x, map_y):
        # Determine appropriate shore tiles based on adjacent tiles and water body perimeter
        directions = [
            (0, -1, 4), (0, 1, 5), (-1, 0, 6), (1, 0, 7),  # Straight shores
            (-1, -1, 8), (1, -1, 9), (-1, 1, 10), (1, 1, 11)  # Corners
        ]
        if self.map[map_y][map_x] not in [2, 3]:
            return  # Only process water tiles
        for dx, dy, shore_index in directions:
            new_x, new_y = map_x + dx, map_y + dy
            if 0 <= new_x < self.map_width and 0 <= new_y < self.map_height:
                neighbor = self.map[new_y][new_x]
                # Place shore if neighbor is grass or if it's the outer edge of the water body
                if neighbor in [0, 1]:  # Grass neighbor
                    self.map[new_y][new_x] = shore_index
                elif neighbor in [2, 3]:  # Adjacent water, check outer boundary
                    opp_dx, opp_dy = -dx, -dy
                    opp_x, opp_y = new_x + opp_dx, new_y + opp_dy
                    if 0 <= opp_x < self.map_width and 0 <= opp_y < self.map_height:
                        if self.map[opp_y][opp_x] in [0, 1]:  # Grass on the outer side
                            self.map[new_x][new_y] = shore_index
                    else:  # Edge of map
                        self.map[new_x][new_y] = shore_index

    def has_adjacent_water(self, map_x, map_y):
        # Check if the tile has adjacent water
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        for dx, dy in directions:
            new_x, new_y = map_x + dx, map_y + dy
            if 0 <= new_x < self.map_width and 0 <= new_y < self.map_height:
                if self.map[new_y][new_x] in [2, 3]:
                    return True
        return False

    def has_adjacent_grass(self, map_x, map_y):
        # Check if the tile has adjacent grass (including diagonals)
        directions = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        for dx, dy in directions:
            new_x, new_y = map_x + dx, map_y + dy
            if 0 <= new_x < self.map_width and 0 <= new_y < self.map_height:
                if self.map[new_y][new_x] in [0, 1]:
                    return True
        return False

    def correct_shore_tile(self, map_x, map_y):
        tile = self.map[map_y][map_x]
        if tile not in [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]:
            return  # Only process shore tiles

        # Check tip conditions with higher priority
        if tile == 4:  # shore-top
            if (self.is_within_bounds(map_x + 1, map_y) and self.map[map_y][map_x + 1] in [2, 3] and  # Right is water
                self.is_within_bounds(map_x, map_y + 1) and self.map[map_y + 1][map_x] in [2, 3] and  # Below is water
                self.is_within_bounds(map_x - 1, map_y - 1) and self.map[map_y - 1][map_x - 1] in [0, 1]):  # Up-left is grass
                self.map[map_y][map_x] = 12  # shore-top-tip-left
            elif (self.is_within_bounds(map_x - 1, map_y) and self.map[map_y][map_x - 1] in [2, 3] and  # Left is water
                  self.is_within_bounds(map_x, map_y + 1) and self.map[map_y + 1][map_x] in [2, 3] and  # Below is water
                  self.is_within_bounds(map_x + 1, map_y - 1) and self.map[map_y - 1][map_x + 1] in [0, 1]):  # Up-right is grass
                self.map[map_y][map_x] = 13  # shore-top-tip-right
            elif self.is_within_bounds(map_x, map_y + 1) and self.map[map_y + 1][map_x] in [2, 3]:  # Below is water
                return  # Keep as shore-top
        elif tile == 5:  # shore-bottom
            if (self.is_within_bounds(map_x + 1, map_y) and self.map[map_y][map_x + 1] in [2, 3] and  # Right is water
                self.is_within_bounds(map_x, map_y - 1) and self.map[map_y - 1][map_x] in [2, 3] and  # Above is water
                self.is_within_bounds(map_x - 1, map_y + 1) and self.map[map_y + 1][map_x - 1] in [0, 1]):  # Down-left is grass
                self.map[map_y][map_x] = 14  # shore-bottom-tip-left
            elif (self.is_within_bounds(map_x - 1, map_y) and self.map[map_y][map_x - 1] in [2, 3] and  # Left is water
                  self.is_within_bounds(map_x, map_y - 1) and self.map[map_y - 1][map_x] in [2, 3] and  # Above is water
                  self.is_within_bounds(map_x + 1, map_y + 1) and self.map[map_y + 1][map_x + 1] in [0, 1]):  # Down-right is grass
                self.map[map_y][map_x] = 15  # shore-bottom-tip-right
            elif self.is_within_bounds(map_x, map_y - 1) and self.map[map_y - 1][map_x] in [2, 3]:  # Above is water
                return  # Keep as shore-bottom
        elif tile == 6:  # shore-left
            if (self.is_within_bounds(map_x + 1, map_y) and self.map[map_y][map_x + 1] in [2, 3] and  # Right is water
                self.is_within_bounds(map_x, map_y + 1) and self.map[map_y + 1][map_x] in [2, 3] and  # Below is water
                self.is_within_bounds(map_x - 1, map_y - 1) and self.map[map_y - 1][map_x - 1] in [0, 1]):  # Up-left is grass
                self.map[map_y][map_x] = 12  # shore-top-tip-left
            elif self.is_within_bounds(map_x + 1, map_y) and self.map[map_y][map_x + 1] in [2, 3]:  # Right is water
                return  # Keep as shore-left
        elif tile == 7:  # shore-right
            if (self.is_within_bounds(map_x, map_y - 1) and self.map[map_y - 1][map_x] in [2, 3] and  # Above is water
                self.is_within_bounds(map_x - 1, map_y) and self.map[map_y][map_x - 1] in [2, 3] and  # Left is water
                self.is_within_bounds(map_x + 1, map_y + 1) and self.map[map_y + 1][map_x + 1] in [0, 1]):  # Down-right is grass
                self.map[map_y][map_x] = 15  # shore-bottom-tip-right
            elif self.is_within_bounds(map_x - 1, map_y) and self.map[map_y][map_x - 1] in [2, 3]:  # Left is water
                return  # Keep as shore-right
        elif tile == 10:  # shore-bottom-left
            if (self.is_within_bounds(map_x + 1, map_y) and self.map[map_y][map_x + 1] in [2, 3] and  # Right is water
                self.is_within_bounds(map_x, map_y - 1) and self.map[map_y - 1][map_x] in [2, 3] and  # Above is water
                self.is_within_bounds(map_x + 1, map_y + 1) and self.map[map_y + 1][map_x + 1] in [0, 1]):  # Down-right is grass
                self.map[map_y][map_x] = 15  # shore-bottom-tip-right
            elif self.is_within_bounds(map_x, map_y - 1) and self.map[map_y - 1][map_x] in [2, 3]:  # Above is water
                return  # Keep as shore-bottom-left
        elif tile == 8:  # shore-top-left
            if self.is_within_bounds(map_x, map_y + 1) and self.map[map_y + 1][map_x] in [2, 3]:  # Below is water
                self.map[map_y][map_x] = 4  # Change to shore-top
            elif self.is_within_bounds(map_x + 1, map_y) and self.map[map_y][map_x + 1] in [2, 3]:  # Right is water
                self.map[map_y][map_x] = 6  # Change to shore-left
        elif tile == 9:  # shore-top-right
            if self.is_within_bounds(map_x, map_y + 1) and self.map[map_y + 1][map_x] in [2, 3]:  # Below is water
                self.map[map_y][map_x] = 4  # Change to shore-top
            elif self.is_within_bounds(map_x - 1, map_y) and self.map[map_y][map_x - 1] in [2, 3]:  # Left is water
                self.map[map_y][map_x] = 7  # Change to shore-right
        elif tile == 11:  # shore-bottom-right
            if self.is_within_bounds(map_x, map_y - 1) and self.map[map_y - 1][map_x] in [2, 3]:  # Above is water
                self.map[map_y][map_x] = 5  # Change to shore-bottom
            elif self.is_within_bounds(map_x - 1, map_y) and self.map[map_y][map_x - 1] in [2, 3]:  # Left is water
                self.map[map_y][map_x] = 7  # Change to shore-right

    def is_within_bounds(self, x, y):
        return 0 <= x < self.map_width and 0 <= y < self.map_height

    def update_tile(self, map_x, map_y):
        current_tile = self.map[map_y][map_x]
        
        # If water, ensure surrounded by valid shores
        if current_tile in [2, 3]:
            self.ensure_water_surrounded(map_x, map_y)
        
        # If shore, validate it
        elif current_tile in [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]:
            if not self.is_valid_shore(map_x, map_y, current_tile):
                self.map[map_y][map_x] = 2  # Convert to water
                self.ensure_water_surrounded(map_x, map_y)

    def is_valid_shore(self, map_x, map_y, shore_type):
        # Validate shore based on required grass neighbor(s)
        if shore_type == 4:  # shore-top
            return self.has_grass(map_x, map_y - 1)
        elif shore_type == 5:  # shore-bottom
            return self.has_grass(map_x, map_y + 1)
        elif shore_type == 6:  # shore-left
            return self.has_grass(map_x - 1, map_y)
        elif shore_type == 7:  # shore-right
            return self.has_grass(map_x + 1, map_y)
        elif shore_type == 8:  # shore-top-left
            return self.has_grass(map_x - 1, map_y) and self.has_grass(map_x, map_y - 1)
        elif shore_type == 9:  # shore-top-right
            return self.has_grass(map_x + 1, map_y) and self.has_grass(map_x, map_y - 1)
        elif shore_type == 10:  # shore-bottom-left
            return self.has_grass(map_x - 1, map_y) and self.has_grass(map_x, map_y + 1)
        elif shore_type == 11:  # shore-bottom-right
            return self.has_grass(map_x + 1, map_y) and self.has_grass(map_x, map_y + 1)
        elif shore_type == 12:  # shore-top-tip-left
            return (self.is_within_bounds(map_x, map_y - 1) and self.map[map_y - 1][map_x] == 8 and
                    self.is_within_bounds(map_x - 1, map_y - 1) and self.map[map_y - 1][map_x - 1] == 8)
        elif shore_type == 13:  # shore-top-tip-right
            return (self.is_within_bounds(map_x, map_y - 1) and self.map[map_y - 1][map_x] == 9 and
                    self.is_within_bounds(map_x + 1, map_y - 1) and self.map[map_y - 1][map_x + 1] == 9)
        elif shore_type == 14:  # shore-bottom-tip-left
            return (self.is_within_bounds(map_x, map_y + 1) and self.map[map_y + 1][map_x] == 10 and
                    self.is_within_bounds(map_x - 1, map_y + 1) and self.map[map_y + 1][map_x - 1] == 10)
        elif shore_type == 15:  # shore-bottom-tip-right
            return (self.is_within_bounds(map_x, map_y + 1) and self.map[map_y + 1][map_x] == 11 and
                    self.is_within_bounds(map_x + 1, map_y + 1) and self.map[map_y + 1][map_x + 1] == 11)
        return False
    
    def has_grass(self, x, y):
        if not (0 <= x < self.map_width and 0 <= y < self.map_height):
            return False
        return self.map[y][x] in [0, 1]
    
    # --- Update Loop (Placeholder) ---
    def update(self):
        pass  # Placeholder for future logic
    
    # --- File Operations ---
    def save_map(self):
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Map As"
        )
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(f"{self.map_width} {self.map_height}\n")
                    for row in self.map:
                        formatted_row = "".join(f"[{str(tile).zfill(5)}]" for tile in row)
                        f.write(formatted_row + "\n")
                print(f"Map saved to {file_path}")
            except Exception as e:
                print(f"Error saving map: {e}")
        root.destroy()

    def load_map(self):
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Load Map"
        )
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    lines = [line.rstrip() for line in f.readlines() if line.strip()]  # Remove empty lines and trailing whitespace
                    if not lines or len(lines) < 2:
                        print("Error: File is empty or missing data.")
                        return
                    # Parse dimensions
                    width, height = map(int, lines[0].split())
                    print(f"Loading map with dimensions: {width}x{height}")
                    if width != self.map_width or height != self.map_height:
                        print(f"Warning: File dimensions ({width}x{height}) do not match editor dimensions ({self.map_width}x{self.map_height}). Loading may fail.")
                        return
                    self.map = []
                    for i, line in enumerate(lines[1:], 1):
                        if not line:
                            print(f"Warning: Skipping empty line at row {i}")
                            continue
                        expected_length = width * 7
                        print(f"Processing row {i}, raw line: '{line}'")  # Debug: Print raw line
                        if len(line) != expected_length:
                            print(f"Error: Row {i} length {len(line)} does not match expected {expected_length} characters. Trimming or padding.")
                            if len(line) > expected_length:
                                line = line[:expected_length]  # Trim excess
                            else:
                                padding_needed = (expected_length - len(line)) // 7
                                line += "[00000]" * padding_needed  # Pad with grass
                        row = []
                        for j in range(0, len(line), 7):
                            tile_str = line[j:j + 7]
                            print(f"Extracted tile string at col {j}: '{tile_str}'")  # Debug: Print extracted tile string
                            if (len(tile_str) != 7 or tile_str[0] != '[' or tile_str[6] != ']' or
                                not tile_str[1:6].isdigit() or int(tile_str[1:6]) > 15):
                                print(f"Error: Invalid tile format '{tile_str}' at row {i}, col {j // 7}. Defaulting to [00000].")
                                row.append(0)  # Default to grass on error
                            else:
                                tile = int(tile_str[1:6])
                                row.append(tile)
                                print(f"Loaded tile at ({j // 7}, {i-1}): {tile}")
                        if len(row) != width:
                            print(f"Warning: Row {i} has {len(row)} tiles, expected {width}. Padding with [00000].")
                            row.extend([0] * (width - len(row)))
                        self.map.append(row)
                    # Ensure correct number of rows
                    while len(self.map) < height:
                        print(f"Warning: Fewer rows ({len(self.map)}) than expected ({height}). Padding with [00000] rows.")
                        self.map.append([0] * width)
                    self.map = self.map[:height]  # Truncate if too many rows
                    print(f"Map loaded with {len(self.map)} rows.")
                    # Remove automatic validation after loading
                    # for y in range(self.map_height):
                    #     for x in range(self.map_width):
                    #         self.update_tile(x, y)
            except Exception as e:
                print(f"Error loading map: {e}")
        root.destroy()

    # --- Exit Function ---
    def exit_editor(self):
        print("Exiting editor...")
        pygame.quit()
        sys.exit()

# --- Main Execution ---
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    pygame.display.set_caption("Map Editor")
    editor = Editor(screen)
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            editor.handle_events(event)
        editor.update()
        editor.render()
        pygame.display.flip()
        clock.tick(60)