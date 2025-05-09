import pygame
import sys
import os
import math
import json
from Core.Game.missile import Missile
from Core.UI.base_screen import BaseScreen
from Core.UI.panel import Panel
from Core.UI.minimap import Minimap
from Core.Game.object_collection import ObjectCollection
from Core.UI.cursor_manager import CursorManager
from Core.Game.animation_manager import AnimationManager
from Core.Game.vertical_panel import VerticalPanel
from typing import Optional, Any

class Game(BaseScreen):
    def __init__(self, screen):
        super().__init__(screen)
        self.screen_height = screen.get_height()
        self.screen_width = screen.get_width()
        self.panel_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)

        # Initialize music
        pygame.mixer.init()
        self.music_file = "Music/__bertsz__cyberpunk_MULTI.mp3"
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        pygame.mixer.music.load(self.music_file)
        pygame.mixer.music.play(-1, 0.0)

        # Initialize object collection before panels
        self.object_collection = ObjectCollection()
        self.objects = []  # Will be populated in load_map

        # Initialize spatial grid for object culling
        self.grid_cell_size = 128  # Size of each grid cell (4 tiles)
        self.spatial_grid = {}  # Dictionary to store objects by grid cell

        # Initialize attack state tracking
        self.active_attacks = {}  # Dictionary to track active attacks: {attacker_id: {'target_id': target_id, 'last_attack_time': time, 'cooldown': cooldown}}
        self.attack_cooldown = 1000  # Attack cooldown in milliseconds

        # Initialize missile state tracking
        self.missiles = []  # List to track active missiles
        self.missiles_images = self.load_missiles_images()

        # Initialize panels
        self.panels = []
        self.create_panels()

        # Initialize object collections
        self.object_collections = []
        self.create_object_collections()

        # Initialize dirty rects for optimization
        self.dirty_rects = []

        # Initialize managers
        self.animation_manager = AnimationManager()

        # Mouse state tracking
        self.last_mouse_pos = None
        self.selected_object = None  # Track the currently selected object

        # Define the tile size (32x32 pixels)
        self.tile_size = 32

        # Selection ring properties
        self.selection_ring_color = (255, 255, 0)  # Yellow
        self.selection_ring_width = 2
        self.selection_ring_radius = 20  # Base radius for small/large objects
        self.selection_ring_huge_radius = 40  # Double radius for huge objects

        # Load and cache tile images
        self.tile_cache = {}  # Cache for tile images
        self.tiles = []
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

        # Initialize minimap after map surface is created and is_dragging_minimap is set to False
        self.minimap = Minimap(self.screen_width, self.screen_height)
        self.minimap.set_map(self.map_surface, self.map_width * self.tile_size, self.map_height * self.tile_size)
        self.is_dragging_minimap = False

        # Camera variables
        self.camera_x = 0
        self.camera_y = 0
        self.camera_speed = 3
        self.camera_width = self.screen_width
        self.camera_height = self.screen_height

        # Create vertical panel
        self.vertical_panel = VerticalPanel(self.screen, self)  # Pass self to access minimap

        # Add object rendering optimization variables
        self.visible_objects_cache = []
        self.last_camera_x = 0
        self.last_camera_y = 0
        self.camera_moved = True  # Set to True initially to force first update

        # Add dirty rectangle optimization variables
        self.last_camera_pos = (0, 0)  # Track last camera position
        self.visible_area = None  # Current visible area rectangle
        self.background_surface = pygame.Surface((self.screen_width, self.screen_height))
        self.background_surface.fill((0, 0, 0))  # Black background

        # Initialize visible objects for the first frame
        self.update_visible_area()
        self.update_visible_objects()

    def create_panels(self):
        # Create panels for the game
        panel_width = 200
        panel_height = 50
        panel_spacing = 20
        start_x = (self.screen.get_width() - panel_width) // 2
        start_y = (self.screen.get_height() - (panel_height * 3 + panel_spacing * 2)) // 2

        # Create a single panel with the game's object collection
        self.panels = []
        self.panel = Panel(self.screen, self.object_collection)  # Create and assign to self.panel
        self.panel.game = self  # Set the game reference for the panel
        self.panels.append(self.panel)  # Also add to panels list

    def create_object_collections(self):
        """Create object collections for different sizes"""
        self.object_collections = []
        self.object_collections.append(ObjectCollection())  # Small objects
        self.object_collections.append(ObjectCollection())  # Large objects
        self.object_collections.append(ObjectCollection())  # Huge objects

    def get_grid_cell(self, x, y):
        """Get the grid cell coordinates for a world position"""
        cell_x = int(x // self.grid_cell_size)
        cell_y = int(y // self.grid_cell_size)
        return (cell_x, cell_y)

    def add_object_to_grid(self, obj):
        """Add an object to the spatial grid"""
        # Get object's world position in pixels
        obj_world_x = obj['x'] * self.tile_size
        obj_world_y = obj['y'] * self.tile_size
        
        # Get the grid cell for this object
        cell = self.get_grid_cell(obj_world_x, obj_world_y)
        
        # Add object to the grid cell
        if cell not in self.spatial_grid:
            self.spatial_grid[cell] = []
        self.spatial_grid[cell].append(obj)

    def remove_object_from_grid(self, obj):
        """Remove an object from the spatial grid"""
        # Get object's world position in pixels
        obj_world_x = obj['x'] * self.tile_size
        obj_world_y = obj['y'] * self.tile_size
        
        # Get the grid cell for this object
        cell = self.get_grid_cell(obj_world_x, obj_world_y)
        
        # Remove object from the grid cell
        if cell in self.spatial_grid and obj in self.spatial_grid[cell]:
            self.spatial_grid[cell].remove(obj)
            if not self.spatial_grid[cell]:  # If cell is empty, remove it
                del self.spatial_grid[cell]

    def load_missiles_images(self):
        # Load missiles from file
        missile_images = []
        for i in [0, 45, 90, 135, 180, 225, 270, 315]:
            missile_image = pygame.image.load(f"Images/Missiles/{str(i)}.png")
            missile_images.append(missile_image)
        return missile_images

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
                self.spatial_grid = {}  # Clear spatial grid
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
                    
                    if len(obj_data) != 7:
                        continue
                    
                    try:
                        x = int(obj_data[0])
                        y = int(obj_data[1])
                        obj_type = obj_data[2].lower()  # Convert to lowercase for consistency
                        obj_id = int(obj_data[3])
                        health = int(obj_data[4])
                        z_index = int(obj_data[5])
                        damage = int(obj_data[6])
                        
                        if 0 <= x < width and 0 <= y < height:
                            # Load object metadata from JSON

                            json_path = os.path.join("Maps", "Common", "Objects", obj_type, f"{obj_type}{obj_id:05d}.json")
                            metadata = {}
                            if os.path.exists(json_path):
                                with open(json_path, 'r') as f:
                                    metadata = json.load(f)
                            
                            # Get object image from animation manager
                            obj_image = self.animation_manager.load_animation(obj_type, obj_id, str(x) + '_' + str(y) + '_' + obj_type + '_' + str(obj_id), "static", 0)
                            if obj_image:
                                obj_image = obj_image[0]  # Get first frame for static animation
                            else:
                                # Fallback to object collection if no animation
                                obj_image = self.object_collection.get_object(obj_type, obj_id, 'huge')
                                if not obj_image:
                                    obj_image = self.object_collection.get_object(obj_type, obj_id, 'large')
                                    if not obj_image:
                                        obj_image = self.object_collection.get_object(obj_type, obj_id, 'small')
                            
                            if obj_image:
                                # Get object metadata
                                metadata = self.object_collection.get_object_metadata(obj_type, obj_id)
                                
                                # Get max_health from metadata, default to -1 (infinite) for resources
                                max_health = metadata.get('max_health', -1 if obj_type == 'resource' else 100)
                                
                                obj = {
                                    'x': x,
                                    'y': y,
                                    'type': obj_type,
                                    'id': obj_id,
                                    'health': health,
                                    'max_health': max_health,  # Add max_health property
                                    'z_index': z_index,
                                    'image': obj_image,
                                    'offset': 64 if obj_image.get_width() == 128 else 32,
                                    'damage': damage,
                                    'unique_id': str(x) + '_' + str(y) + '_' + obj_type + '_' + str(obj_id),
                                    'name': metadata.get('name', 'Unknown'),
                                    'animation_speed': metadata.get('visuals', {}).get('animation_speed', 0),
                                    'frames': metadata.get('visuals', {}).get('frames', 1),
                                    'is_unit': metadata.get('is_unit', False),
                                    'direction': metadata.get('direction', 0),
                                    'has_turret': metadata.get('has_turret', False),
                                    'turret_direction': metadata.get('turret_direction', 0)
                                }
                                self.objects.append(obj)
                                self.add_object_to_grid(obj)  # Add object to spatial grid
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
        minimap_rect = pygame.Rect(self.minimap.x, self.minimap.y, 
                                 self.minimap.size, self.minimap.size)
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

    def get_tile_from_screen_pos(self, screen_x, screen_y):
        """Convert screen coordinates to tile coordinates"""
        world_x = screen_x + self.camera_x
        world_y = screen_y + self.camera_y
        tile_x = world_x // self.tile_size
        tile_y = world_y // self.tile_size
        return tile_x, tile_y

    def get_objects_at_tile(self, tile_x, tile_y):
        """Get all objects at a specific tile coordinate"""
        objects_at_tile = []
        for obj in self.objects:
            if obj['x'] == tile_x and obj['y'] == tile_y:
                objects_at_tile.append(obj)
        return objects_at_tile

    def get_huge_objects_at_adjacent_tiles(self, tile_x, tile_y):
        """Get huge objects (128x128) that might be at adjacent tiles"""
        huge_objects = []
        adjacent_tiles = [
            (tile_x - 1, tile_y),  # left
            (tile_x + 1, tile_y),  # right
            (tile_x, tile_y - 1),  # top
            (tile_x, tile_y + 1)   # bottom
        ]
        
        for adj_x, adj_y in adjacent_tiles:
            for obj in self.objects:
                # Check if it's a huge object (128x128) at this adjacent tile
                if (obj['x'] == adj_x and obj['y'] == adj_y and 
                    obj['image'].get_width() == 128 and 
                    obj['image'].get_height() == 128):
                    huge_objects.append(obj)
        
        return huge_objects

    def is_click_on_panels(self, mouse_pos):
        """Check if the click is on any visible panel"""
        mouse_x, mouse_y = mouse_pos
        
        # Check horizontal panel (bottom panel)
        if self.panel.is_open or self.panel.current_y < self.screen_height - self.panel.handle_height:
            # Panel is visible or animating
            panel_y = self.panel.current_y
            if mouse_y >= panel_y:
                return True
        
        # Check vertical panel (side panel)
        if self.vertical_panel.is_open or self.vertical_panel.x > -self.vertical_panel.width:
            # Panel is visible or animating
            panel_x = self.vertical_panel.x
            if 0 <= mouse_x <= self.vertical_panel.width:
                return True
        
        return False

    def update_camera_from_minimap(self, mouse_pos):
        # Calculate the click position relative to the minimap
        rel_x = mouse_pos[0] - self.minimap.x
        rel_y = mouse_pos[1] - self.minimap.y
        
        # Convert minimap coordinates to world coordinates
        world_x = int(rel_x / self.minimap.scale)
        world_y = int(rel_y / self.minimap.scale)
        
        # Store old camera position to check if it changed
        old_camera_x = self.camera_x
        old_camera_y = self.camera_y
        
        # Center the camera on the clicked position
        self.camera_x = max(0, min(world_x - self.camera_width // 2, 
                                 self.map_width * self.tile_size - self.camera_width))
        self.camera_y = max(0, min(world_y - self.camera_height // 2,
                                 self.map_height * self.tile_size - self.camera_height))
        
        # Always update visible objects when using minimap
        self.camera_moved = True
        self.update_visible_area()
        self.update_visible_objects()

    def update_visible_area(self):
        """Update the visible area rectangle based on camera position"""
        self.visible_area = pygame.Rect(
            self.camera_x,
            self.camera_y,
            self.camera_width,
            self.camera_height
        )

    def handle_next_action(self) -> Optional[Any]:
        """Handle the next_action string and return the appropriate screen or None."""
        if not self.next_action:
            return None
            
        action = self.next_action
        self.next_action = None
        
        if action == "main_menu":
            from Core.Menu.main_menu import MainMenu
            return MainMenu(self.screen)
        elif action == "options":
            raise NotImplementedError("Options menu not yet implemented")
        elif action == "quit":
            pygame.quit()
            sys.exit()
            
        return None

    def update_visible_objects(self):
        """Update the list of visible objects only when camera moves significantly"""
        if not self.camera_moved:
            return

        self.visible_objects_cache = []
        
        # Calculate visible area in world coordinates with padding
        visible_left = self.camera_x - 100
        visible_right = self.camera_x + self.screen_width + 100
        visible_top = self.camera_y - 100
        visible_bottom = self.camera_y + self.screen_height + 100
        
        # Get the grid cells that intersect with the visible area
        start_cell = self.get_grid_cell(visible_left, visible_top)
        end_cell = self.get_grid_cell(visible_right, visible_bottom)
        
        # Pre-calculate tile size and half tile size for faster access
        tile_size = self.tile_size
        half_tile = tile_size // 2
        
        # Pre-calculate camera position for screen coordinate conversion
        camera_x = self.camera_x
        camera_y = self.camera_y
        
        # Pre-calculate screen dimensions for bounds checking
        screen_width = self.screen_width
        screen_height = self.screen_height
        
        # Check each grid cell in the visible area
        for cell_x in range(start_cell[0], end_cell[0] + 1):
            for cell_y in range(start_cell[1], end_cell[1] + 1):
                cell = (cell_x, cell_y)
                if cell in self.spatial_grid:
                    for obj in self.spatial_grid[cell]:
                        # Calculate object's world position in pixels
                        obj_world_x = obj['x'] * tile_size
                        obj_world_y = obj['y'] * tile_size
                        
                        # Get object dimensions
                        obj_width = obj['image'].get_width()
                        obj_height = obj['image'].get_height()
                        
                        # Quick bounds check for object visibility
                        if (obj_world_x + obj_width < visible_left or 
                            obj_world_x > visible_right or
                            obj_world_y + obj_height < visible_top or
                            obj_world_y > visible_bottom):
                            continue
                        
                        # Calculate object's screen position
                        obj_screen_x = obj_world_x - camera_x
                        obj_screen_y = obj_world_y - camera_y
                        
                        # Calculate offset for centering
                        offset = obj['offset'] - half_tile
                        
                        # Final screen position
                        final_x = obj_screen_x - offset
                        final_y = obj_screen_y - offset
                        
                        # Only add objects that are actually visible on screen
                        if (final_x + obj_width > 0 and final_x < screen_width and
                            final_y + obj_height > 0 and final_y < screen_height):
                            self.visible_objects_cache.append({
                                'obj': obj,
                                'screen_x': final_x,
                                'screen_y': final_y
                            })

        # Sort visible objects by z-index, then y, then x
        self.visible_objects_cache.sort(key=lambda x: (x['obj']['z_index'], x['obj']['y'], x['obj']['x']))
        self.camera_moved = False

    def calculate_angle(self, start_x, start_y, target_x, target_y):
        """Calculate the angle between two points in degrees"""
        dx = target_x - start_x
        dy = target_y - start_y
        # Convert to degrees and adjust for pygame's coordinate system
        # Add 90 degrees to rotate the coordinate system so 0 points down
        angle = math.degrees(math.atan2(-dy, dx)) + 90
        # Normalize to 0-359
        angle = (angle + 360) % 360
        return angle

    def get_nearest_direction(self, angle, directions):
        """Get the nearest direction from the available directions"""
        # Find the closest direction by comparing the absolute difference
        closest = min(directions, key=lambda x: min(abs(x - angle), 360 - abs(x - angle)))
        return closest

    def handle_attack_command(self, attack_result):
        """Handle an attack command from the panel"""
        attacker = attack_result['attacker']
        target = attack_result['target']
        
        if attack_result['in_range']:
            # Start attack immediately
            self.active_attacks[attacker['unique_id']] = {
                'attacker_type': attacker['type'],
                'attacker_id': attacker['id'],
                'attacker_unique_id': attacker['unique_id'],
                'target_type': target['type'],
                'target_id': target['id'],
                'target_unique_id': target['unique_id'],
                'last_attack_time': pygame.time.get_ticks() - 1000,
                'cooldown': 1000  # Default cooldown in milliseconds
            }
            # Set attacker's animation state to 'fire'
            # self.animation_manager.set_animation_state(attacker['unique_id'], 'fire')
        elif attack_result['is_unit']:
            # TODO: Handle unit movement towards target
            pass
        else:
            # Building can't reach target, ignore attack
            pass

    def handle_target_selection(self, target_object):
        """Handle target selection for attack"""
        if not self.attacker:
            return None
            
        # Calculate distance in tiles
        dx = target_object['x'] - self.attacker['x']
        dy = target_object['y'] - self.attacker['y']
        distance = (dx * dx + dy * dy) ** 0.5
        
        # Get attacker's metadata
        metadata = self.object_collection.get_object_metadata(self.attacker['type'], self.attacker['id'])
        
        if not metadata:
            return None
            
        properties = metadata.get('properties', {})
        attack_range = properties.get('attack_range', 0)
        
        if distance <= attack_range:
            return {
                'action': 'attack',
                'attacker': self.attacker,
                'target': target_object,
                'in_range': True,
                'is_unit': properties.get('is_unit', False)
            }
        else:
            return {
                'action': 'attack',
                'attacker': self.attacker,
                'target': target_object,
                'in_range': False,
                'is_unit': properties.get('is_unit', False)
            }

    def handle_events(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Handle events for horizontal panel first
        result = self.panel.handle_events(event)
        if result:
            if result == "panel_toggled":
                # Panel was toggled, no need to process further
                return

        # Handle events for vertical panel
        result = self.vertical_panel.handle_events(event)
        if result == "panel_toggled":
            # Panel was toggled, no need to process further
            return

        # Handle events for minimap
        if self.minimap.handle_event(event):
            # If minimap was clicked, update camera position
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEMOTION:
                world_pos = self.minimap.get_world_position(event.pos)
                if world_pos:
                    world_x, world_y = world_pos
                    # Center the camera on the clicked position
                    self.camera_x = max(0, min(world_x - self.camera_width // 2, 
                                             self.map_width * self.tile_size - self.camera_width))
                    self.camera_y = max(0, min(world_y - self.camera_height // 2,
                                             self.map_height * self.tile_size - self.camera_height))
                    # Update visible objects
                    self.camera_moved = True
                    self.update_visible_area()
                    self.update_visible_objects()

        # Track cursor state during targeting
        if self.panel.is_targeting:
            self.cursor_manager.set_cursor("targeting")
        elif event.type == pygame.MOUSEMOTION:
            # Only update cursor to normal if not in targeting mode
            self.cursor_manager.set_cursor("normal")

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check for panel button clicks first
            if self.panel.is_open and self.panel.handle_events(event):
                return

            # Then check if minimap is clicked
            if event.button == 1:  # Left click
                if self.is_minimap_clicked(mouse_pos):
                    self.is_dragging_minimap = True
                    self.last_mouse_pos = mouse_pos
                    self.update_camera_from_minimap(mouse_pos)
                # Check if we're in targeting mode
                elif self.panel.is_targeting:
                    # Get tile coordinates from mouse position
                    tile_x, tile_y = self.get_tile_from_screen_pos(mouse_pos[0], mouse_pos[1])
                    
                    # First check for objects at the clicked tile
                    objects_at_tile = self.get_objects_at_tile(tile_x, tile_y)
                    
                    if objects_at_tile:
                        # If there are objects at this tile, select the one with highest z-index
                        target_object = max(objects_at_tile, key=lambda x: x['z_index'])
                        # Handle the target selection
                        attack_result = self.panel.handle_target_selection(target_object)
                        if attack_result and attack_result['action'] == 'attack':
                            self.handle_attack_command(attack_result)
                    else:
                        # If no objects at this tile, check for huge objects at adjacent tiles
                        huge_objects = self.get_huge_objects_at_adjacent_tiles(tile_x, tile_y)
                        if huge_objects:
                            # Select the huge object with highest z-index
                            target_object = max(huge_objects, key=lambda x: x['z_index'])
                            # Handle the target selection
                            attack_result = self.panel.handle_target_selection(target_object)
                            if attack_result and attack_result['action'] == 'attack':
                                self.handle_attack_command(attack_result)
                # Finally check for object selection, but only if not clicking on panels
                elif not self.is_click_on_panels(mouse_pos):
                    # Get tile coordinates from mouse position
                    tile_x, tile_y = self.get_tile_from_screen_pos(mouse_pos[0], mouse_pos[1])
                    
                    # First check for objects at the clicked tile
                    objects_at_tile = self.get_objects_at_tile(tile_x, tile_y)
                    
                    if objects_at_tile:
                        # If there are objects at this tile, select the one with highest z-index
                        self.selected_object = max(objects_at_tile, key=lambda x: x['z_index'])
                    else:
                        # If no objects at this tile, check for huge objects at adjacent tiles
                        huge_objects = self.get_huge_objects_at_adjacent_tiles(tile_x, tile_y)
                        if huge_objects:
                            # Select the huge object with highest z-index
                            self.selected_object = max(huge_objects, key=lambda x: x['z_index'])
                        else:
                            # No objects found, clear selection
                            self.selected_object = None
                    
                    # Update the panel with the selected object
                    self.panel.set_selected_object(self.selected_object)
            elif event.button == 3:  # Right click
                # Cancel targeting mode if right clicked
                if self.panel.is_targeting:
                    self.panel.cancel_targeting()
                    self.cursor_manager.set_cursor("normal")

        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_dragging_minimap = False
            self.last_mouse_pos = None

        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging_minimap:
                mouse_pos = pygame.mouse.get_pos()
                if self.is_minimap_clicked(mouse_pos):
                    self.update_camera_from_minimap(mouse_pos)
                self.last_mouse_pos = mouse_pos

    def update(self):
        # Get mouse position once
        mouse_pos = pygame.mouse.get_pos()
        
        # Optimize camera movement with edge detection
        edge_area = 50  # pixels from edge to trigger camera movement
        move_speed = 15  # Increased from 5 to 15 for faster movement
        
        # Store old camera position to check if it changed
        old_camera_x = self.camera_x
        old_camera_y = self.camera_y
        
        # Calculate maximum camera positions
        max_camera_x = self.map_width * self.tile_size - self.screen_width
        max_camera_y = self.map_height * self.tile_size - self.screen_height
        
        # Check horizontal movement
        if mouse_pos[0] < edge_area:
            self.camera_x = max(0, self.camera_x - move_speed)
        elif mouse_pos[0] > self.screen_width - edge_area:
            self.camera_x = min(max_camera_x, self.camera_x + move_speed)
            
        # Check vertical movement
        if mouse_pos[1] < edge_area:
            self.camera_y = max(0, self.camera_y - move_speed)
        elif mouse_pos[1] > self.screen_height - edge_area:
            self.camera_y = min(max_camera_y, self.camera_y + move_speed)
            
        # Set camera_moved flag if position changed
        if old_camera_x != self.camera_x or old_camera_y != self.camera_y:
            self.camera_moved = True
            self.update_visible_area()
            self.update_visible_objects()

        # Process active attacks
        for attack in list(self.active_attacks.items()):
            attacker_unique_id = attack[0]
            attack_data = attack[1]
            target_unique_id = attack_data['target_unique_id']
            
            # Get attacker and target objects
            attacker = None
            target = None
            
            # Find attacker
            for obj in self.objects:
                if obj['unique_id'] == attacker_unique_id:
                    attacker = obj
                    break
                    
            # Find target
            for obj in self.objects:
                if obj['unique_id'] == target_unique_id:
                    target = obj
                    break
            
            if attacker and target:
                # Get attacker metadata
                attacker_metadata = self.object_collection.get_object_metadata(attacker['type'], attacker['id'])
                if not attacker_metadata:
                    del self.active_attacks[attacker_unique_id]
                    continue
                    
                # Get attack range from properties
                properties = attacker_metadata.get('properties', {})
                attack_range = properties.get('attack_range', 0)
                
                # Calculate distance in tiles
                dx = target['x'] - attacker['x']
                dy = target['y'] - attacker['y']
                distance = (dx * dx + dy * dy) ** 0.5
                
                # Check if target is still in range
                if distance > attack_range:
                    # Stop the attack
                    self.animation_manager.set_animation_state(attacker_unique_id, "static")
                    del self.active_attacks[attacker_unique_id]
                    continue
                
                # Update attack cooldown
                current_time = pygame.time.get_ticks()
                if current_time - attack_data['last_attack_time'] >= attack_data['cooldown']:
                    # Calculate angle for projectile
                    angle = self.calculate_angle(attacker['x'], attacker['y'], target['x'], target['y'])
                    nearest_direction = self.get_nearest_direction(angle, attacker_metadata['visuals']['directions'])
                    attacker['turret_direction'] = self.animation_manager.get_current_direction(attacker_unique_id)
                    if(nearest_direction != attacker['turret_direction']):
                        self.animation_manager.set_target_direction(attacker_unique_id, nearest_direction)
                    else:
                        # Perform attack
                        self.animation_manager.set_animation_state(attacker_unique_id, "fire")
                        attack_data['last_attack_time'] = current_time
                        # Convert tile coordinates to world coordinates
                        attacker_world_x, attacker_world_y = self.calculate_missile_origin(attacker)
                        target_world_x = target['x'] * self.tile_size + self.tile_size // 2
                        target_world_y = target['y'] * self.tile_size + self.tile_size // 2
                        missile = Missile((attacker_world_x, attacker_world_y), (target_world_x, target_world_y), 10, nearest_direction)
                        self.missiles.append(missile)
            else:
                self.animation_manager.set_animation_state(attacker_unique_id, "static")
                del self.active_attacks[attacker_unique_id]
        
        # Process missiles
        for missile in self.missiles:
            missile.update()

        # Handle next_action and check for screen transitions
        next_screen = self.handle_next_action()
        if next_screen:
            return next_screen

        # Update panel animations
        self.vertical_panel.update()

    def calculate_missile_origin(self, attacker):
        angle_map_x = {0: 0, 45: 13, 90: 32, 135: 21, 180: 0, 225: -21, 270: -32, 315: -13}
        angle_map_y = {0: -7, 45: -8, 90: -16, 135: -32, 180: -32, 225: -32, 270: -16, 315: -8}
        attacker_world_x = attacker['x'] * self.tile_size + self.tile_size // 2 + angle_map_x[attacker['turret_direction']]
        attacker_world_y = attacker['y'] * self.tile_size + self.tile_size // 2 + angle_map_y[attacker['turret_direction']]
        
        return attacker_world_x,attacker_world_y

    def render(self):
        # Clear the screen before rendering
        self.screen.fill((0, 0, 0))  # Black background

        # Clear dirty rectangles from last frame
        self.dirty_rects = []

        # Add the entire visible area to dirty rects if camera moved
        if self.camera_moved:
            self.dirty_rects.append(pygame.Rect(0, 0, self.screen_width, self.screen_height))
        else:
            # Only update areas that need to be redrawn
            self.dirty_rects.append(pygame.Rect(0, 0, self.screen_width, self.screen_height))

        # Calculate visible area in tiles with extra buffer
        start_tile_x = max(0, int(self.camera_x / self.tile_size - 1))
        start_tile_y = max(0, int(self.camera_y / self.tile_size - 1))
        end_tile_x = min(self.map_width, start_tile_x + (self.camera_width // self.tile_size) + 3)
        end_tile_y = min(self.map_height, start_tile_y + (self.camera_height // self.tile_size) + 3)

        # Calculate precise pixel offsets
        offset_x = -(self.camera_x - start_tile_x * self.tile_size)
        offset_y = -(self.camera_y - start_tile_y * self.tile_size)

        # Calculate the source and destination rectangles for the map surface
        source_rect = pygame.Rect(
            start_tile_x * self.tile_size,
            start_tile_y * self.tile_size,
            (end_tile_x - start_tile_x) * self.tile_size,
            (end_tile_y - start_tile_y) * self.tile_size
        )
        dest_rect = pygame.Rect(
            int(offset_x),
            int(offset_y),
            source_rect.width,
            source_rect.height
        )

        # Blit the visible portion of the pre-rendered map
        self.screen.blit(self.map_surface, dest_rect, source_rect)

        # First pass: Draw all non-selected objects and back parts of selection rings
        objects_to_remove = []
        for obj_data in self.visible_objects_cache:
            obj = obj_data['obj']
            screen_x = obj_data['screen_x']
            screen_y = obj_data['screen_y']
            
            # Get current animation frame
            current_frame = self.animation_manager.get_next_frame(
                obj['id'],
                obj['type'],
                obj['unique_id']
            )
            
            # Check if object should be destroyed
            if current_frame == "DESTROYED" and obj.get('max_health', 100) != -1:  # Don't destroy if infinite health
                objects_to_remove.append(obj)
                continue
            
            # If no animation frame is available, use the default image
            obj_image = current_frame if current_frame else obj['image']
            
            # Get object dimensions
            obj_width = obj_image.get_width()
            obj_height = obj_image.get_height()
            
            # Add object's rectangle to dirty rects
            obj_rect = pygame.Rect(screen_x, screen_y, obj_width, obj_height)
            self.dirty_rects.append(obj_rect)
            
            # Draw selection ring behind the object if it's selected
            if self.selected_object == obj:
                ring_radius = self.selection_ring_huge_radius if obj_width == 128 else self.selection_ring_radius
                x, y = screen_x + obj_width // 2, screen_y + obj_height // 2
                rect = pygame.Rect(x - ring_radius, y - ring_radius * 0.7, ring_radius * 2, ring_radius * 1.4)
                pygame.draw.arc(self.screen, self.selection_ring_color, rect,
                              math.pi/2, 3*math.pi/2, self.selection_ring_width)
            
            # Render the object
            self.screen.blit(obj_image, (screen_x, screen_y))

        # Second pass: Draw front parts of selection rings for selected objects
        for obj_data in self.visible_objects_cache:
            obj = obj_data['obj']
            if self.selected_object == obj:
                screen_x = obj_data['screen_x']
                screen_y = obj_data['screen_y']
                
                # Get current animation frame for dimensions
                current_frame = self.animation_manager.get_current_frame(
                    obj['id'],
                    obj['type'],
                    obj['unique_id'])
                
                obj_width = current_frame.get_width() if current_frame and current_frame != "DESTROYED" else obj['image'].get_width()
                obj_height = current_frame.get_height() if current_frame and current_frame != "DESTROYED" else obj['image'].get_height()
                
                # Draw front half of selection ring
                ring_radius = self.selection_ring_huge_radius if obj_width == 128 else self.selection_ring_radius
                x, y = screen_x + obj_width // 2, screen_y + obj_height // 2
                rect = pygame.Rect(x - ring_radius, y - ring_radius * 0.7, ring_radius * 2, ring_radius * 1.4)
                pygame.draw.arc(self.screen, self.selection_ring_color, rect,
                              -math.pi/2, math.pi/2, self.selection_ring_width)
        
        # Render missiles
        for missile in self.missiles:
            missile.render(self.screen, self.missiles_images[missile.orientation // 45])
            if missile.finished:
                self.missiles.remove(missile)
            else:
                self.dirty_rects.append(pygame.Rect(missile.position[0] - 8, missile.position[1] - 8, 16, 16))

        # Remove destroyed objects
        for obj in objects_to_remove:
            if obj in self.objects:
                self.objects.remove(obj)
                self.remove_object_from_grid(obj)  # Remove from spatial grid
            if obj == self.selected_object:
                self.selected_object = None
                self.selected_object_image = None
                self.panel.set_selected_object(None)

        # Render the minimap
        self.minimap.render(self.screen, self.camera_x, self.camera_y, self.camera_width, self.camera_height)
        minimap_rect = pygame.Rect(self.minimap.x, self.minimap.y, 
                                 self.minimap.size, self.minimap.size)
        self.dirty_rects.append(minimap_rect)

        # Render the panels
        self.vertical_panel.render()
        self.panel.render()

        # Render selected object image in the horizontal panel's left area
        if self.panel.current_y < self.screen_height - self.panel.handle_height:
            # Get the left area position from the panel
            left_area_rect = self.panel.get_left_area_rect()
            
            # Adjust the y position based on the panel's current position
            left_area_rect.y = self.panel.current_y + self.panel.margin - 5
            
            # Draw the selected object image or default image
            if self.panel.selected_object_image:
                # Scale the image to fit the left area while maintaining aspect ratio
                img_width, img_height = self.panel.selected_object_image.get_size()
                scale = min(left_area_rect.width / img_width, left_area_rect.height / img_height)
                new_width = int(img_width * scale)
                new_height = int(img_height * scale)
                scaled_image = pygame.transform.scale(self.panel.selected_object_image, (new_width, new_height))
                
                # Center the image in the left area
                x = left_area_rect.x + (left_area_rect.width - new_width) // 2
                y = left_area_rect.y + (left_area_rect.height - new_height) // 2
                self.screen.blit(scaled_image, (x, y))
            else:
                # Draw the default selection image
                self.screen.blit(self.panel.default_selection, left_area_rect)
            
            # Draw the left area border on top
            self.screen.blit(self.panel.horizontal_left_area, left_area_rect)
            
            # Render panel text after drawing the selected object
            self.panel.render_text()

            # Render life bar and check if object should be destroyed
            if self.selected_object:
                if self.panel.render_life_bar(self.selected_object, left_area_rect) and self.selected_object.get('max_health', 100) != -1:  # Don't destroy if infinite health
                    # Object should be destroyed
                    self.objects.remove(self.selected_object)
                    self.remove_object_from_grid(self.selected_object)  # Remove from spatial grid
                    self.selected_object = None
                    self.selected_object_image = None

        # IMPORTANT: Call parent's render method to ensure cursor is rendered on top of everything
        # This is required because BaseScreen handles cursor rendering and we want the cursor
        # to always be visible on top of all game elements
        super().render()

        # Add cursor's dirty rectangle to the update list
        cursor_size = self.cursor_manager.cursor_size
        cursor_pos = pygame.mouse.get_pos()
        cursor_rect = pygame.Rect(
            cursor_pos[0] - cursor_size // 2,
            cursor_pos[1] - cursor_size // 2,
            cursor_size,
            cursor_size
        )
        self.dirty_rects.append(cursor_rect)

        # Update only the dirty areas of the screen
        if self.dirty_rects:
            pygame.display.update(self.dirty_rects)
        else:
            pygame.display.flip()

