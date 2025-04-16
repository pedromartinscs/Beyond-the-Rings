import pygame
import sys
import tkinter as tk
from tkinter import filedialog
import random
from object_collection import ObjectCollection

# Main class for the map editor
class Editor:
    # --- Initialization ---
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = screen.get_width() - 30      # Screen width with padding
        self.screen_height = screen.get_height() - 10    # Screen height with padding
        
        # Tile and map setup
        self.tile_size = 32                              # Size of each tile (32x32 pixels)
        self.map_width = 100                             # Map width in tiles
        self.map_height = 100                            # Map height in tiles
        self.selected_tile = 0                           # Index of currently selected tile (default: 0)
        
        # Object setup
        self.objects = []  # List to store placed objects
        self.object_collection = ObjectCollection()
        self.selected_object = None
        self.selected_object_type = "Trees"  # Default object type
        
        # Load and scale tile images (4 selectable + transition tiles)
        self.tile_images = []                            # List to store tile images
        # Selectable tiles (0-5)
        grass1 = pygame.image.load("Maps/Common/Tiles/00000.png")  # Grass tile 1
        grass1 = pygame.transform.scale(grass1, (self.tile_size, self.tile_size))
        self.tile_images.append(grass1)
        grass2 = pygame.image.load("Maps/Common/Tiles/00001.png")  # Grass tile 2
        grass2 = pygame.transform.scale(grass2, (self.tile_size, self.tile_size))
        self.tile_images.append(grass2)
        grass3 = pygame.image.load("Maps/Common/Tiles/00002.png")  # Grass tile 3
        grass3 = pygame.transform.scale(grass3, (self.tile_size, self.tile_size))
        self.tile_images.append(grass3)
        grass4 = pygame.image.load("Maps/Common/Tiles/00003.png")  # Grass tile 4
        grass4 = pygame.transform.scale(grass4, (self.tile_size, self.tile_size))
        self.tile_images.append(grass4)
        water1 = pygame.image.load("Maps/Common/Tiles/00004.png")  # Water tile 1
        water1 = pygame.transform.scale(water1, (self.tile_size, self.tile_size))
        self.tile_images.append(water1)
        water2 = pygame.image.load("Maps/Common/Tiles/00005.png")  # Water tile 2
        water2 = pygame.transform.scale(water2, (self.tile_size, self.tile_size))
        self.tile_images.append(water2)
        
        # Transition tiles (6-19, not selectable)
        shore_top = pygame.image.load("Maps/Common/Tiles/00006.png")
        shore_top = pygame.transform.scale(shore_top, (self.tile_size, self.tile_size))
        self.tile_images.append(shore_top)
        shore_bottom = pygame.image.load("Maps/Common/Tiles/00007.png")
        shore_bottom = pygame.transform.scale(shore_bottom, (self.tile_size, self.tile_size))
        self.tile_images.append(shore_bottom)
        shore_left = pygame.image.load("Maps/Common/Tiles/00008.png")
        shore_left = pygame.transform.scale(shore_left, (self.tile_size, self.tile_size))
        self.tile_images.append(shore_left)
        shore_right = pygame.image.load("Maps/Common/Tiles/00009.png")
        shore_right = pygame.transform.scale(shore_right, (self.tile_size, self.tile_size))
        self.tile_images.append(shore_right)
        shore_topleft = pygame.image.load("Maps/Common/Tiles/00010.png")
        shore_topleft = pygame.transform.scale(shore_topleft, (self.tile_size, self.tile_size))
        self.tile_images.append(shore_topleft)
        shore_topright = pygame.image.load("Maps/Common/Tiles/00011.png")
        shore_topright = pygame.transform.scale(shore_topright, (self.tile_size, self.tile_size))
        self.tile_images.append(shore_topright)
        shore_bottomleft = pygame.image.load("Maps/Common/Tiles/00012.png")
        shore_bottomleft = pygame.transform.scale(shore_bottomleft, (self.tile_size, self.tile_size))
        self.tile_images.append(shore_bottomleft)
        shore_bottomright = pygame.image.load("Maps/Common/Tiles/00013.png")
        shore_bottomright = pygame.transform.scale(shore_bottomright, (self.tile_size, self.tile_size))
        self.tile_images.append(shore_bottomright)
        shore_top_tip_left = pygame.image.load("Maps/Common/Tiles/00014.png")
        shore_top_tip_left = pygame.transform.scale(shore_top_tip_left, (self.tile_size, self.tile_size))
        self.tile_images.append(shore_top_tip_left)
        shore_top_tip_right = pygame.image.load("Maps/Common/Tiles/00015.png")
        shore_top_tip_right = pygame.transform.scale(shore_top_tip_right, (self.tile_size, self.tile_size))
        self.tile_images.append(shore_top_tip_right)
        shore_bottom_tip_left = pygame.image.load("Maps/Common/Tiles/00016.png")
        shore_bottom_tip_left = pygame.transform.scale(shore_bottom_tip_left, (self.tile_size, self.tile_size))
        self.tile_images.append(shore_bottom_tip_left)
        shore_bottom_tip_right = pygame.image.load("Maps/Common/Tiles/00017.png")
        shore_bottom_tip_right = pygame.transform.scale(shore_bottom_tip_right, (self.tile_size, self.tile_size))
        self.tile_images.append(shore_bottom_tip_right)
        shore_double_tip_left_top = pygame.image.load("Maps/Common/Tiles/00018.png")
        shore_double_tip_left_top = pygame.transform.scale(shore_double_tip_left_top, (self.tile_size, self.tile_size))
        self.tile_images.append(shore_double_tip_left_top)
        shore_double_tip_right_top = pygame.image.load("Maps/Common/Tiles/00019.png")
        shore_double_tip_right_top = pygame.transform.scale(shore_double_tip_right_top, (self.tile_size, self.tile_size))
        self.tile_images.append(shore_double_tip_right_top)
        
        # Tile palette setup
        self.palette_width = 150
        self.palette_offset_x = 40
        self.tiles_per_page = 8  # 2x4 grid
        self.current_page = 0
        self.total_pages = 1  # Only one page since we're only showing 6 tiles
        self.selectable_tiles = 6  # Number of tiles that can be selected (4 grass + 2 water)
        
        # Object palette setup
        self.object_palette_width = 150
        self.object_palette_offset_x = 40
        self.objects_per_page = 8  # 2x4 grid for small objects
        self.current_object_page = 0
        self.showing_large_objects = False  # Track if we're showing large objects
        
        # Initialize map as a 2D array filled with grass (tile 0)
        self.map = [[0 for _ in range(self.map_width)] for _ in range(self.map_height)]
        
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
            self.screen_height - 80,
            100, 30
        )
        self.save_button_rect = pygame.Rect(
            self.screen_width - self.palette_width + self.palette_offset_x,
            self.screen_height - 120,
            100, 30
        )
        self.load_button_rect = pygame.Rect(
            self.screen_width - self.palette_width + self.palette_offset_x,
            self.screen_height - 160,
            100, 30
        )
        
        # Random map generation buttons
        self.rnd_grass_button_rect = pygame.Rect(
            self.screen_width - self.palette_width + self.palette_offset_x,
            self.screen_height - 240,
            100, 30
        )
        self.rnd_water_button_rect = pygame.Rect(
            self.screen_width - self.palette_width + self.palette_offset_x,
            self.screen_height - 200,
            100, 30
        )
        self.rnd_map_button_rect = pygame.Rect(
            self.screen_width - self.palette_width + self.palette_offset_x,
            self.screen_height - 280,
            100, 30
        )
        
        # Navigation buttons
        self.prev_button_rect = pygame.Rect(
            self.screen_width - self.palette_width + self.palette_offset_x - 30,
            10 + (self.tile_size * 2),  # Center vertically with the grid
            30, 30
        )
        self.next_button_rect = pygame.Rect(
            self.screen_width - self.palette_width + self.palette_offset_x + (self.tile_size * 2) + 10,
            10 + (self.tile_size * 2),  # Center vertically with the grid
            30, 30
        )
        
        # Object navigation buttons
        self.object_prev_button_rect = pygame.Rect(
            self.screen_width - self.object_palette_width + self.object_palette_offset_x - 30,
            10 + (self.tile_size * 4) + 20,  # Below the tile palette
            30, 30
        )
        self.object_next_button_rect = pygame.Rect(
            self.screen_width - self.object_palette_width + self.object_palette_offset_x + (self.tile_size * 2) + 10,
            10 + (self.tile_size * 4) + 20,  # Below the tile palette
            30, 30
        )
        
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)  # Set default cursor to arrow
    
    # --- Rendering ---
    def render(self):
        self.screen.fill((30, 30, 30))                   # Dark gray background
        
        # Initialize font
        font = pygame.font.Font(None, 36)
        
        # Define map area (grid on left side)
        map_margin_right = 10
        map_margin_bottom = 16  # Space for instructions and padding
        map_area_width = self.screen_width - self.palette_width - map_margin_right
        map_area_height = self.screen_height - map_margin_bottom
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
        
        # Render objects (sorted by z-index)
        for obj in sorted(self.objects, key=lambda x: x['z_index']):
            obj_x = obj['x'] * self.tile_size - self.camera_x
            obj_y = obj['y'] * self.tile_size - self.camera_y
            
            if -self.tile_size <= obj_x <= map_area_width and -self.tile_size <= obj_y <= map_area_height:
                object_data = self.object_collection.get_object(obj['type'], obj['id'])
                if object_data:
                    map_surface.blit(object_data['image'], (obj_x, obj_y))
        
        # Render tile palette (2x4 grid) - only show first 6 tiles
        palette_x = self.screen_width - self.palette_width + self.palette_offset_x
        palette_y = 10
        
        # Draw tiles in 2x4 grid (only first 6 tiles)
        for i in range(self.selectable_tiles):
            row = i // 2
            col = i % 2
            rect = pygame.Rect(
                palette_x + (col * self.tile_size),
                palette_y + (row * self.tile_size),
                self.tile_size,
                self.tile_size
            )
            self.screen.blit(self.tile_images[i], rect.topleft)
            if i == self.selected_tile:
                pygame.draw.rect(self.screen, (255, 255, 0), rect, 3)
        
        # Draw navigation buttons
        # Show left arrow only if not on first page
        if self.current_page > 0:
            pygame.draw.rect(self.screen, (100, 100, 100), self.prev_button_rect)
            prev_text = font.render("<", True, (255, 255, 255))
            self.screen.blit(prev_text, (self.prev_button_rect.x + 8, self.prev_button_rect.y + 2))
        
        # Show right arrow if there are more tiles to show
        total_pages = (self.selectable_tiles + self.tiles_per_page - 1) // self.tiles_per_page
        if self.current_page < total_pages - 1:
            pygame.draw.rect(self.screen, (100, 100, 100), self.next_button_rect)
            next_text = font.render(">", True, (255, 255, 255))
            self.screen.blit(next_text, (self.next_button_rect.x + 8, self.next_button_rect.y + 2))
        
        # Render object palette
        object_palette_y = palette_y + (self.tile_size * 4) + 10
        
        # Get objects based on current view
        if self.showing_large_objects:
            objects = self.object_collection.get_objects_by_type(self.selected_object_type, 'large')
            objects_per_page = 2  # Only 2 large objects per page
        else:
            objects = self.object_collection.get_objects_by_type(self.selected_object_type, 'small')
            objects_per_page = self.objects_per_page
        
        # Calculate start and end indices for current page
        start_idx = self.current_object_page * objects_per_page
        end_idx = min(start_idx + objects_per_page, len(objects))
        
        # Draw objects in grid
        for i in range(start_idx, end_idx):
            obj = objects[i]
            if self.showing_large_objects:
                # For large objects, use 2x2 grid
                row = (i - start_idx) // 1  # Only one column for large objects
                col = 0
                rect = pygame.Rect(
                    palette_x,
                    object_palette_y + (row * self.tile_size * 2),
                    self.tile_size * 2,
                    self.tile_size * 2
                )
            else:
                # For small objects, use 2x4 grid
                row = (i - start_idx) // 2
                col = (i - start_idx) % 2
                rect = pygame.Rect(
                    palette_x + (col * self.tile_size),
                    object_palette_y + (row * self.tile_size),
                    self.tile_size,
                    self.tile_size
                )
            
            # Draw the object
            self.screen.blit(obj['image'], rect.topleft)
            
            # Draw selection highlight
            if self.selected_object and obj['id'] == self.selected_object['id']:
                pygame.draw.rect(self.screen, (255, 255, 0), rect, 3)
        
        # Draw object navigation buttons
        # Show left arrow only if not on first page or if showing large objects
        if self.current_object_page > 0 or self.showing_large_objects:
            pygame.draw.rect(self.screen, (100, 100, 100), self.object_prev_button_rect)
            prev_text = font.render("<", True, (255, 255, 255))
            self.screen.blit(prev_text, (self.object_prev_button_rect.x + 8, self.object_prev_button_rect.y + 2))
        
        # Show right arrow if there are more objects to show
        total_pages = (len(objects) + objects_per_page - 1) // objects_per_page
        if self.current_object_page < total_pages - 1 or (
            not self.showing_large_objects and 
            self.object_collection.get_total_objects('large') > 0
        ):
            pygame.draw.rect(self.screen, (100, 100, 100), self.object_next_button_rect)
            next_text = font.render(">", True, (255, 255, 255))
            self.screen.blit(next_text, (self.object_next_button_rect.x + 8, self.object_next_button_rect.y + 2))
        
        # Draw palette buttons
        pygame.draw.rect(self.screen, (200, 0, 0), self.exit_button_rect)
        pygame.draw.rect(self.screen, (0, 200, 0), self.save_button_rect)
        pygame.draw.rect(self.screen, (0, 0, 200), self.load_button_rect)
        
        # Draw random map generation buttons
        pygame.draw.rect(self.screen, (0, 0, 0), self.rnd_grass_button_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), self.rnd_water_button_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), self.rnd_map_button_rect)
        
        # Render button text
        font = pygame.font.Font(None, 24)
        exit_text = font.render("Exit", True, (255, 255, 255))
        save_text = font.render("Save Map", True, (255, 255, 255))
        load_text = font.render("Load Map", True, (255, 255, 255))
        rnd_grass_text = font.render("Rnd grass", True, (255, 255, 255))
        rnd_water_text = font.render("Rnd water", True, (255, 255, 255))
        rnd_map_text = font.render("Rnd map", True, (255, 255, 255))
        
        self.screen.blit(exit_text, (self.exit_button_rect.x + 5, self.exit_button_rect.y + 5))
        self.screen.blit(save_text, (self.save_button_rect.x + 5, self.save_button_rect.y + 5))
        self.screen.blit(load_text, (self.load_button_rect.x + 5, self.load_button_rect.y + 5))
        self.screen.blit(rnd_grass_text, (self.rnd_grass_button_rect.x + 5, self.rnd_grass_button_rect.y + 5))
        self.screen.blit(rnd_water_text, (self.rnd_water_button_rect.x + 5, self.rnd_water_button_rect.y + 5))
        self.screen.blit(rnd_map_text, (self.rnd_map_button_rect.x + 5, self.rnd_map_button_rect.y + 5))
        
        # Display instructions at the bottom of the screen
        instructions = "Left click: place tile/object; Right click: drag map; Middle click: remove object; Click palette to select tile/object."
        inst_text = font.render(instructions, True, (255, 255, 255))
        instruction_padding = 11  # Space from bottom of screen
        self.screen.blit(inst_text, (10, self.screen_height - instruction_padding))
    
    # --- Event Handling ---
    def handle_events(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # Define clickable palette areas
        palette_buttons = [self.exit_button_rect, self.save_button_rect, self.load_button_rect, 
                         self.prev_button_rect, self.next_button_rect,
                         self.rnd_grass_button_rect, self.rnd_water_button_rect, self.rnd_map_button_rect,
                         self.object_prev_button_rect, self.object_next_button_rect]
        
        # Mouse hover cursor change
        if event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
            over_button = False
            
            # Get objects based on current view
            if self.showing_large_objects:
                objects = self.object_collection.get_objects_by_type(self.selected_object_type, 'large')
                objects_per_page = 2  # Only 2 large objects per page
            else:
                objects = self.object_collection.get_objects_by_type(self.selected_object_type, 'small')
                objects_per_page = self.objects_per_page
            
            # Check regular buttons
            for rect in [self.exit_button_rect, self.save_button_rect, self.load_button_rect,
                        self.rnd_grass_button_rect, self.rnd_water_button_rect, self.rnd_map_button_rect]:
                if rect.collidepoint(mouse_x, mouse_y):
                    over_button = True
                    break
            
            # Check tile navigation buttons only if they're visible
            if not over_button:
                if self.current_page > 0 and self.prev_button_rect.collidepoint(mouse_x, mouse_y):
                    over_button = True
                elif self.current_page < ((self.selectable_tiles + self.tiles_per_page - 1) // self.tiles_per_page - 1) and self.next_button_rect.collidepoint(mouse_x, mouse_y):
                    over_button = True
            
            # Check object navigation buttons only if they're visible
            if not over_button:
                if (self.current_object_page > 0 or self.showing_large_objects) and self.object_prev_button_rect.collidepoint(mouse_x, mouse_y):
                    over_button = True
                elif self.object_next_button_rect.collidepoint(mouse_x, mouse_y):
                    total_pages = (len(objects) + objects_per_page - 1) // objects_per_page
                    if self.current_object_page < total_pages - 1 or (
                        not self.showing_large_objects and 
                        self.object_collection.get_total_objects('large') > 0
                    ):
                        over_button = True
            
            if over_button:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        
        # Mouse button press
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_x, mouse_y = event.pos
                if mouse_x >= self.screen_width - self.palette_width:  # Palette area
                    # Check navigation buttons
                    if self.prev_button_rect.collidepoint(event.pos):
                        if self.current_page > 0:
                            self.current_page -= 1
                    elif self.next_button_rect.collidepoint(event.pos):
                        total_pages = (self.selectable_tiles + self.tiles_per_page - 1) // self.tiles_per_page
                        if self.current_page < total_pages - 1:
                            self.current_page += 1
                    
                    # Handle object navigation buttons
                    if self.object_prev_button_rect.collidepoint(event.pos):
                        if self.showing_large_objects:
                            # If we're showing large objects and on first page, switch to small objects
                            if self.current_object_page == 0:
                                self.showing_large_objects = False
                                small_objects = self.object_collection.get_objects_by_type(self.selected_object_type, 'small')
                                self.current_object_page = (len(small_objects) + self.objects_per_page - 1) // self.objects_per_page - 1
                            else:
                                self.current_object_page -= 1
                        else:
                            if self.current_object_page > 0:
                                self.current_object_page -= 1
                    elif self.object_next_button_rect.collidepoint(event.pos):
                        if self.showing_large_objects:
                            large_objects = self.object_collection.get_objects_by_type(self.selected_object_type, 'large')
                            total_large_pages = (len(large_objects) + 1) // 2  # 2 objects per page
                            if self.current_object_page < total_large_pages - 1:
                                self.current_object_page += 1
                        else:
                            small_objects = self.object_collection.get_objects_by_type(self.selected_object_type, 'small')
                            total_small_pages = (len(small_objects) + self.objects_per_page - 1) // self.objects_per_page
                            if self.current_object_page < total_small_pages - 1:
                                self.current_object_page += 1
                            elif self.object_collection.get_total_objects('large') > 0:
                                # Switch to large objects if we have any
                                self.showing_large_objects = True
                                self.current_object_page = 0
                    
                    # Handle object selection
                    object_palette_y = 10 + (self.tile_size * 4) + 10
                    if self.showing_large_objects:
                        objects = self.object_collection.get_objects_by_type(self.selected_object_type, 'large')
                        objects_per_page = 2
                    else:
                        objects = self.object_collection.get_objects_by_type(self.selected_object_type, 'small')
                        objects_per_page = self.objects_per_page
                    
                    start_idx = self.current_object_page * objects_per_page
                    end_idx = min(start_idx + objects_per_page, len(objects))
                    
                    for i in range(start_idx, end_idx):
                        obj = objects[i]
                        if self.showing_large_objects:
                            row = (i - start_idx) // 1
                            rect = pygame.Rect(
                                self.screen_width - self.object_palette_width + self.object_palette_offset_x,
                                object_palette_y + (row * self.tile_size * 2),
                                self.tile_size * 2,
                                self.tile_size * 2
                            )
                        else:
                            row = (i - start_idx) // 2
                            col = (i - start_idx) % 2
                            rect = pygame.Rect(
                                self.screen_width - self.object_palette_width + self.object_palette_offset_x + (col * self.tile_size),
                                object_palette_y + (row * self.tile_size),
                                self.tile_size,
                                self.tile_size
                            )
                        
                        if rect.collidepoint(event.pos):
                            self.selected_object = obj
                            self.selected_tile = None  # Deselect tile when selecting an object
                            break
                    
                    # Check other buttons
                    if self.exit_button_rect.collidepoint(event.pos):
                        self.exit_editor()
                    elif self.save_button_rect.collidepoint(event.pos):
                        self.save_map()
                    elif self.load_button_rect.collidepoint(event.pos):
                        self.load_map()
                    elif self.rnd_grass_button_rect.collidepoint(event.pos):
                        self.randomize_grass_tiles()
                    elif self.rnd_water_button_rect.collidepoint(event.pos):
                        self.randomize_water_tiles()
                    elif self.rnd_map_button_rect.collidepoint(event.pos):
                        self.randomize_map()
                    else:
                        # Check if a tile was clicked
                        palette_x = self.screen_width - self.palette_width + self.palette_offset_x
                        palette_y = 10
                        
                        for i in range(self.selectable_tiles):
                            row = i // 2
                            col = i % 2
                            rect = pygame.Rect(
                                palette_x + (col * self.tile_size),
                                palette_y + (row * self.tile_size),
                                self.tile_size,
                                self.tile_size
                            )
                            if rect.collidepoint(event.pos):
                                self.selected_tile = i
                                self.selected_object = None  # Deselect object when selecting a tile
                                break
                else:  # Map area
                    map_x = (mouse_x + self.camera_x) // self.tile_size
                    map_y = (mouse_y + self.camera_y) // self.tile_size
                    if 0 <= map_x < self.map_width and 0 <= map_y < self.map_height:
                        if self.selected_object:
                            # Check if the position is valid before placing the object
                            if self.is_valid_object_position(map_x, map_y):
                                # Place object
                                self.objects.append({
                                    'x': map_x,
                                    'y': map_y,
                                    'type': self.selected_object_type,
                                    'id': self.selected_object['id'],
                                    'health': 500 if self.selected_object_type == "Trees" else 0,
                                    'z_index': 1 if self.selected_object_type == "Trees" else 0
                                })
                            else:
                                print("Cannot place objects on water or shore tiles!")
                        else:
                            self.place_tile(map_x, map_y)
            elif event.button == 3:  # Right click (drag start)
                self.dragging = True
                self.last_mouse_pos = event.pos
            elif event.button == 2:  # Middle click to remove object
                mouse_x, mouse_y = event.pos
                map_x = (mouse_x + self.camera_x) // self.tile_size
                map_y = (mouse_y + self.camera_y) // self.tile_size
                # Remove object at this position
                self.objects = [obj for obj in self.objects if not (obj['x'] == map_x and obj['y'] == map_y)]
        
        # Mouse button release
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 3:
                self.dragging = False
                self.last_mouse_pos = None
        
        # Mouse movement (dragging or painting)
        if event.type == pygame.MOUSEMOTION:
            if hasattr(self, 'dragging') and self.dragging:
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
    def check_and_remove_objects(self, map_x, map_y):
        """Check and remove objects that are on water or shore tiles.
        Only removes objects with z-index 0 or 1 (floor level or just above)."""
        # Get all objects at this position
        objects_to_remove = []
        for obj in self.objects:
            if obj['x'] == map_x and obj['y'] == map_y:
                # Check if the object is at floor level (z-index 0 or 1)
                if obj['z_index'] in [0, 1]:
                    # Check if the tile is water or shore
                    tile = self.map[map_y][map_x]
                    if tile in [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]:
                        objects_to_remove.append(obj)
        
        # Remove the objects
        for obj in objects_to_remove:
            self.objects.remove(obj)
        
        return len(objects_to_remove) > 0  # Return True if any objects were removed

    def place_tile(self, map_x, map_y):
        # Check if placing grass would isolate it
        if self.selected_tile in [0, 1, 2, 3]:
            if self.is_isolated_grass(map_x, map_y):
                return  # Don't place grass if it would be surrounded
        
        # Place the selected tile
        old_tile = self.map[map_y][map_x]
        self.map[map_y][map_x] = self.selected_tile
        
        # If we're placing water or shore tiles, check and remove any objects
        if self.selected_tile in [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]:
            self.check_and_remove_objects(map_x, map_y)
        
        # Update the surrounding area if the tile type changed (water or grass placement)
        if old_tile != self.selected_tile:
            self.update_map_area(map_x, map_y)
            
            # After updating the area, check and remove objects from any new water/shore tiles
            for y in range(max(0, map_y - 2), min(self.map_height, map_y + 3)):
                for x in range(max(0, map_x - 2), min(self.map_width, map_x + 3)):
                    if self.map[y][x] in [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]:
                        self.check_and_remove_objects(x, y)
    
    def is_isolated_grass(self, map_x, map_y):
        # Check if placing grass here would surround it with water or shore
        directions = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        all_surrounded = True
        for dx, dy in directions:
            new_x, new_y = map_x + dx, map_y + dy
            if 0 <= new_x < self.map_width and 0 <= new_y < self.map_height:
                tile = self.map[new_y][new_x]
                if tile in [0, 1, 2, 3]:  # Grass neighbor
                    all_surrounded = False
            else:
                all_surrounded = False  # Edge counts as accessible
        return all_surrounded

    def update_map_area(self, map_x, map_y):
        # Find all connected water tiles and ensure they are surrounded by shores
        water_tiles = self.find_water_region(map_x, map_y)
        for water_x, water_y in water_tiles:
            self.ensure_water_surrounded_by_shore(water_x, water_y)
        # Refine shore tiles in the affected area with multiple passes
        for _ in range(2):  # Two passes to ensure convergence
            for y in range(max(0, map_y - 2), min(self.map_height, map_y + 3)):
                for x in range(max(0, map_x - 2), min(self.map_width, map_x + 3)):
                    if self.map[y][x] in [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]:
                        self.correct_shore_tile(x, y)

    def find_water_region(self, map_x, map_y):
        # Use flood fill to identify all connected water tiles
        if self.map[map_y][map_x] not in [4, 5]:
            return set()  # Only process if the starting tile is water
        water_set = set()
        stack = [(map_x, map_y)]
        while stack:
            x, y = stack.pop()
            if (x, y) in water_set or not (0 <= x < self.map_width and 0 <= y < self.map_height):
                continue
            if self.map[y][x] in [4, 5]:  # Water tile
                water_set.add((x, y))
                # Check adjacent tiles
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, -1), (1, 1), (-1, -1), (-1, 1)]:  # Cardinal directions
                    stack.append((x + dx, y + dy))
        return water_set

    def ensure_water_surrounded_by_shore(self, map_x, map_y):
        # Determine appropriate shore tiles based on adjacent tiles and water body perimeter
        directions = [
            (0, -1, 6), (0, 1, 7), (-1, 0, 8), (1, 0, 9),  # Straight shores
            (-1, -1, 10), (1, -1, 11), (-1, 1, 12), (1, 1, 13)  # Corners
        ]
        if self.map[map_y][map_x] not in [4, 5]:
            return  # Only process water tiles
        for dx, dy, shore_index in directions:
            new_x, new_y = map_x + dx, map_y + dy
            if 0 <= new_x < self.map_width and 0 <= new_y < self.map_height:
                neighbor = self.map[new_y][new_x]
                # Place shore if neighbor is grass or if it's the outer edge of the water body
                if neighbor in [0, 1, 2, 3]:  # Grass neighbor
                    self.map[new_y][new_x] = shore_index
                elif neighbor in [2, 3]:  # Adjacent water, check outer boundary
                    opp_dx, opp_dy = -dx, -dy
                    opp_x, opp_y = new_x + opp_dx, new_y + opp_dy
                    if 0 <= opp_x < self.map_width and 0 <= opp_y < self.map_height:
                        if self.map[opp_y][opp_x] in [0, 1, 2, 3]:  # Grass on the outer side
                            self.map[new_x][new_y] = shore_index
                    else:  # Edge of map
                        self.map[new_x][new_y] = shore_index

    def has_adjacent_water(self, map_x, map_y):
        # Check if the tile has adjacent water
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        for dx, dy in directions:
            new_x, new_y = map_x + dx, map_y + dy
            if 0 <= new_x < self.map_width and 0 <= new_y < self.map_height:
                if self.map[new_y][new_x] in [4, 5]:
                    return True
        return False

    def has_adjacent_grass(self, map_x, map_y):
        # Check if the tile has adjacent grass (including diagonals)
        directions = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        for dx, dy in directions:
            new_x, new_y = map_x + dx, map_y + dy
            if 0 <= new_x < self.map_width and 0 <= new_y < self.map_height:
                if self.map[new_y][new_x] in [0, 1, 2, 3]:
                    return True
        return False

    def correct_shore_tile(self, map_x, map_y):
        tile = self.map[map_y][map_x]
        if tile not in [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]:
            return  # Only process shore tiles

        # Check tip conditions with higher priority
        if len(self.get_surrounding_grass(map_x, map_y)) == 0:  # No grass neighbors
            self.map[map_y][map_x] = 4  # Convert to water
        elif (self.is_within_bounds(map_x + 1, map_y) and self.map[map_y][map_x + 1] not in [0, 1, 2, 3] and  # Right is not grass
              self.is_within_bounds(map_x, map_y + 1) and self.map[map_y + 1][map_x] not in [0, 1, 2, 3] and  # Below is not grass
              self.is_within_bounds(map_x, map_y - 1) and self.map[map_y - 1][map_x] not in [0, 1, 2, 3, 4, 5] and  # Above is not grass or water
              self.is_within_bounds(map_x - 1, map_y) and self.map[map_y][map_x - 1] not in [0, 1, 2, 3, 4, 5] and  # Left is not grass or water
              self.is_within_bounds(map_x - 1, map_y - 1) and self.map[map_y - 1][map_x - 1] in [0, 1, 2, 3, 7, 9, 11, 12, 13] and # Top-left is grass or shore with grass
              not (self.is_within_bounds(map_x + 1, map_y + 1) and self.map[map_y + 1][map_x + 1] in [0, 1, 2, 3])): # Bottom-left is not grass
            self.map[map_y][map_x] = 14  # shore-top-tip-left
        elif (self.is_within_bounds(map_x - 1, map_y) and self.map[map_y][map_x - 1] not in [0, 1, 2, 3] and  # Left is not grass
              self.is_within_bounds(map_x, map_y + 1) and self.map[map_y + 1][map_x] not in [0, 1, 2, 3] and  # Below is not grass
              self.is_within_bounds(map_x, map_y - 1) and self.map[map_y - 1][map_x] not in [0, 1, 2, 3, 4, 5] and  # Above is not grass or water
              self.is_within_bounds(map_x + 1, map_y) and self.map[map_y][map_x + 1] not in [0, 1, 2, 3, 4, 5] and  # Right is not grass or water
              self.is_within_bounds(map_x - 1, map_y - 1) and self.map[map_y - 1][map_x + 1] in [0, 1, 2, 3, 7, 8, 10, 12, 13] and # Top-right is grass or shore with grass
              not (self.is_within_bounds(map_x - 1, map_y + 1) and self.map[map_y + 1][map_x - 1] in [0, 1, 2, 3])): # Bottom-left is not grass
            self.map[map_y][map_x] = 15  # shore-top-tip-right
        elif (self.is_within_bounds(map_x + 1, map_y) and self.map[map_y][map_x + 1] not in [0, 1, 2, 3] and  # Right is not grass
              self.is_within_bounds(map_x, map_y - 1) and self.map[map_y - 1][map_x] not in [0, 1, 2, 3] and  # Above is not grass
              self.is_within_bounds(map_x, map_y + 1) and self.map[map_y + 1][map_x] not in [0, 1, 2, 3, 4, 5] and  # Below is not grass or water
              self.is_within_bounds(map_x - 1, map_y) and self.map[map_y][map_x - 1] not in [0, 1, 2, 3, 4, 5] and  # Left is not grass or water
              self.is_within_bounds(map_x - 1, map_y + 1) and self.map[map_y + 1][map_x - 1] in [0, 1, 2, 3, 6, 9, 10, 11, 13] and # Bottom-left is grass or shore with grass
              not (self.is_within_bounds(map_x + 1, map_y - 1) and self.map[map_y - 1][map_x + 1] in [0, 1, 2, 3])):
            self.map[map_y][map_x] = 16  # shore-bottom-tip-left
        elif (self.is_within_bounds(map_x - 1, map_y) and self.map[map_y][map_x - 1] not in [0, 1, 2, 3] and  # Left is not grass
              self.is_within_bounds(map_x, map_y - 1) and self.map[map_y - 1][map_x] not in [0, 1, 2, 3] and  # Above is not grass
              self.is_within_bounds(map_x, map_y + 1) and self.map[map_y + 1][map_x] not in [0, 1, 2, 3, 4, 5] and  # Below is not grass or water
              self.is_within_bounds(map_x + 1, map_y) and self.map[map_y][map_x + 1] not in [0, 1, 2, 3, 4, 5] and  # Right is not grass or water
              self.is_within_bounds(map_x + 1, map_y + 1) and self.map[map_y + 1][map_x + 1] in [0, 1, 2, 3, 6, 8, 10, 11, 12] and # Bottom-right is grass or shore with grass
              not (self.is_within_bounds(map_x - 1, map_y - 1) and self.map[map_y - 1][map_x - 1] in [0, 1, 2, 3])):
            self.map[map_y][map_x] = 17  # shore-bottom-tip-right
        elif (self.is_within_bounds(map_x + 1, map_y - 1) and self.map[map_y - 1][map_x + 1] in [4, 5] and # Top right is water
              self.is_within_bounds(map_x - 1, map_y + 1) and self.map[map_y + 1][map_x - 1] in [4, 5] and # Bottom left is water
              self.is_within_bounds(map_x - 1, map_y - 1) and self.map[map_y - 1][map_x - 1] in [0, 1, 2, 3] and # Top left is grass
              self.is_within_bounds(map_x + 1, map_y + 1) and self.map[map_y + 1][map_x + 1] in [0, 1, 2, 3]): # Bottom right is grass
            self.map[map_y][map_x] = 18 # shore-double-tip-topleft
        elif (self.is_within_bounds(map_x - 1, map_y - 1) and self.map[map_y - 1][map_x - 1] in [4, 5] and # Top left is water
              self.is_within_bounds(map_x + 1, map_y + 1) and self.map[map_y + 1][map_x + 1] in [4, 5] and # Bottom right is water
              self.is_within_bounds(map_x + 1, map_y - 1) and self.map[map_y - 1][map_x + 1] in [0, 1, 2, 3] and # Top right is grass
              self.is_within_bounds(map_x - 1, map_y + 1) and self.map[map_y + 1][map_x - 1] in [0, 1, 2, 3]): # Bottom left is grass
            self.map[map_y][map_x] = 19 # shore-double-tip-topright
        elif (self.is_within_bounds(map_x, map_y + 1) and self.map[map_y + 1][map_x] not in [0, 1, 2, 3] and  # Below is not grass
              self.is_within_bounds(map_x - 1, map_y) and self.map[map_y][map_x - 1] not in [0, 1, 2, 3, 4, 5] and  # Left is not grass or water
              self.is_within_bounds(map_x + 1, map_y) and self.map[map_y][map_x + 1] not in [0, 1, 2, 3, 4, 5] and  # Right is not grass or water
              self.is_within_bounds(map_x, map_y - 1) and self.map[map_y - 1][map_x] in [0, 1, 2, 3, 7, 12, 13] and # Above is grass or shore with grass
              not (self.map[map_y][map_x + 1] in [7, 12] and self.map[map_y + 1][map_x] in [9]) and
              not (self.map[map_y][map_x - 1] in [7, 13] and self.map[map_y + 1][map_x] in [8])):
            self.map[map_y][map_x] = 6 # shore-top
        elif (self.is_within_bounds(map_x, map_y - 1) and self.map[map_y - 1][map_x] not in [0, 1, 2, 3] and  # Above is not grass
              self.is_within_bounds(map_x - 1, map_y) and self.map[map_y][map_x - 1] not in [0, 1, 2, 3, 4, 5] and  # Left is not grass or water
              self.is_within_bounds(map_x + 1, map_y) and self.map[map_y][map_x + 1] not in [0, 1, 2, 3, 4, 5] and  # Right is not grass or water
              self.is_within_bounds(map_x, map_y + 1) and self.map[map_y + 1][map_x] in [0, 1, 2, 3, 6, 10, 11] and
              not (self.map[map_y][map_x - 1] in [6, 11] and self.map[map_y - 1][map_x] in [8]) and
              not (self.map[map_y][map_x + 1] in [6, 10] and self.map[map_y - 1][map_x] in [9])):
            self.map[map_y][map_x] = 7 # shore-bottom
        elif (self.is_within_bounds(map_x + 1, map_y) and self.map[map_y][map_x + 1] not in [0, 1, 2, 3] and  # Right is not grass
              self.is_within_bounds(map_x, map_y - 1) and self.map[map_y - 1][map_x] not in [0, 1, 2, 3, 4, 5] and  # Above is not grass or water
              self.is_within_bounds(map_x, map_y + 1) and self.map[map_y + 1][map_x] not in [0, 1, 2, 3, 4, 5] and  # Below is not grass or water
              self.is_within_bounds(map_x - 1, map_y) and self.map[map_y][map_x - 1] in [0, 1, 2, 3, 9, 11, 13] and  # Left is something with grass on the right
              not (self.map[map_y - 1][map_x] in [9, 13] and self.map[map_y][map_x + 1] in [6]) and
              not (self.map[map_y + 1][map_x] in [9, 11] and self.map[map_y][map_x + 1] in [7])):
            self.map[map_y][map_x] = 8 # shore-left
        elif (self.is_within_bounds(map_x - 1, map_y) and self.map[map_y][map_x - 1] not in [0, 1, 2, 3] and  # Left is not grass
              self.is_within_bounds(map_x, map_y - 1) and self.map[map_y - 1][map_x] not in [0, 1, 2, 3, 4, 5] and  # Above is not grass or water
              self.is_within_bounds(map_x, map_y + 1) and self.map[map_y + 1][map_x] not in [0, 1, 2, 3, 4, 5] and  # Below is not grass or water
              self.is_within_bounds(map_x + 1, map_y) and self.map[map_y][map_x + 1] in [0, 1, 2, 3, 8, 10, 12] and  # Right is something with grass on the left
              not (self.map[map_y + 1][map_x] in [8, 10] and self.map[map_y][map_x - 1] in [7]) and
              not (self.map[map_y - 1][map_x] in [8, 12] and self.map[map_y][map_x - 1] in [6])):
            self.map[map_y][map_x] = 9 # shore-right
        elif (self.is_within_bounds(map_x, map_y + 1) and self.map[map_y + 1][map_x] not in [0, 1, 2, 3, 4, 5] and  # Below is not grass or water AND
              self.is_within_bounds(map_x + 1, map_y) and self.map[map_y][map_x + 1] not in [0, 1, 2, 3, 4, 5] and  # Right is not grass or water AND
              ((self.is_within_bounds(map_x - 1, map_y) and self.map[map_y][map_x - 1] in [0, 1, 2, 3, 9, 11, 13]) or  # Left is something with grass on the right or...
               (((self.is_within_bounds(map_x, map_y + 1) and self.map[map_y + 1][map_x] in [8]) and (self.is_within_bounds(map_x - 1, map_y) and self.map[map_y][map_x - 1] in [7])))) and #... an especific exception where its trapped AND
              ((self.is_within_bounds(map_x, map_y - 1) and self.map[map_y - 1][map_x] in [0, 1, 2, 3, 7, 12, 13]) or # Above is something with grass on the bottom or...
                ((self.is_within_bounds(map_x, map_y - 1) and self.map[map_y - 1][map_x] in [9]) and (self.is_within_bounds(map_x + 1, map_y) and self.map[map_y][map_x + 1] in [6])))): #... an especific exception where its trapped with the above tile also wrong, and the right tile is an specific shore tile
            self.map[map_y][map_x] = 10 # shore-topleft
        elif (self.is_within_bounds(map_x, map_y + 1) and self.map[map_y + 1][map_x] not in [0, 1, 2, 3, 4, 5] and  # Below is not grass or water
              self.is_within_bounds(map_x - 1, map_y) and self.map[map_y][map_x - 1] not in [0, 1, 2, 3, 4, 5] and  # Left is not grass or water
              ((self.is_within_bounds(map_x + 1, map_y) and self.map[map_y][map_x + 1] in [0, 1, 2, 3, 8, 10, 12]) or  # Right is something with grass on the left or...
               (((self.is_within_bounds(map_x, map_y + 1) and self.map[map_y + 1][map_x] in [9]) and (self.is_within_bounds(map_x + 1, map_y) and self.map[map_y][map_x + 1] in [7])))) and #... an especific exception where its trapped AND
              ((self.is_within_bounds(map_x, map_y - 1) and self.map[map_y - 1][map_x] in [0, 1, 2, 3, 7, 12, 13]) or # Above is something with grass on the bottom or...
               ((self.is_within_bounds(map_x, map_y - 1) and self.map[map_y - 1][map_x] in [8]) and (self.is_within_bounds(map_x - 1, map_y) and self.map[map_y][map_x - 1] in [6])))): #... an especific exception where its trapped with the above tile also wrong, and the left tile is an specific shore tile
            self.map[map_y][map_x] = 11 # shore-topright
        elif (self.is_within_bounds(map_x, map_y - 1) and self.map[map_y - 1][map_x] not in [0, 1, 2, 3, 4, 5] and # Above is not grass or water
              self.is_within_bounds(map_x + 1, map_y) and self.map[map_y][map_x + 1] not in [0, 1, 2, 3, 4, 5] and # Right is not grass or water
              self.is_within_bounds(map_x - 1, map_y) and self.map[map_y][map_x - 1] in [0, 1, 2, 3, 9, 11, 13] and # Left is something with grass on the right
              self.is_within_bounds(map_x, map_y + 1) and self.map[map_y + 1][map_x] in [0, 1, 6, 10, 11]): # Below is something with grass on the top
            self.map[map_y][map_x] = 12 # shore-bottomleft
        elif (self.is_within_bounds(map_x, map_y - 1) and self.map[map_y - 1][map_x] not in [0, 1, 2, 3, 4, 5] and # Above is not grass or water
              self.is_within_bounds(map_x - 1, map_y) and self.map[map_y][map_x - 1] not in [0, 1, 2, 3, 4, 5] and # Left is not grass or water
              self.is_within_bounds(map_x + 1, map_y) and self.map[map_y][map_x + 1] in [0, 1, 2, 3, 8, 10, 12] and # Right is something with grass on the left
              self.is_within_bounds(map_x, map_y + 1) and self.map[map_y + 1][map_x] in [0, 1, 2, 3, 6, 10, 11]): # Below is something with grass on the top
            self.map[map_y][map_x] = 13 # shore-bottomright
    
    def get_surrounding_grass(self, map_x, map_y):
        grass_coords = []
        directions = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        
        for dx, dy in directions:
            new_x, new_y = map_x + dx, map_y + dy
            if self.is_within_bounds(new_x, new_y):
                if self.map[new_y][new_x] in [0, 1, 2, 3]:
                    grass_coords.append((new_x, new_y))
        
        return grass_coords

    def is_within_bounds(self, x, y):
        return 0 <= x < self.map_width and 0 <= y < self.map_height

    def update_tile(self, map_x, map_y):
        current_tile = self.map[map_y][map_x]
        
        # If water, ensure surrounded by valid shores
        if current_tile in [4, 5]:
            self.ensure_water_surrounded_by_shore(map_x, map_y)
        
        # If shore, validate it
        elif current_tile in [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]:
            if not self.is_valid_shore(map_x, map_y, current_tile):
                self.map[map_y][map_x] = 4  # Convert to water
                self.ensure_water_surrounded_by_shore(map_x, map_y)

    def is_valid_shore(self, map_x, map_y, shore_type):
        # Validate shore based on required grass neighbor(s)
        if shore_type == 6:  # shore-top
            return self.has_grass(map_x, map_y - 1)
        elif shore_type == 7:  # shore-bottom
            return self.has_grass(map_x, map_y + 1)
        elif shore_type == 8:  # shore-left
            return self.has_grass(map_x - 1, map_y)
        elif shore_type == 9:  # shore-right
            return self.has_grass(map_x + 1, map_y)
        elif shore_type == 10:  # shore-top-left
            return self.has_grass(map_x - 1, map_y) and self.has_grass(map_x, map_y - 1)
        elif shore_type == 11:  # shore-top-right
            return self.has_grass(map_x + 1, map_y) and self.has_grass(map_x, map_y - 1)
        elif shore_type == 12:  # shore-bottom-left
            return self.has_grass(map_x - 1, map_y) and self.has_grass(map_x, map_y + 1)
        elif shore_type == 13:  # shore-bottom-right
            return self.has_grass(map_x + 1, map_y) and self.has_grass(map_x, map_y + 1)
        elif shore_type == 14:  # shore-top-tip-left
            return (self.is_within_bounds(map_x, map_y - 1) and self.map[map_y - 1][map_x] == 10 and
                    self.is_within_bounds(map_x - 1, map_y - 1) and self.map[map_y - 1][map_x - 1] == 10)
        elif shore_type == 15:  # shore-top-tip-right
            return (self.is_within_bounds(map_x, map_y - 1) and self.map[map_y - 1][map_x] == 11 and
                    self.is_within_bounds(map_x + 1, map_y - 1) and self.map[map_y - 1][map_x + 1] == 11)
        elif shore_type == 16:  # shore-bottom-tip-left
            return (self.is_within_bounds(map_x, map_y + 1) and self.map[map_y + 1][map_x] == 12 and
                    self.is_within_bounds(map_x - 1, map_y + 1) and self.map[map_y + 1][map_x - 1] == 12)
        elif shore_type == 17:  # shore-bottom-tip-right
            return (self.is_within_bounds(map_x, map_y + 1) and self.map[map_y + 1][map_x] == 13 and
                    self.is_within_bounds(map_x + 1, map_y + 1) and self.map[map_y + 1][map_x + 1] == 13)
        elif shore_type == 18:  # shore-double-tip-topleft
            return (self.is_within_bounds(map_x, map_y - 1) and self.map[map_y - 1][map_x] in [10, 14] and
                    self.is_within_bounds(map_x - 1, map_y) and self.map[map_y][map_x - 1] in [8, 14])
        elif shore_type == 19:  # shore-double-tip-topright
            return (self.is_within_bounds(map_x, map_y - 1) and self.map[map_y - 1][map_x] in [11, 15] and
                    self.is_within_bounds(map_x + 1, map_y) and self.map[map_y][map_x + 1] in [9, 15])
        return False
    
    def has_grass(self, x, y):
        if not (0 <= x < self.map_width and 0 <= y < self.map_height):
            return False
        return self.map[y][x] in [0, 1, 2, 3]
    
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
            title="Save Map"
        )
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    # Write header comments
                    f.write("#Map tiles: Dimensions followed by tile separated by [ ].\n")
                    f.write(f"{self.map_width} {self.map_height}\n")
                    
                    # Write map tiles
                    for row in self.map:
                        line = ''.join(f"[{tile:05d}]" for tile in row)
                        f.write(line + '\n')
                    
                    # Write objects section
                    f.write("#Objects: on format [x][y][type][id][health][z-index]\n")
                    for obj in self.objects:
                        f.write(f"[{obj['x']}][{obj['y']}][{obj['type']}][{obj['id']}][{obj['health']}][{obj['z_index']}]\n")
                
                print(f"Map saved successfully to {file_path}")
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
                    lines = [line.strip() for line in f.readlines() if line.strip() and not line.strip().startswith('#')]
                    
                    if not lines or len(lines) < 2:
                        print("Error: File is empty or missing data.")
                        return
                    
                    # Parse dimensions from first line
                    width, height = map(int, lines[0].split())
                    print(f"Loading map with dimensions: {width}x{height}")
                    
                    if width != self.map_width or height != self.map_height:
                        print(f"Warning: File dimensions ({width}x{height}) do not match editor dimensions ({self.map_width}x{self.map_height}). Loading may fail.")
                        return
                    
                    # Read map tiles
                    self.map = []
                    for y in range(height):
                        if y + 1 >= len(lines):
                            print(f"Error: Missing row {y} in map data.")
                            return
                        
                        # Extract tile numbers from [00000] format
                        tiles = []
                        line = lines[y + 1]
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
                        
                        if len(tiles) != width:
                            print(f"Error: Row {y} has {len(tiles)} tiles, expected {width}.")
                            return
                        
                        self.map.append(tiles)
                    
                    # Read objects (if any)
                    self.objects = []
                    for line in lines[height + 1:]:
                        # Extract object data from [x][y][type][id][health][z-index] format
                        obj_data = []
                        i = 0
                        while i < len(line):
                            if line[i] == '[':
                                end = line.find(']', i)
                                if end != -1:
                                    data = line[i+1:end]
                                    obj_data.append(data)
                                    i = end + 1
                                else:
                                    i += 1
                            else:
                                i += 1
                        
                        if len(obj_data) != 6:
                            print(f"Error: Invalid object format: {line}")
                            continue
                        
                        try:
                            x = int(obj_data[0])
                            y = int(obj_data[1])
                            obj_type = obj_data[2]
                            obj_id = int(obj_data[3])
                            health = int(obj_data[4])
                            z_index = int(obj_data[5])
                            
                            if 0 <= x < width and 0 <= y < height:
                                self.objects.append({
                                    'x': x,
                                    'y': y,
                                    'type': obj_type,
                                    'id': obj_id,
                                    'health': health,
                                    'z_index': z_index
                                })
                            else:
                                print(f"Warning: Object at invalid coordinates ({x}, {y})")
                        except ValueError as e:
                            print(f"Error parsing object data: {e}")
                
                print(f"Successfully loaded map with {len(self.objects)} objects")
            except Exception as e:
                print(f"Error loading map: {e}")
        root.destroy()

    # --- Exit Function ---
    def exit_editor(self):
        print("Exiting editor...")
        pygame.quit()
        sys.exit()

    def randomize_grass_tiles(self):
        """Randomize all grass tiles (0-3) in the map"""
        for y in range(self.map_height):
            for x in range(self.map_width):
                if self.map[y][x] in [0, 1, 2, 3]:  # If it's a grass tile
                    self.map[y][x] = random.randint(0, 3)  # Replace with random grass tile
                    # Update surrounding area to ensure proper shore tiles
                    self.update_map_area(x, y)

    def randomize_water_tiles(self):
        """Randomize all water tiles (4-5) in the map"""
        for y in range(self.map_height):
            for x in range(self.map_width):
                if self.map[y][x] in [4, 5]:  # If it's a water tile
                    self.map[y][x] = random.randint(4, 5)  # Replace with random water tile
                    # Update surrounding area to ensure proper shore tiles
                    self.update_map_area(x, y)

    def randomize_map(self):
        """Generate a random map with water tiles and proper shore transitions"""
        # First, clear the map with grass
        for y in range(self.map_height):
            for x in range(self.map_width):
                self.map[y][x] = 0  # Set to grass tile 00000
        
        # First pass: 3% chance for water tiles
        for y in range(self.map_height):
            for x in range(self.map_width):
                if random.random() < 0.03:  # 3% chance
                    # Temporarily change selected tile to water
                    old_selected = self.selected_tile
                    self.selected_tile = random.randint(4, 5)  # Random water tile
                    self.place_tile(x, y)  # This will handle all the shore tile logic
                    self.selected_tile = old_selected  # Restore original selection
        
        # Second pass: 10% chance for shore tiles to become water
        for y in range(self.map_height):
            for x in range(self.map_width):
                if self.map[y][x] in [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]:  # If it's a shore tile
                    if random.random() < 0.10:  # 10% chance
                        # Temporarily change selected tile to water
                        old_selected = self.selected_tile
                        self.selected_tile = random.randint(4, 5)  # Random water tile
                        self.place_tile(x, y)  # This will handle all the shore tile logic
                        self.selected_tile = old_selected  # Restore original selection

    def is_valid_object_position(self, map_x, map_y):
        """Check if an object can be placed at the given position.
        Returns True if the position is valid (grass tile and no existing object), False otherwise."""
        if not (0 <= map_x < self.map_width and 0 <= map_y < self.map_height):
            return False
        
        # Check if the tile is grass (0-3)
        tile = self.map[map_y][map_x]
        if tile not in [0, 1, 2, 3]:  # Not a grass tile
            return False
        
        # Check if there's already an object at this position
        for obj in self.objects:
            if obj['x'] == map_x and obj['y'] == map_y:
                return False
        
        return True  # Position is valid (grass tile and no existing object)

# --- Main Execution ---
if __name__ == "__main__":
    pygame.init()
    # Get screen info
    screen_info = pygame.display.Info()
    # Set window size to 90% of screen size for comfortable windowed mode
    window_width = int(screen_info.current_w * 0.9)
    window_height = int(screen_info.current_h * 0.9)
    
    # Create a resizable window with window controls
    screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
    pygame.display.set_caption("Map Editor")
    editor = Editor(screen)
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                editor = Editor(screen)  # Reinitialize editor with new screen size
            editor.handle_events(event)
        editor.update()
        editor.render()
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()