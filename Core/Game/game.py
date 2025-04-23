import pygame
import sys
import os
import math
from Core.Game.panel import Panel
from Core.Game.vertical_panel import VerticalPanel
from Core.Game.object_collection import ObjectCollection

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
        self.selected_object = None  # Track the currently selected object

        # Define the tile size (32x32 pixels)
        self.tile_size = 32

        # Selection ring properties
        self.selection_ring_color = (255, 255, 0)  # Yellow
        self.selection_ring_width = 2
        self.selection_ring_radius = 20  # Base radius for small/large objects
        self.selection_ring_huge_radius = 40  # Double radius for huge objects

        # Load panel images
        self.horizontal_left_area = pygame.image.load("Images/game_menu_horizontal_left_area.png").convert_alpha()
        self.default_selection = pygame.image.load("Images/default_selection.png").convert_alpha()
        self.selected_object_image = None  # Will store the selected object's image

        # Load and cache tile images
        self.tile_cache = {}  # Cache for tile images
        self.tiles = []  # List of cached tile surfaces
        for i in range(20):  # Load tiles 00000.png to 00019.png
            try:
                tile_path = f"Maps/Common/Tiles/{i:05d}.png"
                if tile_path not in self.tile_cache:
                    tile_image = pygame.image.load(tile_path)
                    tile_image = pygame.transform.scale(tile_image, (self.tile_size, self.tile_size))
                    self.tile_cache[tile_path] = tile_image
                self.tiles.append(self.tile_cache[tile_path])
            except pygame.error as e:
                print(f"Error loading tile {i:05d}.png: {e}")
                # If a tile fails to load, use a default colored surface
                default_tile = pygame.Surface((self.tile_size, self.tile_size))
                default_tile.fill((i * 10, i * 10, i * 10))  # Different shade for each missing tile
                self.tiles.append(default_tile)

        # Initialize object collection before loading map
        self.object_collection = ObjectCollection()
        self.objects = []  # Will be populated in load_map

        # Load the map from file
        map_path = os.path.join("Maps", "Battle", "map.map")
        self.map = self.load_map(map_path)
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

        # Add object rendering optimization variables
        self.visible_objects_cache = []
        self.last_camera_x = 0
        self.last_camera_y = 0
        self.camera_moved = True

        # Add dirty rectangle optimization variables
        self.dirty_rects = []  # List of rectangles that need updating
        self.last_camera_pos = (0, 0)  # Track last camera position
        self.visible_area = None  # Current visible area rectangle
        self.background_surface = pygame.Surface((self.screen_width, self.screen_height))
        self.background_surface.fill((0, 0, 0))  # Black background

    def load_map(self, file_path):
        try:
            with open(file_path, 'r') as file:
                # Read all lines, ignoring comments and empty lines
                lines = [line.strip() for line in file.readlines() if line.strip() and not line.strip().startswith('#')]
                
                if not lines or len(lines) < 2:
                    print(f"Error: Map file is empty or missing data: {file_path}")
                    return [[(x + y) % 2 for x in range(120)] for y in range(120)]  # Return default map
                
                # Parse dimensions from first line
                width, height = map(int, lines[0].split())
                
                # Read map tiles
                map_data = []
                for y in range(height):
                    if y + 1 >= len(lines):
                        print(f"Error: Missing row {y} in map data.")
                        return [[(x + y) % 2 for x in range(120)] for y in range(120)]  # Return default map
                    
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
                        return [[(x + y) % 2 for x in range(120)] for y in range(120)]  # Return default map
                    
                    map_data.append(tiles)
                
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
                        continue
                    
                    try:
                        x = int(obj_data[0])
                        y = int(obj_data[1])
                        obj_type = obj_data[2].lower()  # Convert to lowercase for consistency
                        obj_id = int(obj_data[3])
                        health = int(obj_data[4])
                        z_index = int(obj_data[5])
                        
                        if 0 <= x < width and 0 <= y < height:
                            # Try to get the object in all sizes
                            obj_image = None
                            offset = 16  # Default to small object offset
                            
                            # Try huge first
                            obj_image = self.object_collection.get_object(obj_type, obj_id, 'huge')
                            if obj_image:
                                offset = 64
                            else:
                                # Try large
                                obj_image = self.object_collection.get_object(obj_type, obj_id, 'large')
                                if obj_image:
                                    offset = 32
                                else:
                                    # Try small
                                    obj_image = self.object_collection.get_object(obj_type, obj_id, 'small')
                            
                            if obj_image:
                                self.objects.append({
                                    'x': x,
                                    'y': y,
                                    'type': obj_type,
                                    'id': obj_id,
                                    'health': health,
                                    'z_index': z_index,
                                    'image': obj_image,
                                    'offset': offset
                                })
                            else:
                                print(f"Warning: Could not find object image for {obj_type} {obj_id}")
                    except ValueError as e:
                        print(f"Error parsing object data: {e}")
                
                return map_data
                
        except FileNotFoundError:
            print(f"Map file not found: {file_path}")
            return [[(x + y) % 2 for x in range(120)] for y in range(120)]  # Return default map
        except Exception as e:
            print(f"Error loading map: {e}")
            return [[(x + y) % 2 for x in range(120)] for y in range(120)]  # Return default map

    def is_minimap_clicked(self, pos):
        minimap_rect = pygame.Rect(self.minimap_x, self.minimap_y, 
                                 self.minimap_size, self.minimap_size)
        return minimap_rect.collidepoint(pos)

    def draw_selection_ring(self, center, radius, color, width):
        """
        Draws an elliptical ring around `center`, but split into a back‑half and front‑half
        so you can render a sprite between them to give depth.
        """
        x, y = center
        # Create a rect with different width and height for the ellipse
        rect = pygame.Rect(x - radius, y - radius * 0.7, radius * 2, radius * 1.4)
        
        # Back half: from 90° to 270° (bottom part of circle)
        pygame.draw.arc(self.screen, color, rect,
                        math.pi/2,      # start angle (90°)
                        3*math.pi/2,    # end angle   (270°)
                        width)
        
        # Front half: from -90° to +90° (top part of circle)
        pygame.draw.arc(self.screen, color, rect,
                        -math.pi/2,     # start angle (-90°)
                        math.pi/2,      # end angle   (+90°)
                        width)

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
            # Check for object selection
            elif event.button == 1:  # Left click
                self.selected_object = None  # Clear current selection
                self.selected_object_image = None  # Clear selected object image
                mouse_x, mouse_y = mouse_pos
                
                # Convert screen coordinates to world coordinates
                world_x = mouse_x + self.camera_x
                world_y = mouse_y + self.camera_y
                
                # Check each object for selection
                for obj in self.objects:
                    obj_world_x = obj['x'] * self.tile_size
                    obj_world_y = obj['y'] * self.tile_size
                    obj_width = obj['image'].get_width()
                    obj_height = obj['image'].get_height()
                    
                    # Calculate object's screen position
                    obj_screen_x = obj_world_x - self.camera_x
                    obj_screen_y = obj_world_y - self.camera_y
                    
                    # Calculate offset for centering
                    offset = obj['offset'] - self.tile_size // 2
                    
                    # Create a rect for the object
                    obj_rect = pygame.Rect(
                        obj_screen_x - offset,
                        obj_screen_y - offset,
                        obj_width,
                        obj_height
                    )
                    
                    # Check if mouse is within the object's rect
                    if obj_rect.collidepoint(mouse_x, mouse_y):
                        self.selected_object = obj
                        # Try to load the object's image from the Images folder
                        try:
                            image_path = os.path.join("Images", f"{obj['type']}{obj['id']:05d}.png")
                            if os.path.exists(image_path):
                                self.selected_object_image = pygame.image.load(image_path).convert_alpha()
                            else:
                                self.selected_object_image = self.default_selection
                        except:
                            self.selected_object_image = self.default_selection
                        break
            
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

        # Pass events to the vertical panel if it's visible
        if self.vertical_panel_visible:
            self.vertical_panel.handle_events(event)

    def update_camera_from_minimap(self, mouse_pos):
        # Calculate the click position relative to the minimap
        rel_x = mouse_pos[0] - self.minimap_x
        rel_y = mouse_pos[1] - self.minimap_y
        
        # Convert minimap coordinates to world coordinates
        world_x = int(rel_x / self.minimap_scale)
        world_y = int(rel_y / self.minimap_scale)
        
        # Store old camera position to check if it changed
        old_camera_x = self.camera_x
        old_camera_y = self.camera_y
        
        # Center the camera on the clicked position
        self.camera_x = max(0, min(world_x - self.camera_width // 2, 
                                 self.map_width * self.tile_size - self.camera_width))
        self.camera_y = max(0, min(world_y - self.camera_height // 2,
                                 self.map_height * self.tile_size - self.camera_height))
        
        # Set camera_moved flag if position changed
        if old_camera_x != self.camera_x or old_camera_y != self.camera_y:
            self.camera_moved = True

    def update_visible_area(self):
        """Update the visible area rectangle based on camera position"""
        self.visible_area = pygame.Rect(
            self.camera_x,
            self.camera_y,
            self.camera_width,
            self.camera_height
        )

    def update(self):
        # Get mouse position once
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Define the edge detection area and speed
        edge_area = 10  # Pixels from the edge to start moving
        base_speed = self.camera_speed
        edge_speed = base_speed * 2  # Double speed at edges

        # Calculate camera movement
        dx = 0
        dy = 0

        # Horizontal movement
        if mouse_x < edge_area:
            dx = -edge_speed
        elif mouse_x > self.screen_width - edge_area:
            dx = edge_speed
        elif mouse_x < edge_area * 2:
            dx = -base_speed
        elif mouse_x > self.screen_width - edge_area * 2:
            dx = base_speed

        # Vertical movement
        if mouse_y < edge_area:
            dy = -edge_speed
        elif mouse_y > self.screen_height - edge_area:
            dy = edge_speed
        elif mouse_y < edge_area * 2:
            dy = -base_speed
        elif mouse_y > self.screen_height - edge_area * 2:
            dy = edge_speed

        # Update camera position
        if dx != 0 or dy != 0:
            old_camera_x = self.camera_x
            old_camera_y = self.camera_y
            self.camera_x = max(0, min(self.camera_x + dx, 
                                     self.map_width * self.tile_size - self.camera_width))
            self.camera_y = max(0, min(self.camera_y + dy,
                                     self.map_height * self.tile_size - self.camera_height))
            # Set camera_moved if the position actually changed
            if old_camera_x != self.camera_x or old_camera_y != self.camera_y:
                self.camera_moved = True

        # Update panel animations and check for screen transitions
        next_screen = self.vertical_panel.update()
        if next_screen:
            return next_screen

    def update_visible_objects(self):
        """Update the list of visible objects only when camera moves significantly"""
        if not self.camera_moved:
            return

        self.visible_objects_cache = []
        
        # Calculate visible area in world coordinates with padding
        visible_left = self.camera_x - 100  # Add padding to ensure objects are visible when partially off-screen
        visible_right = self.camera_x + self.screen_width + 100
        visible_top = self.camera_y - 100
        visible_bottom = self.camera_y + self.screen_height + 100
        
        # Pre-calculate tile size for faster access
        tile_size = self.tile_size
        
        # Pre-calculate half tile size for offset calculations
        half_tile = tile_size // 2
        
        for obj in self.objects:
            # Calculate object's world position in pixels
            obj_world_x = obj['x'] * tile_size
            obj_world_y = obj['y'] * tile_size
            
            # Get object dimensions
            obj_width = obj['image'].get_width()
            obj_height = obj['image'].get_height()
            
            # Check if object is in view with padding using simple bounds check
            if (obj_world_x + obj_width < visible_left or 
                obj_world_x > visible_right or
                obj_world_y + obj_height < visible_top or
                obj_world_y > visible_bottom):
                continue
            
            # Calculate object's screen position
            obj_screen_x = obj_world_x - self.camera_x
            obj_screen_y = obj_world_y - self.camera_y
            
            # Calculate offset for centering
            offset = obj['offset'] - half_tile
            
            self.visible_objects_cache.append({
                'obj': obj,
                'screen_x': obj_screen_x - offset,
                'screen_y': obj_screen_y - offset
            })

        # Sort visible objects by z-index, then y, then x
        self.visible_objects_cache.sort(key=lambda x: (x['obj']['z_index'], x['obj']['y'], x['obj']['x']))
        self.camera_moved = False

    def render(self):
        # Clear the screen before rendering
        self.screen.fill((0, 0, 0))  # Black background

        # Clear dirty rectangles from last frame
        self.dirty_rects = []

        # Add the entire visible area to dirty rects if camera moved
        if self.camera_moved:
            self.dirty_rects.append(pygame.Rect(0, 0, self.screen_width, self.screen_height))
            # Update visible objects when camera moves
            self.update_visible_objects()

        # Calculate exact camera position in tiles (floating point)
        camera_tile_x = self.camera_x / self.tile_size
        camera_tile_y = self.camera_y / self.tile_size

        # Calculate visible area in tiles with extra buffer, ensuring we round down
        start_tile_x = max(0, int(camera_tile_x - 1))
        start_tile_y = max(0, int(camera_tile_y - 1))
        end_tile_x = min(self.map_width, start_tile_x + (self.camera_width // self.tile_size) + 3)
        end_tile_y = min(self.map_height, start_tile_y + (self.camera_height // self.tile_size) + 3)

        # Calculate precise pixel offsets
        offset_x = -(self.camera_x - start_tile_x * self.tile_size)
        offset_y = -(self.camera_y - start_tile_y * self.tile_size)

        # Calculate the source rectangle for the map surface
        source_rect = pygame.Rect(
            start_tile_x * self.tile_size,
            start_tile_y * self.tile_size,
            (end_tile_x - start_tile_x) * self.tile_size,
            (end_tile_y - start_tile_y) * self.tile_size
        )

        # Calculate the destination rectangle using precise offsets
        dest_rect = pygame.Rect(
            int(offset_x),
            int(offset_y),
            source_rect.width,
            source_rect.height
        )

        # Blit the visible portion of the pre-rendered map
        self.screen.blit(self.map_surface, dest_rect, source_rect)

        # First pass: Draw all non-selected objects and back parts of selection rings
        for obj_data in self.visible_objects_cache:
            obj = obj_data['obj']
            screen_x = obj_data['screen_x']
            screen_y = obj_data['screen_y']
            
            # Get object dimensions
            obj_width = obj['image'].get_width()
            obj_height = obj['image'].get_height()
            
            # Add object's rectangle to dirty rects
            obj_rect = pygame.Rect(screen_x, screen_y, obj_width, obj_height)
            self.dirty_rects.append(obj_rect)
            
            # Draw selection ring behind the object if it's selected
            if self.selected_object == obj:
                # Determine ring radius based on object size
                ring_radius = self.selection_ring_huge_radius if obj_width == 128 else self.selection_ring_radius
                
                # Draw back half of selection ring
                x, y = screen_x + obj_width // 2, screen_y + obj_height // 2
                rect = pygame.Rect(x - ring_radius, y - ring_radius * 0.7, ring_radius * 2, ring_radius * 1.4)
                pygame.draw.arc(self.screen, self.selection_ring_color, rect,
                              math.pi/2, 3*math.pi/2, self.selection_ring_width)
            
            # Render the object
            self.screen.blit(obj['image'], (screen_x, screen_y))
        
        # Second pass: Draw front parts of selection rings for selected objects
        for obj_data in self.visible_objects_cache:
            obj = obj_data['obj']
            if self.selected_object == obj:
                screen_x = obj_data['screen_x']
                screen_y = obj_data['screen_y']
                obj_width = obj['image'].get_width()
                obj_height = obj['image'].get_height()
                
                # Determine ring radius based on object size
                ring_radius = self.selection_ring_huge_radius if obj_width == 128 else self.selection_ring_radius
                
                # Draw front half of selection ring
                x, y = screen_x + obj_width // 2, screen_y + obj_height // 2
                rect = pygame.Rect(x - ring_radius, y - ring_radius * 0.7, ring_radius * 2, ring_radius * 1.4)
                pygame.draw.arc(self.screen, self.selection_ring_color, rect,
                              -math.pi/2, math.pi/2, self.selection_ring_width)

        # Render the minimap
        self.update_minimap()
        minimap_rect = pygame.Rect(self.minimap_x, self.minimap_y, 
                                 self.minimap_size, self.minimap_size)
        self.dirty_rects.append(minimap_rect)
        self.screen.blit(self.minimap_surface, (self.minimap_x, self.minimap_y))

        # Render the panels
        self.vertical_panel.render()
        self.panel.render()

        # Render selected object image in the horizontal panel's left area
        if self.panel_visible or self.panel.current_y < self.screen_height - self.panel.handle_height:
            # Get the left area position from the panel
            left_area_rect = self.panel.get_left_area_rect()
            
            # Adjust the y position based on the panel's current position
            left_area_rect.y = self.panel.current_y + self.panel.margin + 5
            
            # Draw the selected object image or default image
            if self.selected_object_image:
                # Scale the image to fit the left area while maintaining aspect ratio
                img_width, img_height = self.selected_object_image.get_size()
                scale = min(left_area_rect.width / img_width, left_area_rect.height / img_height)
                new_width = int(img_width * scale)
                new_height = int(img_height * scale)
                scaled_image = pygame.transform.scale(self.selected_object_image, (new_width, new_height))
                
                # Center the image in the left area
                x = left_area_rect.x + (left_area_rect.width - new_width) // 2
                y = left_area_rect.y + (left_area_rect.height - new_height) // 2
                self.screen.blit(scaled_image, (x, y))
            else:
                # Draw the default selection image
                self.screen.blit(self.default_selection, left_area_rect)
            
            # Draw the left area border on top
            self.screen.blit(self.horizontal_left_area, left_area_rect)

        # Update only the dirty areas of the screen
        if self.dirty_rects:
            pygame.display.update(self.dirty_rects)
        else:
            pygame.display.flip()

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
