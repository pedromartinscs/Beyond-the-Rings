import pygame


class GameCamera:
    def __init__(self, game):
        self.game = game

    def initialize(self):
        self.game.camera_x = 0
        self.game.camera_y = 0
        self.game.camera_speed = 3
        self.game.camera_width = self.game.screen_width
        self.game.camera_height = self.game.screen_height

    def get_tile_from_screen_pos(self, screen_x, screen_y):
        world_x = screen_x + self.game.camera_x
        world_y = screen_y + self.game.camera_y
        tile_x = world_x // self.game.tile_size
        tile_y = world_y // self.game.tile_size
        return tile_x, tile_y

    def center_on_world_position(self, world_x, world_y):
        self.game.camera_x = max(
            0,
            min(
                world_x - self.game.camera_width // 2,
                self.game.map_width * self.game.tile_size - self.game.camera_width,
            ),
        )
        self.game.camera_y = max(
            0,
            min(
                world_y - self.game.camera_height // 2,
                self.game.map_height * self.game.tile_size - self.game.camera_height,
            ),
        )

        self.game.camera_moved = True
        self.update_visible_area()
        self.update_visible_objects()

    def update_visible_area(self):
        self.game.visible_area = pygame.Rect(
            self.game.camera_x,
            self.game.camera_y,
            self.game.camera_width,
            self.game.camera_height,
        )

    def update_visible_objects(self):
        if not self.game.camera_moved:
            return

        self.game.visible_objects_cache = []

        visible_left = self.game.camera_x - 100
        visible_right = self.game.camera_x + self.game.screen_width + 100
        visible_top = self.game.camera_y - 100
        visible_bottom = self.game.camera_y + self.game.screen_height + 100

        start_cell = self.game.game_world.get_grid_cell(visible_left, visible_top)
        end_cell = self.game.game_world.get_grid_cell(visible_right, visible_bottom)

        tile_size = self.game.tile_size
        half_tile = tile_size // 2
        camera_x = self.game.camera_x
        camera_y = self.game.camera_y
        screen_width = self.game.screen_width
        screen_height = self.game.screen_height

        for cell_x in range(start_cell[0], end_cell[0] + 1):
            for cell_y in range(start_cell[1], end_cell[1] + 1):
                cell = (cell_x, cell_y)
                if cell in self.game.spatial_grid:
                    for obj in self.game.spatial_grid[cell]:
                        obj_world_x = obj['x'] * tile_size
                        obj_world_y = obj['y'] * tile_size

                        obj_width = obj['image'].get_width()
                        obj_height = obj['image'].get_height()

                        if (
                            obj_world_x + obj_width < visible_left
                            or obj_world_x > visible_right
                            or obj_world_y + obj_height < visible_top
                            or obj_world_y > visible_bottom
                        ):
                            continue

                        obj_screen_x = obj_world_x - camera_x
                        obj_screen_y = obj_world_y - camera_y

                        offset = obj['offset'] - half_tile

                        final_x = obj_screen_x - offset
                        final_y = obj_screen_y - offset

                        if (
                            final_x + obj_width > 0
                            and final_x < screen_width
                            and final_y + obj_height > 0
                            and final_y < screen_height
                        ):
                            self.game.visible_objects_cache.append(
                                {
                                    'obj': obj,
                                    'screen_x': final_x,
                                    'screen_y': final_y,
                                }
                            )

        self.game.visible_objects_cache.sort(
            key=lambda x: (x['obj']['z_index'], x['obj']['y'], x['obj']['x'])
        )
        self.game.camera_moved = False

    def update_edge_scroll(self, mouse_pos):
        edge_area = 50
        move_speed = 15

        old_camera_x = self.game.camera_x
        old_camera_y = self.game.camera_y

        max_camera_x = self.game.map_width * self.game.tile_size - self.game.screen_width
        max_camera_y = self.game.map_height * self.game.tile_size - self.game.screen_height

        if mouse_pos[0] < edge_area:
            self.game.camera_x = max(0, self.game.camera_x - move_speed)
        elif mouse_pos[0] > self.game.screen_width - edge_area:
            self.game.camera_x = min(max_camera_x, self.game.camera_x + move_speed)

        if mouse_pos[1] < edge_area:
            self.game.camera_y = max(0, self.game.camera_y - move_speed)
        elif mouse_pos[1] > self.game.screen_height - edge_area:
            self.game.camera_y = min(max_camera_y, self.game.camera_y + move_speed)

        if old_camera_x != self.game.camera_x or old_camera_y != self.game.camera_y:
            self.game.camera_moved = True
            self.update_visible_area()
            self.update_visible_objects()
