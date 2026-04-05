import os

import pygame


class GameWorld:
    def __init__(self, game):
        self.game = game
        self.tile_cache = {}
        self.tiles = []
        self.map = []
        self.map_width = 120
        self.map_height = 120
        self.map_surface = None
        self.objects = []
        self.grid_cell_size = 128
        self.spatial_grid = {}

    def initialize(self):
        self.initialize_tiles()
        self.initialize_map()

    def initialize_tiles(self):
        self.tile_cache = {}
        self.tiles = []

        for index in range(20):
            try:
                tile_path = f"Maps/Common/Tiles/{index:05d}.png"
                if tile_path not in self.tile_cache:
                    tile_image = pygame.image.load(tile_path)
                    tile_image = pygame.transform.scale(
                        tile_image,
                        (self.game.tile_size, self.game.tile_size),
                    )
                    self.tile_cache[tile_path] = tile_image
                self.tiles.append(self.tile_cache[tile_path])
            except pygame.error as error:
                print(f"Error loading tile {index:05d}.png: {error}")
                default_tile = pygame.Surface((self.game.tile_size, self.game.tile_size))
                default_tile.fill((index * 10, index * 10, index * 10))
                self.tiles.append(default_tile)

    def initialize_map(self):
        map_path = os.path.join("Maps", "Battle", "map.map")
        self.map = self.load_map(map_path)
        self.map_width = len(self.map[0]) if self.map else 120
        self.map_height = len(self.map) if self.map else 120
        self.map_surface = pygame.Surface(
            (self.map_width * self.game.tile_size, self.map_height * self.game.tile_size)
        )

        for tile_y in range(self.map_height):
            for tile_x in range(self.map_width):
                tile_index = self.map[tile_y][tile_x]
                tile_image = self.tiles[tile_index] if 0 <= tile_index < len(self.tiles) else self.tiles[0]
                self.map_surface.blit(
                    tile_image,
                    (tile_x * self.game.tile_size, tile_y * self.game.tile_size),
                )

    def load_map(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = [
                    line.strip()
                    for line in file.readlines()
                    if line.strip() and not line.strip().startswith('#')
                ]

            if not lines or len(lines) < 2:
                print(f"Error: Map file is empty or missing data: {file_path}")
                return self._build_fallback_map()

            width, height = map(int, lines[0].split())

            map_data = []
            for row_index in range(height):
                if row_index + 1 >= len(lines):
                    print(f"Error: Missing row {row_index} in map data.")
                    return self._build_fallback_map()

                tile_row = self._parse_bracketed_values(lines[row_index + 1], cast=int)
                if len(tile_row) != width:
                    print(
                        f"Error: Row {row_index} has {len(tile_row)} tiles, expected {width}."
                    )
                    return self._build_fallback_map()

                map_data.append(tile_row)

            self.objects = []
            self.spatial_grid = {}
            for line in lines[height + 1 :]:
                obj_data = self._parse_bracketed_values(line)
                if len(obj_data) != 7:
                    continue

                self._create_map_object_from_data(obj_data, width, height)

            return map_data

        except FileNotFoundError:
            print(f"Map file not found: {file_path}")
            return self._build_fallback_map()
        except Exception as error:
            print(f"Error loading map: {error}")
            return self._build_fallback_map()

    def render_map(self, surface):
        start_tile_x = max(0, int(self.game.camera_x / self.game.tile_size - 1))
        start_tile_y = max(0, int(self.game.camera_y / self.game.tile_size - 1))
        end_tile_x = min(self.map_width, start_tile_x + (self.game.camera_width // self.game.tile_size) + 3)
        end_tile_y = min(self.map_height, start_tile_y + (self.game.camera_height // self.game.tile_size) + 3)

        offset_x = -(self.game.camera_x - start_tile_x * self.game.tile_size)
        offset_y = -(self.game.camera_y - start_tile_y * self.game.tile_size)

        source_rect = pygame.Rect(
            start_tile_x * self.game.tile_size,
            start_tile_y * self.game.tile_size,
            (end_tile_x - start_tile_x) * self.game.tile_size,
            (end_tile_y - start_tile_y) * self.game.tile_size,
        )
        dest_rect = pygame.Rect(int(offset_x), int(offset_y), source_rect.width, source_rect.height)

        surface.blit(self.map_surface, dest_rect, source_rect)

    def render_objects(self, surface, dirty_rects):
        objects_to_remove = []

        for obj_data in self.game.visible_objects_cache:
            obj = obj_data['obj']
            screen_x = obj_data['screen_x']
            screen_y = obj_data['screen_y']

            current_frame = self.game.animation_manager.get_next_frame(obj['id'], obj['type'], obj['unique_id'])

            if current_frame == "DESTROYED" or (
                obj['health'] <= 0 and obj.get('max_health', 100) != -1
            ):
                objects_to_remove.append(obj)
                self._erase_destroyed_object_area(surface, obj, screen_x, screen_y, dirty_rects)

                if current_frame != "DESTROYED":
                    self.game.animation_manager.set_animation_state(obj['unique_id'], "destruction")

                continue

            obj_image = current_frame if current_frame else obj['image']
            obj_rect = pygame.Rect(screen_x, screen_y, obj_image.get_width(), obj_image.get_height())
            dirty_rects.append(obj_rect)
            surface.blit(obj_image, (screen_x, screen_y))

        return objects_to_remove

    def get_grid_cell(self, world_x, world_y):
        cell_x = int(world_x // self.grid_cell_size)
        cell_y = int(world_y // self.grid_cell_size)
        return cell_x, cell_y

    def add_object_to_grid(self, obj):
        obj_world_x = obj['x'] * self.game.tile_size
        obj_world_y = obj['y'] * self.game.tile_size
        cell = self.get_grid_cell(obj_world_x, obj_world_y)
        self.spatial_grid.setdefault(cell, []).append(obj)

    def remove_object_from_grid(self, obj):
        obj_world_x = obj['x'] * self.game.tile_size
        obj_world_y = obj['y'] * self.game.tile_size
        cell = self.get_grid_cell(obj_world_x, obj_world_y)

        if cell in self.spatial_grid and obj in self.spatial_grid[cell]:
            self.spatial_grid[cell].remove(obj)
            if not self.spatial_grid[cell]:
                del self.spatial_grid[cell]

    def get_objects_at_tile(self, tile_x, tile_y):
        return [obj for obj in self.objects if obj['x'] == tile_x and obj['y'] == tile_y]

    def get_huge_objects_at_adjacent_tiles(self, tile_x, tile_y):
        huge_objects = []
        adjacent_tiles = [
            (tile_x - 1, tile_y),
            (tile_x + 1, tile_y),
            (tile_x, tile_y - 1),
            (tile_x, tile_y + 1),
        ]

        for adj_x, adj_y in adjacent_tiles:
            for obj in self.objects:
                if (
                    obj['x'] == adj_x
                    and obj['y'] == adj_y
                    and obj['image'].get_width() == 128
                    and obj['image'].get_height() == 128
                ):
                    huge_objects.append(obj)

        return huge_objects

    def get_object_by_unique_id(self, unique_id):
        for obj in self.objects:
            if obj['unique_id'] == unique_id:
                return obj
        return None

    def get_top_object_at_tile(self, tile_x, tile_y):
        objects_at_tile = self.get_objects_at_tile(tile_x, tile_y)
        if objects_at_tile:
            return max(objects_at_tile, key=lambda obj: obj['z_index'])

        huge_objects = self.get_huge_objects_at_adjacent_tiles(tile_x, tile_y)
        if huge_objects:
            return max(huge_objects, key=lambda obj: obj['z_index'])

        return None

    def remove_destroyed_objects(self, objects_to_remove):
        for obj in objects_to_remove:
            if obj not in self.objects:
                continue

            self._spawn_resource_from_destroyed_building(obj)
            self.objects.remove(obj)
            self.remove_object_from_grid(obj)
            self.game.visible_objects_cache = [
                cached for cached in self.game.visible_objects_cache if cached['obj'] != obj
            ]

            if self.game.game_selection.is_selected(obj):
                self.game.game_selection.clear_selection()

    def _spawn_resource_from_destroyed_building(self, obj):
        if obj['type'] != 'building':
            return

        metadata = self.game.object_collection.get_object_metadata(obj['type'], obj['id'])
        if not metadata or 'properties' not in metadata:
            return

        properties = metadata['properties']
        if not (properties.get('is_ore_iron', False) or properties.get('is_ore_gold', False)):
            return

        resource_id = 0 if properties.get('is_ore_iron', False) else 1
        new_resource = self.game.object_factory.create_resource_from_destroyed_building(
            obj['x'],
            obj['y'],
            resource_id,
        )
        if not new_resource:
            return

        self.objects.append(new_resource)
        self.add_object_to_grid(new_resource)

        world_x = new_resource['x'] * self.game.tile_size
        world_y = new_resource['y'] * self.game.tile_size
        screen_x = world_x - self.game.camera_x - new_resource['offset'] + self.game.tile_size // 2
        screen_y = world_y - self.game.camera_y - new_resource['offset'] + self.game.tile_size // 2

        resource_rect = pygame.Rect(
            screen_x,
            screen_y,
            new_resource['image'].get_width(),
            new_resource['image'].get_height(),
        )
        self.game.dirty_rects.append(resource_rect)

        map_area = self.map_surface.subsurface(
            pygame.Rect(world_x, world_y, self.game.tile_size, self.game.tile_size)
        ).copy()
        self.game.screen.blit(map_area, (screen_x, screen_y))

        self.game.camera_moved = True
        self.game.game_camera.update_visible_objects()

    def _erase_destroyed_object_area(self, surface, obj, screen_x, screen_y, dirty_rects):
        obj_width = obj['image'].get_width()
        obj_height = obj['image'].get_height()

        removal_rect = pygame.Rect(screen_x, screen_y, obj_width, obj_height)
        dirty_rects.append(removal_rect)

        map_area = self.map_surface.subsurface(
            pygame.Rect(screen_x + self.game.camera_x, screen_y + self.game.camera_y, obj_width, obj_height)
        ).copy()
        surface.blit(map_area, (screen_x, screen_y))

    def _build_fallback_map(self, width=120, height=120):
        return [[(x + y) % 2 for x in range(width)] for y in range(height)]

    def _parse_bracketed_values(self, line, cast=str):
        values = []
        index = 0
        while index < len(line):
            if line[index] == '[':
                end = line.find(']', index)
                if end != -1:
                    raw_value = line[index + 1 : end]
                    values.append(cast(raw_value))
                    index = end + 1
                    continue
            index += 1
        return values

    def _create_map_object_from_data(self, obj_data, width, height):
        try:
            tile_x = int(obj_data[0])
            tile_y = int(obj_data[1])
            obj_type = obj_data[2].lower()
            obj_id = int(obj_data[3])
            health = int(obj_data[4])
            z_index = int(obj_data[5])
            damage = int(obj_data[6])
            current_health = health - damage

            if not (0 <= tile_x < width and 0 <= tile_y < height):
                return

            obj = self.game.object_factory.create_map_object(
                x=tile_x,
                y=tile_y,
                obj_type=obj_type,
                obj_id=obj_id,
                current_health=current_health,
                z_index=z_index,
            )
            if obj:
                self.objects.append(obj)
                self.add_object_to_grid(obj)
            else:
                print(f"Warning: Could not find object image for {obj_type} {obj_id}")
        except ValueError as error:
            print(f"Error parsing object data: {error}")
