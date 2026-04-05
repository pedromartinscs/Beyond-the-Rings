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
        self._render_selected_object_image(left_area_rect)
        self.screen.blit(self.horizontal_left_area, left_area_rect)
        self._render_object_name(current_y)

        if not selected_object:
            return False

        return self.status_bars.render(selected_object, left_area_rect)

    def _render_selected_object_image(self, left_area_rect):
        if not self.selected_object_image:
            self.screen.blit(self.default_selection, left_area_rect)
            return

        img_width, img_height = self.selected_object_image.get_size()
        scale = min(left_area_rect.width / img_width, left_area_rect.height / img_height)
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        scaled_image = pygame.transform.scale(self.selected_object_image, (new_width, new_height))

        x = left_area_rect.x + (left_area_rect.width - new_width) // 2
        y = left_area_rect.y + (left_area_rect.height - new_height) // 2
        self.screen.blit(scaled_image, (x, y))

    def _render_object_name(self, current_y):
        name_x = self.left_area_pos[0] + (self.left_area_size - self.object_name_surface.get_width()) // 2
        name_y = current_y + self.left_area_pos[1] + self.area_height - 20
        self.screen.blit(self.object_name_surface, (name_x, name_y))
