import math

import pygame


class GameSelection:
    def __init__(self, game):
        self.game = game
        self._selected_object = None
        self.ring_color = (255, 255, 0)
        self.ring_width = 2
        self.ring_radius = 20
        self.ring_huge_radius = 40

    @property
    def selected_object(self):
        return self._selected_object

    def set_selected_object(self, obj):
        self._selected_object = obj
        self._sync_interface_selection(obj)
        return obj

    def clear_selection(self):
        self._selected_object = None
        self._sync_interface_selection(None)

    def is_selected(self, obj):
        return self._selected_object == obj

    def get_object_at_screen_position(self, screen_x, screen_y):
        tile_x, tile_y = self.game.game_camera.get_tile_from_screen_pos(screen_x, screen_y)
        return self.game.game_world.get_top_object_at_tile(tile_x, tile_y)

    def select_object_at_screen_position(self, screen_x, screen_y):
        selected_object = self.get_object_at_screen_position(screen_x, screen_y)
        return self.set_selected_object(selected_object)

    def render_back_overlay(self, surface, visible_objects_cache, dirty_rects):
        for obj_data in visible_objects_cache:
            obj = obj_data["obj"]
            if not self.is_selected(obj):
                continue

            image = self._get_current_render_image(obj)
            if image == "DESTROYED":
                continue

            self._draw_object_ring_half(surface, obj_data, image, dirty_rects, is_front_half=False)

    def render_front_overlay(self, surface, visible_objects_cache, objects_to_remove, dirty_rects):
        for obj_data in visible_objects_cache:
            obj = obj_data["obj"]
            if obj in objects_to_remove or not self.is_selected(obj):
                continue

            image = self._get_current_render_image(obj)
            if image == "DESTROYED":
                continue

            self._draw_object_ring_half(surface, obj_data, image, dirty_rects, is_front_half=True)

    def _get_current_render_image(self, obj):
        current_frame = self.game.animation_manager.get_current_frame(
            obj["id"],
            obj["type"],
            obj["unique_id"],
        )
        return current_frame if current_frame else obj["image"]

    def _draw_object_ring_half(self, surface, obj_data, image, dirty_rects, is_front_half):
        screen_x = obj_data["screen_x"]
        screen_y = obj_data["screen_y"]
        obj_width = image.get_width()
        obj_height = image.get_height()

        ring_radius = self.ring_huge_radius if obj_width == 128 else self.ring_radius
        center_x = screen_x + obj_width // 2
        center_y = screen_y + obj_height // 2
        rect = pygame.Rect(
            center_x - ring_radius,
            center_y - int(ring_radius * 0.7),
            ring_radius * 2,
            int(ring_radius * 1.4),
        )

        if is_front_half:
            start_angle, end_angle = -math.pi / 2, math.pi / 2
        else:
            start_angle, end_angle = math.pi / 2, 3 * math.pi / 2

        pygame.draw.arc(surface, self.ring_color, rect, start_angle, end_angle, self.ring_width)
        dirty_rects.append(rect)

    def _sync_interface_selection(self, obj):
        if hasattr(self.game, "game_interface"):
            self.game.game_interface.set_selected_object(obj)
