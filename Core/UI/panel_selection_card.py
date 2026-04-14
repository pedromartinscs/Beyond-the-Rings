import os

import pygame

from config import COLORS, FONT_SIZES
from Core.UI.panel_status_bars import PanelStatusBars


class PanelSelectionCard:
    def __init__(self, screen, left_area_size, area_height, left_area_pos, margin):
        self.screen = screen
        self.left_area_size = left_area_size
        self.area_height = area_height
        self.left_area_pos = left_area_pos
        self.margin = margin

        self.object_name_font = pygame.font.Font(None, FONT_SIZES['large'])
        self.object_name_color = COLORS['gray']
        self.object_name_text = "No selection"
        self.object_name_surface = self.object_name_font.render(
            self.object_name_text,
            True,
            self.object_name_color,
        )

        self.horizontal_left_area = pygame.image.load("Images/game_menu_horizontal_left_area.png").convert_alpha()
        self.default_selection = pygame.image.load("Images/default_selection.png").convert_alpha()
        self.selected_object_image = self.default_selection
        self.status_bars = PanelStatusBars(screen, left_area_size)

        self.selection_image_size = 150
        self.queue_thumbnail_size = 20
        self.queue_thumbnail_gap = 5
        self.queue_thumbnail_margin = 2
        self.queue_thumbnail_cache = {}

    def set_selected_object(self, obj):
        if obj:
            self.object_name_text = obj.get('name', 'Unknown')
            self.object_name_surface = self.object_name_font.render(
                self.object_name_text,
                True,
                self.object_name_color,
            )
            self.selected_object_image = self._load_selected_object_image(obj)
        else:
            self.object_name_text = "No selection"
            self.object_name_surface = self.object_name_font.render(
                self.object_name_text,
                True,
                self.object_name_color,
            )
            self.selected_object_image = self.default_selection

    def _load_selected_object_image(self, obj):
        try:
            image_path = os.path.join("Images", f"{obj['type']}{obj['id']:05d}.png")
            if os.path.exists(image_path):
                return pygame.image.load(image_path).convert_alpha()
        except Exception:
            pass
        return self.default_selection

    def get_left_area_rect(self, current_y):
        return pygame.Rect(
            self.left_area_pos[0],
            current_y + self.left_area_pos[1],
            self.left_area_size,
            self.area_height,
        )

    def render(self, current_y, handle_height, selected_object):
        if current_y >= self.screen.get_height() - handle_height:
            return False

        left_area_rect = self.get_left_area_rect(current_y)
        selection_image_rect = self.get_selection_image_rect(left_area_rect)
        self._render_selected_object_image(selection_image_rect)
        self.screen.blit(self.horizontal_left_area, left_area_rect)
        self._render_queue_thumbnails(selection_image_rect, selected_object)
        self._render_object_name(current_y)

        if not selected_object:
            return False

        return self.status_bars.render(selected_object, left_area_rect)

    def _render_selected_object_image(self, selection_image_rect):
        if not self.selected_object_image:
            self.screen.blit(self.default_selection, selection_image_rect)
            return

        img_width, img_height = self.selected_object_image.get_size()
        scale = min(selection_image_rect.width / img_width, selection_image_rect.height / img_height)
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        scaled_image = pygame.transform.scale(self.selected_object_image, (new_width, new_height))

        x = selection_image_rect.x + (selection_image_rect.width - new_width) // 2
        y = selection_image_rect.y + (selection_image_rect.height - new_height) // 2
        self.screen.blit(scaled_image, (x, y))

    def get_selection_image_rect(self, left_area_rect):
        x = left_area_rect.x + (left_area_rect.width - self.selection_image_size) // 2
        y = left_area_rect.y + (left_area_rect.height - self.selection_image_size) // 2
        return pygame.Rect(x, y, self.selection_image_size, self.selection_image_size)

    def get_queue_thumbnail_rects(self, current_y, handle_height, selected_object):
        if current_y >= self.screen.get_height() - handle_height:
            return []

        production_queue = (selected_object or {}).get('production_queue', [])
        if not production_queue:
            return []

        left_area_rect = self.get_left_area_rect(current_y)
        selection_image_rect = self.get_selection_image_rect(left_area_rect)
        thumbnail_rects = []
        start_x = (
            selection_image_rect.right
            - self.queue_thumbnail_margin
            - self.queue_thumbnail_size
        )
        y = selection_image_rect.y + self.queue_thumbnail_margin

        for index in range(min(len(production_queue), 6)):
            x = start_x - index * (self.queue_thumbnail_size + self.queue_thumbnail_gap)
            thumbnail_rects.append(
                pygame.Rect(x, y, self.queue_thumbnail_size, self.queue_thumbnail_size)
            )

        return thumbnail_rects

    def get_queue_thumbnail_index_at_position(self, current_y, handle_height, selected_object, mouse_pos):
        for index, thumbnail_rect in enumerate(
            self.get_queue_thumbnail_rects(current_y, handle_height, selected_object)
        ):
            if thumbnail_rect.collidepoint(mouse_pos):
                return index
        return None

    def _render_queue_thumbnails(self, selection_image_rect, selected_object):
        production_queue = (selected_object or {}).get('production_queue', [])
        if not production_queue:
            return

        start_x = (
            selection_image_rect.right
            - self.queue_thumbnail_margin
            - self.queue_thumbnail_size
        )
        y = selection_image_rect.y + self.queue_thumbnail_margin

        for index, queue_item in enumerate(production_queue[:6]):
            thumbnail_surface = self._load_queue_thumbnail_surface(queue_item)
            if not thumbnail_surface:
                continue

            x = start_x - index * (self.queue_thumbnail_size + self.queue_thumbnail_gap)
            self.screen.blit(thumbnail_surface, (x, y))

    def _load_queue_thumbnail_surface(self, queue_item):
        cache_key = (
            queue_item.get('thumbnail_name'),
            queue_item.get('unit_type'),
            queue_item.get('unit_id'),
        )
        if cache_key in self.queue_thumbnail_cache:
            return self.queue_thumbnail_cache[cache_key]

        thumbnail_surface = None
        thumbnail_name = queue_item.get('thumbnail_name')
        if thumbnail_name:
            image_path = os.path.join('Images', f'{thumbnail_name}.png')
            if os.path.exists(image_path):
                thumbnail_surface = pygame.image.load(image_path).convert_alpha()

        if thumbnail_surface is None:
            unit_type = queue_item.get('unit_type')
            unit_id = queue_item.get('unit_id')
            if unit_type is not None and unit_id is not None:
                try:
                    image_path = os.path.join('Images', f'{unit_type}{unit_id:05d}.png')
                    if os.path.exists(image_path):
                        thumbnail_surface = pygame.image.load(image_path).convert_alpha()
                except Exception:
                    thumbnail_surface = None

        if thumbnail_surface is None:
            thumbnail_surface = self.default_selection.copy()

        thumbnail_surface = pygame.transform.scale(
            thumbnail_surface,
            (self.queue_thumbnail_size, self.queue_thumbnail_size),
        )
        self.queue_thumbnail_cache[cache_key] = thumbnail_surface
        return thumbnail_surface

    def _render_object_name(self, current_y):
        name_x = self.left_area_pos[0] + (self.left_area_size - self.object_name_surface.get_width()) // 2
        name_y = current_y + self.left_area_pos[1] + self.area_height - 20
        self.screen.blit(self.object_name_surface, (name_x, name_y))
