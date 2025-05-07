import pygame
import os
from Core.Menu.button import Button
from Core.UI.cursor_manager import CursorManager
from config import PANEL, COLORS, FONT_SIZES

class Panel:
    def __init__(self, screen, object_collection):
        self.screen = screen
        self.object_collection = object_collection
        self.width = screen.get_width()
        self.height = PANEL['height']
        self.color = COLORS['dark_gray']
        self.visible = False
        self.current_y = self.screen.get_height()
        self.handle_height = PANEL['handle_height']
        self.speed = PANEL['animation_speed']
        self.cap_width = PANEL['cap_width']
        self.arrow_width = PANEL['arrow_width']

        # Add target selection state
        self.is_targeting = False
        self.current_action = None
        self.attacker = None
        
        # Get cursor manager instance
        self.cursor_manager = CursorManager()

        # Load life bar images
        self.life_bar_left = pygame.image.load("Images/life_bar_left.png").convert_alpha()
        self.life_bar_right = pygame.image.load("Images/life_bar_right.png").convert_alpha()
        self.life_bar_energy_stretch = pygame.image.load("Images/life_bar_energy_stretch.png").convert_alpha()
        self.life_bar_energy_tip = pygame.image.load("Images/life_bar_energy_tip.png").convert_alpha()

        # Create font for life bar percentage
        self.life_bar_font = pygame.font.Font(None, FONT_SIZES['small'])

        # Add tooltip timer properties
        self.tooltip_timer = 0
        self.tooltip_delay = PANEL['tooltip']['delay']
        self.hovered_box = None

        # Add hint text properties
        self.hint_font = pygame.font.Font(None, FONT_SIZES['medium'])
        self.hint_text = "press SPACE to toggle"
        self.hint_color = COLORS['gray']
        self.hint_surface = self.hint_font.render(self.hint_text, True, self.hint_color)
        self.hint_x = (self.width - self.hint_surface.get_width()) // 2
        self.hint_y = 5

        # Add object name text properties
        self.object_name_font = pygame.font.Font(None, FONT_SIZES['large'])
        self.object_name_color = COLORS['gray']
        self.object_name_text = "No selection"
        self.object_name_surface = self.object_name_font.render(self.object_name_text, True, self.object_name_color)

        # Define areas dimensions and margins
        self.margin = PANEL['margin']
        self.left_area_size = PANEL['left_area_size']
        self.right_area_width = PANEL['right_area_width']
        self.area_height = PANEL['area_height']

        # Calculate middle area width
        self.middle_area_width = self.width - (self.left_area_size + self.right_area_width + (self.margin * 4))

        # Create surfaces for each area
        self.left_area = pygame.image.load(os.path.join('Images', 'game_menu_horizontal_left_area.png'))
        self.left_area = pygame.transform.scale(self.left_area, (self.left_area_size, self.area_height))
        self.middle_area = pygame.Surface((self.middle_area_width, self.area_height), pygame.SRCALPHA)
        self.right_area = pygame.Surface((self.right_area_width, self.area_height))
        self.right_area.fill(COLORS['black'])

        # Calculate area positions
        self.left_area_pos = (self.margin, self.margin - 5)
        self.middle_area_pos = (self.left_area_pos[0] + self.left_area_size + self.margin, self.margin + 5)
        self.right_area_pos = (self.width - self.right_area_width - self.margin, self.margin + 5)

        # Create buttons for middle area
        self.create_middle_area_buttons()

        # Load cap and middle images for panel
        self.left_cap = pygame.image.load(os.path.join('Images', 'left_horizontal_menu_cap.png'))
        self.left_cap = pygame.transform.scale(self.left_cap, (self.cap_width, self.height))
        self.right_cap = pygame.image.load(os.path.join('Images', 'right_horizontal_menu_cap.png'))
        self.right_cap = pygame.transform.scale(self.right_cap, (self.cap_width, self.height))
        self.middle = pygame.image.load(os.path.join('Images', 'middle_horizontal_menu.png'))
        self.middle = pygame.transform.scale(self.middle, (1, self.height))

        # Load handle images
        self.handle_left_cap = pygame.image.load(os.path.join('Images', 'left_horizontal_handle_cap.png'))
        self.handle_left_cap = pygame.transform.scale(self.handle_left_cap, (self.cap_width, self.handle_height))
        self.handle_right_cap = pygame.image.load(os.path.join('Images', 'right_horizontal_handle_cap.png'))
        self.handle_right_cap = pygame.transform.scale(self.handle_right_cap, (self.cap_width, self.handle_height))
        self.handle_middle = pygame.image.load(os.path.join('Images', 'middle_horizontal_handle.png'))
        self.handle_middle = pygame.transform.scale(self.handle_middle, (1, self.handle_height))
        self.handle_arrow_open = pygame.image.load(os.path.join('Images', 'middle_horizontal_handle_open.png'))
        self.handle_arrow_open = pygame.transform.scale(self.handle_arrow_open, (self.arrow_width, self.handle_height))
        self.handle_arrow_close = pygame.image.load(os.path.join('Images', 'middle_horizontal_handle_close.png'))
        self.handle_arrow_close = pygame.transform.scale(self.handle_arrow_close, (self.arrow_width, self.handle_height))

        # Tooltip properties
        self.tooltip_font = pygame.font.Font(None, FONT_SIZES['small'])
        self.tooltip_padding = PANEL['tooltip']['padding']
        self.tooltip_margin = PANEL['tooltip']['margin']
        self.tooltip_bg_color = PANEL['tooltip']['bg_color']
        self.tooltip_text_color = PANEL['tooltip']['text_color']
        self.tooltip_border_color = PANEL['tooltip']['border_color']
        self.tooltip_border_width = PANEL['tooltip']['border_width']
        self.current_tooltip = None

        # Create cached surfaces
        self.create_cached_surfaces()

        # ... existing code ... 