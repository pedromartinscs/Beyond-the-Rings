from typing import Optional

import pygame

from Core.UI.cursor_manager import CursorManager
from Core.UI.panel_action_grid import PanelActionGrid
from Core.UI.panel_selection_card import PanelSelectionCard
from config import COLORS, FONT_SIZES, PANEL


class Panel:
    def __init__(self, screen, object_collection):
        self.screen = screen
        self.object_collection = object_collection
        self.width = screen.get_width()
        self.height = PANEL['height']
        self.color = COLORS['dark_gray']
        self.is_open = False
        self.current_y = self.screen.get_height()
        self.handle_height = PANEL['handle_height']
        self.speed = PANEL['animation_speed']
        self.cap_width = PANEL['cap_width']
        self.arrow_width = PANEL['arrow_width']

        self.is_targeting = False
        self.current_action = None
        self.attacker = None
        self.selected_object = None

        self.cursor_manager = CursorManager()

        self.tooltip_timer = 0
        self.tooltip_delay = PANEL['tooltip']['delay']
        self.hovered_box = None

        self.hint_font = pygame.font.Font(None, FONT_SIZES['medium'])
        self.hint_text = "press SPACE to toggle"
        self.hint_color = COLORS['gray']
        self.hint_surface = self.hint_font.render(self.hint_text, True, self.hint_color)
        self.hint_x = (self.width - self.hint_surface.get_width()) // 2
        self.hint_y = 5

        self.margin = PANEL['margin']
        self.left_area_size = PANEL['left_area_size']
        self.right_area_width = PANEL['right_area_width']
        self.area_height = PANEL['area_height']
        self.middle_area_width = self.width - (
            self.left_area_size + self.right_area_width + (self.margin * 4)
        )

        self.left_area = pygame.image.load('Images/game_menu_horizontal_left_area.png').convert_alpha()
        self.left_area = pygame.transform.scale(self.left_area, (self.left_area_size, self.area_height))
        self.middle_area = pygame.Surface((self.middle_area_width, self.area_height), pygame.SRCALPHA)
        self.right_area = pygame.Surface((self.right_area_width, self.area_height))
        self.right_area.fill(COLORS['black'])

        self.left_area_pos = (self.margin, self.margin - 5)
        self.middle_area_pos = (self.left_area_pos[0] + self.left_area_size + self.margin, self.margin + 5)
        self.right_area_pos = (self.width - self.right_area_width - self.margin, self.margin + 5)

        self.action_grid = PanelActionGrid(self.middle_area_width, object_collection)
        self.selection_card = PanelSelectionCard(
            screen,
            self.left_area_size,
            self.area_height,
            self.left_area_pos,
            self.margin,
        )

        self.left_cap = pygame.image.load('Images/left_horizontal_menu_cap.png').convert_alpha()
        self.left_cap = pygame.transform.scale(self.left_cap, (self.cap_width, self.height))
        self.right_cap = pygame.image.load('Images/right_horizontal_menu_cap.png').convert_alpha()
        self.right_cap = pygame.transform.scale(self.right_cap, (self.cap_width, self.height))
        self.middle = pygame.image.load('Images/middle_horizontal_menu.png').convert_alpha()
        self.middle = pygame.transform.scale(self.middle, (1, self.height))

        self.handle_left_cap = pygame.image.load('Images/left_horizontal_handle_cap.png').convert_alpha()
        self.handle_left_cap = pygame.transform.scale(self.handle_left_cap, (self.cap_width, self.handle_height))
        self.handle_right_cap = pygame.image.load('Images/right_horizontal_handle_cap.png').convert_alpha()
        self.handle_right_cap = pygame.transform.scale(self.handle_right_cap, (self.cap_width, self.handle_height))
        self.handle_middle = pygame.image.load('Images/middle_horizontal_handle.png').convert_alpha()
        self.handle_middle = pygame.transform.scale(self.handle_middle, (1, self.handle_height))
        self.handle_arrow_open = pygame.image.load('Images/middle_horizontal_handle_open.png').convert_alpha()
        self.handle_arrow_open = pygame.transform.scale(self.handle_arrow_open, (self.arrow_width, self.handle_height))
        self.handle_arrow_close = pygame.image.load('Images/middle_horizontal_handle_close.png').convert_alpha()
        self.handle_arrow_close = pygame.transform.scale(self.handle_arrow_close, (self.arrow_width, self.handle_height))

        self.tooltip_font = pygame.font.Font(None, FONT_SIZES['small'])
        self.tooltip_padding = PANEL['tooltip']['padding']
        self.tooltip_margin = PANEL['tooltip']['margin']
        self.tooltip_bg_color = PANEL['tooltip']['bg_color']
        self.tooltip_text_color = PANEL['tooltip']['text_color']
        self.tooltip_border_color = PANEL['tooltip']['border_color']
        self.tooltip_border_width = PANEL['tooltip']['border_width']
        self.current_tooltip = None

        self.create_cached_surfaces()

    def show(self):
        self.is_open = True

    def hide(self):
        self.is_open = False

    def toggle(self):
        self.is_open = not self.is_open

    def is_handle_clicked(self, pos):
        if self.is_open or self.current_y < self.screen.get_height() - self.handle_height:
            handle_y = self.current_y - self.handle_height
        else:
            handle_y = self.screen.get_height() - self.handle_height

        handle_rect = pygame.Rect(0, handle_y, self.width, self.handle_height)
        return handle_rect.collidepoint(pos)

    def animate_panel(self, target_y):
        if self.is_open:
            self.current_y = max(target_y, self.current_y - self.speed)
        else:
            self.current_y = min(target_y, self.current_y + self.speed)

    def render(self):
        if self.is_open:
            target_y = self.screen.get_height() - self.height
        else:
            target_y = self.screen.get_height() - self.handle_height

        self.animate_panel(target_y)

        if self.is_open or self.current_y < self.screen.get_height() - self.handle_height:
            self.screen.blit(self.base_surface, (0, self.current_y))
            self.screen.blit(self.hint_surface, (self.hint_x, self.current_y + self.hint_y))

            panel_y = self.current_y
            self.screen.blit(self.left_area, (self.left_area_pos[0], panel_y + self.left_area_pos[1]))

            middle_x = self.middle_area_pos[0]
            middle_y = panel_y + self.middle_area_pos[1]
            self.screen.blit(self.middle_area, (middle_x, middle_y))
            self.action_grid.render(self.screen, middle_x, middle_y)
            self.current_tooltip = self.action_grid.current_tooltip

        if self.is_open or self.current_y < self.screen.get_height() - self.handle_height:
            handle_y = self.current_y - self.handle_height
        else:
            handle_y = self.screen.get_height() - self.handle_height

        handle_image = self.handle_close_surface if self.is_open else self.handle_open_surface
        self.screen.blit(handle_image, (0, handle_y))

    def handle_events(self, event: pygame.event.Event) -> Optional[str]:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.toggle()
                return "panel_toggled"

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            if self.is_handle_clicked(mouse_pos):
                self.toggle()
                return "panel_toggled"

            middle_x = self.middle_area_pos[0]
            middle_y = self.current_y + self.middle_area_pos[1]
            clicked_box = self.action_grid.get_clicked_box(mouse_pos, middle_x, middle_y)
            if clicked_box:
                self.handle_button_click(clicked_box)
                return "button_clicked"

        return None

    def create_cached_surfaces(self):
        self.base_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.base_surface.blit(self.left_cap, (0, 0))

        for x in range(self.cap_width, self.width - self.cap_width):
            self.base_surface.blit(self.middle, (x, 0))

        self.base_surface.blit(self.right_cap, (self.width - self.cap_width, 0))

        self.handle_open_surface = pygame.Surface((self.width, self.handle_height), pygame.SRCALPHA)
        self.handle_close_surface = pygame.Surface((self.width, self.handle_height), pygame.SRCALPHA)
        self.handle_open_surface.blit(self.handle_left_cap, (0, 0))
        self.handle_close_surface.blit(self.handle_left_cap, (0, 0))

        for x in range(self.cap_width, self.width - self.cap_width):
            self.handle_open_surface.blit(self.handle_middle, (x, 0))
            self.handle_close_surface.blit(self.handle_middle, (x, 0))

        self.handle_open_surface.blit(self.handle_right_cap, (self.width - self.cap_width, 0))
        self.handle_close_surface.blit(self.handle_right_cap, (self.width - self.cap_width, 0))

        arrow_x = (self.width - self.arrow_width) // 2
        self.handle_open_surface.blit(self.handle_arrow_open, (arrow_x, 0))
        self.handle_close_surface.blit(self.handle_arrow_close, (arrow_x, 0))

    def handle_button_click(self, box):
        if not box or 'action' not in box:
            return

        action = box['action']

        if action == 'attack':
            if not self.selected_object:
                return

            self.is_targeting = True
            self.current_action = 'attack'
            self.attacker = self.selected_object
            self.cursor_manager.set_cursor('aim')
        elif action == 'build':
            self.is_targeting = True
            self.current_action = 'build'
            self.cursor_manager.set_cursor('build')
        elif action == 'builder_unit':
            self.game.handle_builder_unit_action(self.selected_object)
        elif action == 'cancel':
            self.cancel_targeting()
        elif action == 'destroy':
            if not self.selected_object:
                return

            self.selected_object['health'] = 0
            self.selected_object = None
            self.set_selected_object(None)
        elif action == 'halt':
            if not self.selected_object:
                return
            self.selected_object['is_attacking'] = False

    def cancel_targeting(self):
        self.is_targeting = False
        self.current_action = None
        self.attacker = None
        self.cursor_manager.set_cursor('normal')

    def handle_target_selection(self, target_object):
        if not self.is_targeting or not target_object or not self.attacker:
            return

        if self.current_action == 'attack':
            dx = target_object['x'] - self.attacker['x']
            dy = target_object['y'] - self.attacker['y']
            distance = (dx * dx + dy * dy) ** 0.5

            metadata = self.object_collection.get_object_metadata(self.attacker['type'], self.attacker['id'])
            properties = metadata.get('properties', {}) if metadata else {}
            attack_range = properties.get('attack_range', 0)

            if distance <= attack_range:
                result = {
                    'action': 'attack',
                    'attacker': self.attacker,
                    'target': target_object,
                    'in_range': True,
                }
                self.cancel_targeting()
                return result

            if metadata and metadata.get('is_unit', False):
                return {
                    'action': 'attack',
                    'attacker': self.attacker,
                    'target': target_object,
                    'in_range': False,
                    'is_unit': True,
                }

            return {
                'action': 'attack',
                'attacker': self.attacker,
                'target': target_object,
                'in_range': False,
                'is_unit': False,
            }

        if self.current_action == 'builder_unit':
            result = {
                'action': 'build',
                'position': (target_object['x'], target_object['y']),
            }
            self.cancel_targeting()
            return result

    def set_selected_object(self, obj):
        self.selected_object = obj
        self.selection_card.set_selected_object(obj)
        self.action_grid.update_for_object(obj)

    def render_selected_object_card(self, selected_object):
        return self.selection_card.render(self.current_y, self.handle_height, selected_object)

    def get_current_y(self):
        return self.current_y
