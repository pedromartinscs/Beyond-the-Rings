import pygame
import os
from Core.UI.button import Button
from Core.UI.cursor_manager import CursorManager
from config import PANEL, COLORS, FONT_SIZES
from typing import Optional

class Panel:
    def __init__(self, screen, object_collection):
        self.screen = screen
        self.object_collection = object_collection
        self.width = screen.get_width()
        self.height = PANEL['height']
        self.color = COLORS['dark_gray']
        self.is_open = False  # Changed from visible to is_open
        self.current_y = self.screen.get_height()
        self.handle_height = PANEL['handle_height']
        self.speed = PANEL['animation_speed']
        self.cap_width = PANEL['cap_width']
        self.arrow_width = PANEL['arrow_width']

        # Add target selection state
        self.is_targeting = False
        self.current_action = None
        self.attacker = None
        self.selected_object = None  # Add selected_object attribute
        
        # Get cursor manager instance
        self.cursor_manager = CursorManager()

        # Load life bar images
        self.life_bar_left = pygame.image.load("Images/life_bar_left.png").convert_alpha()
        self.life_bar_right = pygame.image.load("Images/life_bar_right.png").convert_alpha()
        self.life_bar_energy_stretch = pygame.image.load("Images/life_bar_energy_stretch.png").convert_alpha()
        self.life_bar_energy_tip = pygame.image.load("Images/life_bar_energy_tip.png").convert_alpha()
        # Load charge bar images
        self.life_bar_charge_stretch = pygame.image.load("Images/life_bar_charge_stretch.png").convert_alpha()
        self.life_bar_charge_tip = pygame.image.load("Images/life_bar_charge_tip.png").convert_alpha()

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

        # Load panel images for selected object display
        self.horizontal_left_area = pygame.image.load("Images/game_menu_horizontal_left_area.png").convert_alpha()
        self.default_selection = pygame.image.load("Images/default_selection.png").convert_alpha()
        self.selected_object_image = None  # Will store the selected object's image

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

    def create_middle_area_buttons(self):
        """Create buttons for the middle area of the panel"""
        # Button dimensions
        button_width = 32
        button_height = 32
        
        # Grid dimensions
        max_rows = 4
        max_cols = 6
        total_buttons = 12  # Maximum number of buttons
        
        # Calculate spacing between buttons
        spacing_x = 8  # Fixed spacing between buttons
        spacing_y = 8  # Fixed spacing between rows
        
        # Calculate actual number of columns needed (up to max_cols)
        actual_cols = min(max_cols, total_buttons)
        
        # Calculate column positions and box width
        total_width = self.middle_area_width - (spacing_x * (actual_cols - 1))
        box_width = (total_width - (button_width * actual_cols)) // actual_cols
        
        # Calculate starting x position to center the buttons
        start_x = (self.middle_area_width - (actual_cols * (button_width + box_width + spacing_x) - spacing_x)) // 2
        start_y = 30
        
        # Create fonts for title and description
        self.title_font = pygame.font.Font(None, 16)  # Bold font for title
        self.description_font = pygame.font.Font(None, 14)  # Regular font for description
        
        # Box color and margin
        self.box_color = (48, 82, 101)
        self.box_margin = 1
        
        # Initialize empty lists for buttons and boxes
        self.middle_buttons = []
        self.description_boxes = []

    def update_buttons_for_object(self, selected_object):
        """Update buttons based on the selected object's JSON data"""
        # Clear existing buttons and boxes
        self.middle_buttons = []
        self.description_boxes = []
        
        if not selected_object:
            # If no object is selected, don't show any buttons
            return
            
        # Get object metadata
        metadata = self.object_collection.get_object_metadata(selected_object['type'], selected_object['id'])
        if not metadata or 'buttons' not in metadata or not metadata['buttons']:
            # If no buttons found in metadata, don't show any buttons
            return
            
        # Button dimensions and layout
        button_width = 32
        button_height = 32
        spacing_x = 8
        spacing_y = 8
        max_cols = 6
        
        # Calculate layout
        total_buttons = len(metadata['buttons'])
        if total_buttons == 0:
            return
            
        actual_cols = min(max_cols, total_buttons)
        if actual_cols == 0:
            return
            
        total_width = self.middle_area_width - (spacing_x * (actual_cols - 1))
        box_width = (total_width - (button_width * actual_cols)) // actual_cols
        
        # Calculate starting position
        start_x = (self.middle_area_width - (actual_cols * (button_width + box_width + spacing_x) - spacing_x)) // 2
        start_y = 30
        
        # Create fonts for title and description
        self.title_font = pygame.font.Font(None, 16)  # Bold font for title
        self.description_font = pygame.font.Font(None, 14)  # Regular font for description
        
        # Box color and margin
        self.box_color = (48, 82, 101)
        self.box_margin = 1
        
        # Create buttons for each action in the JSON
        for i, button_data in enumerate(metadata['buttons']):
            # Calculate position
            col = i % actual_cols
            row = i // actual_cols
            x = start_x + col * (button_width + spacing_x + box_width)
            y = start_y + row * (button_height + spacing_y)
            
            # Try to load action-specific button images
            action = button_data['action']
            default_button = "Images/tiny_button_basic.png"
            default_button_hover = "Images/tiny_button_basic_hover.png"
            
            # Construct paths for action-specific button images
            action_button = f"Images/{action}_tiny_button_basic.png"
            action_button_hover = f"Images/{action}_tiny_button_basic_hover.png"
            
            # Check if action-specific images exist
            button_image = action_button if os.path.exists(action_button) else default_button
            button_hover_image = action_button_hover if os.path.exists(action_button_hover) else default_button_hover
            
            # Create button
            button = Button(
                x, y, 0, 0, button_width, button_height,
                "", None,  # No text or action for now
                button_image,
                button_hover_image
            )
            
            # Create description box
            box = {
                'rect': pygame.Rect(x + button_width + self.box_margin, y, box_width, button_height),
                'title': button_data['name'],
                'description': button_data['description'],
                'button': button,
                'action': button_data['action'],
                'lines': [],  # Will store wrapped description lines
                'is_wrapped': False  # Flag to track if description was wrapped
            }
            
            # Create description surface
            box['surface'] = pygame.Surface((box_width, button_height), pygame.SRCALPHA)
            box['surface'].fill(self.box_color)
            
            # Render title and description
            title_surface = self.title_font.render(box['title'], True, (255, 255, 255))
            desc_surface = self.description_font.render(box['description'], True, (200, 200, 200))
            
            # Center text in box
            title_x = (box_width - title_surface.get_width()) // 2
            desc_x = (box_width - desc_surface.get_width()) // 2
            title_y = 5
            desc_y = title_y + title_surface.get_height() + 2
            
            box['surface'].blit(title_surface, (title_x, title_y))
            box['surface'].blit(desc_surface, (desc_x, desc_y))
            
            self.middle_buttons.append(button)
            self.description_boxes.append(box)

    def show(self):
        """Show the panel (slide it in)"""
        self.is_open = True

    def hide(self):
        """Hide the panel (slide it out)"""
        self.is_open = False

    def toggle(self):
        """Toggle the panel open/closed state"""
        self.is_open = not self.is_open

    def is_handle_clicked(self, pos):
        """Check if the click position is within the handle area"""
        mouse_x, mouse_y = pos
        
        # Calculate handle position
        if self.is_open or self.current_y < self.screen.get_height() - self.handle_height:
            # When panel is visible or animating, handle follows panel
            handle_y = self.current_y - self.handle_height
        else:
            # When panel is fully hidden, handle touches bottom of screen
            handle_y = self.screen.get_height() - self.handle_height
            
        # Check if the click is within the handle area
        handle_rect = pygame.Rect(0, handle_y, self.width, self.handle_height)
        return handle_rect.collidepoint(pos)

    def animate_panel(self, target_y):
        """Smoothly animate the panel's Y position to the target Y position"""
        if self.is_open:
            self.current_y = max(target_y, self.current_y - self.speed)
        else:
            self.current_y = min(target_y, self.current_y + self.speed)

    def render(self):
        """Render the panel"""
        # Calculate target positions
        if self.is_open:
            target_y = self.screen.get_height() - self.height
        else:
            target_y = self.screen.get_height() - self.handle_height

        # Animate the panel
        self.animate_panel(target_y)
        
        # Render the panel if visible or animating
        if self.is_open or self.current_y < self.screen.get_height() - self.handle_height:
            # Draw the base panel
            self.screen.blit(self.base_surface, (0, self.current_y))
            
            # Draw the hint text when panel is visible or animating
            if self.is_open or self.current_y < self.screen.get_height() - self.handle_height:
                self.screen.blit(self.hint_surface, (self.hint_x, self.current_y + self.hint_y))
            
            # Draw the three areas
            panel_y = self.current_y
            
            # Draw the left area background
            self.screen.blit(self.left_area, (self.left_area_pos[0], panel_y + self.left_area_pos[1]))
            
            # Draw middle area background
            middle_x = self.middle_area_pos[0]
            middle_y = panel_y + self.middle_area_pos[1]
            self.screen.blit(self.middle_area, (middle_x, middle_y))
            
            # Get mouse position
            mouse_pos = pygame.mouse.get_pos()
            self.current_tooltip = None  # Reset current tooltip
            
            # Draw middle buttons and their descriptions
            for box in self.description_boxes:
                button = box['button']
                # Store original position
                original_x = button.rect.x
                original_y = button.rect.y
                
                # Calculate button position relative to panel
                button.rect.x = middle_x + original_x
                button.rect.y = middle_y + original_y
                
                # Draw button
                button.draw(self.screen)
                
                # Always draw description box
                desc_rect = box['rect'].copy()
                desc_rect.x = middle_x + box['rect'].x
                desc_rect.y = middle_y + box['rect'].y
                self.screen.blit(box['surface'], desc_rect)
                
                # Store tooltip if button is hovered
                if button.rect.collidepoint(mouse_pos):
                    self.current_tooltip = box['description']
                
                # Restore original position
                button.rect.x = original_x
                button.rect.y = original_y
        
        # Always render the handle, regardless of panel state
        if self.is_open or self.current_y < self.screen.get_height() - self.handle_height:
            # When panel is visible or animating, handle follows panel
            handle_y = self.current_y - self.handle_height
        else:
            # When panel is fully hidden, handle touches bottom of screen
            handle_y = self.screen.get_height() - self.handle_height
            
        # Render the handle
        handle_image = self.handle_close_surface if self.is_open else self.handle_open_surface
        self.screen.blit(handle_image, (0, handle_y))

    def handle_events(self, event: pygame.event.Event) -> Optional[str]:
        """
        Handle pygame events for the panel.
        
        Args:
            event: The pygame event to handle
            
        Returns:
            Optional[str]: Action string if an event was handled, None otherwise
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.toggle()
                return "panel_toggled"
                
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Use is_handle_clicked method for handle click detection
            if self.is_handle_clicked(mouse_pos):
                self.toggle()
                return "panel_toggled"
                
            # Check button clicks
            for i, button in enumerate(self.middle_buttons):
                # Calculate button position relative to panel
                middle_x = self.middle_area_pos[0]
                middle_y = self.current_y + self.middle_area_pos[1]
                adjusted_x = middle_x + button.rect.x
                adjusted_y = middle_y + button.rect.y
                
                # Create a temporary rect for click detection
                temp_rect = pygame.Rect(adjusted_x, adjusted_y, button.rect.width, button.rect.height)
                if temp_rect.collidepoint(mouse_pos):
                    # Get the corresponding box for this button
                    box = next((b for b in self.description_boxes if b['button'] == button), None)
                    if box:
                        self.handle_button_click(box)
                    return f"button_{i}_clicked"
                    
        return None

    def create_cached_surfaces(self):
        """Create and cache the static parts of the panel"""
        # Create the base panel surface (background + static button parts)
        self.base_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw the panel background
        # Draw left cap
        self.base_surface.blit(self.left_cap, (0, 0))
        
        # Draw middle section
        for x in range(self.cap_width, self.width - self.cap_width):
            self.base_surface.blit(self.middle, (x, 0))
            
        # Draw right cap
        self.base_surface.blit(self.right_cap, (self.width - self.cap_width, 0))

        # Create handle surfaces
        self.handle_open_surface = pygame.Surface((self.width, self.handle_height), pygame.SRCALPHA)
        self.handle_close_surface = pygame.Surface((self.width, self.handle_height), pygame.SRCALPHA)
        
        # Draw handle background
        # Draw left cap
        self.handle_open_surface.blit(self.handle_left_cap, (0, 0))
        self.handle_close_surface.blit(self.handle_left_cap, (0, 0))
        
        # Draw middle section
        for x in range(self.cap_width, self.width - self.cap_width):
            self.handle_open_surface.blit(self.handle_middle, (x, 0))
            self.handle_close_surface.blit(self.handle_middle, (x, 0))
            
        # Draw right cap
        self.handle_open_surface.blit(self.handle_right_cap, (self.width - self.cap_width, 0))
        self.handle_close_surface.blit(self.handle_right_cap, (self.width - self.cap_width, 0))
        
        # Draw arrow
        arrow_x = (self.width - self.arrow_width) // 2
        self.handle_open_surface.blit(self.handle_arrow_open, (arrow_x, 0))
        self.handle_close_surface.blit(self.handle_arrow_close, (arrow_x, 0))

    def handle_button_click(self, box):
        """Handle a button click in the panel"""
        if not box or 'action' not in box:
            return
            
        action = box['action']
        
        if action == 'attack':
            if not self.selected_object:
                return
                
            self.is_targeting = True
            self.current_action = 'attack'
            self.attacker = self.selected_object  # Store the attacker object
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
                
            # Set health to 0 to trigger destruction
            self.selected_object['health'] = 0
            # Clear selection since object will be destroyed
            self.selected_object = None
            self.selected_object_image = None
            self.set_selected_object(None)
        elif action == 'halt':
            if not self.selected_object:
                return
            # Ensure the 'is_attacking' flag is set to False on the selected object.
            self.selected_object['is_attacking'] = False

    def cancel_targeting(self):
        """Cancel targeting mode"""
        self.is_targeting = False
        self.current_action = None
        self.attacker = None
        self.cursor_manager.set_cursor('normal')

    def handle_target_selection(self, target_object):
        """Handle target selection during targeting mode"""
        if not self.is_targeting or not target_object or not self.attacker:
            return
            
        if self.current_action == 'attack':
            # Calculate distance between attacker and target
            dx = target_object['x'] - self.attacker['x']
            dy = target_object['y'] - self.attacker['y']
            distance = (dx * dx + dy * dy) ** 0.5  # Euclidean distance
            
            # Get attacker's range from metadata
            metadata = self.object_collection.get_object_metadata(self.attacker['type'], self.attacker['id'])
            properties = metadata.get('properties', {}) if metadata else {}
            attack_range = properties.get('attack_range', 0)
            
            if distance <= attack_range:
                # Target is in range, start attack
                result = {
                    'action': 'attack',
                    'attacker': self.attacker,
                    'target': target_object,
                    'in_range': True
                }
                # Only cancel targeting if attack was successful
                self.cancel_targeting()
                return result
            else:
                # Target is out of range
                if metadata and metadata.get('is_unit', False):
                    # TODO: Handle unit movement towards target
                    return {
                        'action': 'attack',
                        'attacker': self.attacker,
                        'target': target_object,
                        'in_range': False,
                        'is_unit': True
                    }
                else:
                    # Building can't move, ignore attack
                    return {
                        'action': 'attack',
                        'attacker': self.attacker,
                        'target': target_object,
                        'in_range': False,
                        'is_unit': False
                    }
                
        elif self.current_action == 'builder_unit':
            # Handle build action
            result = {
                'action': 'build',
                'position': (target_object['x'], target_object['y'])
            }
            # Cancel targeting after successful build
            self.cancel_targeting()
            return result

    def set_selected_object(self, obj):
        """Set the currently selected object and update panel accordingly"""
        self.selected_object = obj  # Store the selected object
        if obj:
            self.object_name_text = obj.get('name', 'Unknown')
            self.object_name_surface = self.object_name_font.render(self.object_name_text, True, self.object_name_color)
            self.update_buttons_for_object(obj)
            
            # Try to load the object's image
            try:
                image_path = os.path.join("Images", f"{obj['type']}{obj['id']:05d}.png")
                if os.path.exists(image_path):
                    self.selected_object_image = pygame.image.load(image_path).convert_alpha()
                else:
                    self.selected_object_image = self.default_selection
            except:
                self.selected_object_image = self.default_selection
        else:
            self.object_name_text = "No selection"
            self.object_name_surface = self.object_name_font.render(self.object_name_text, True, self.object_name_color)
            self.middle_buttons = []
            self.description_boxes = []
            self.selected_object_image = self.default_selection

    def render_text(self):
        """Render text elements of the panel"""
        if self.is_open or self.current_y < self.screen.get_height() - self.handle_height:
            # Render object name at the bottom of the left area
            name_x = self.left_area_pos[0] + (self.left_area_size - self.object_name_surface.get_width()) // 2
            name_y = self.current_y + self.left_area_pos[1] + self.area_height - 20  # Position at bottom with some padding
            self.screen.blit(self.object_name_surface, (name_x, name_y))

    def render_life_bar(self, obj, left_area_rect):
        """Render the life bar and charge bar for the selected object"""
        if not obj or 'health' not in obj or 'max_health' not in obj:
            return False
            
        # Calculate life bar position
        bar_width = self.left_area_size - 20  # Leave some margin
        bar_height = 10
        bar_x = left_area_rect.x + 10
        bar_y = left_area_rect.y + self.left_area_size - bar_height + 12  # Move down 20px
        
        # Get health values
        current_health = obj['health']  # Current health value
        max_health = obj['max_health']  # Maximum health value
        
        # Get charge value (default to 0 if not present)
        charge_percent = obj.get('charge_percent', 0)
        
        # Check if object has infinite health
        if max_health == -1:  # -1 represents infinite health
            health_percent = 1.0  # Always show full health bar
            # Create infinity symbol by rotating "8" 90 degrees
            text_surface = self.life_bar_font.render("8", True, (255, 255, 255))
            text_surface = pygame.transform.rotate(text_surface, 90)
            health_text = None  # We'll use the rotated surface directly
        else:
            # Calculate actual percentage of current health relative to max health
            health_percent = min(1.0, max(0.0, current_health / max_health))  # Clamp between 0 and 1
            # Show the actual percentage, not the raw health value
            health_text = f"{int(health_percent * 100)}%"
            text_surface = self.life_bar_font.render(health_text, True, (255, 255, 255))
        
        # Draw life bar background structure
        left_width = self.life_bar_left.get_width()
        background_x = bar_x - 10  # Offset background 10px to the left
        self.screen.blit(self.life_bar_left, (background_x, bar_y))
        right_pos = (background_x + left_width, bar_y)
        self.screen.blit(self.life_bar_right, right_pos)  # Position right after left image's width
        
        # Draw life bar fill
        fill_width = int((bar_width - 19) * health_percent)  # Adjusted margin to allow complete fill
        if fill_width > 0:
            # Draw left cap of energy fill
            energy_x = bar_x + 20  # Start energy fill 20px to the right
            self.screen.blit(self.life_bar_energy_tip, (energy_x, bar_y))
            
            # Draw middle section
            for x in range(energy_x + 2, energy_x + fill_width - 2):
                self.screen.blit(self.life_bar_energy_stretch, (x, bar_y))
                
            # Draw right cap
            self.screen.blit(self.life_bar_energy_tip, (energy_x + fill_width - 2, bar_y))
        

        # Calculate charge bar width (max 86 pixels for stretch)
        charge_stretch_width = int(96 * charge_percent)
        charge_x = right_pos[0]  # Start at the same position as life_bar_right
        
        # Draw charge stretch
        for x in range(charge_x, charge_x + charge_stretch_width):
            self.screen.blit(self.life_bar_charge_stretch, (x, bar_y))
        
        # Draw charge tip if there's any charge
        if charge_stretch_width > 0:
            self.screen.blit(self.life_bar_charge_tip, (charge_x + charge_stretch_width, bar_y))
        
        # Draw health percentage text centered in the left part
        text_x = background_x + (left_width - text_surface.get_width()) // 2  # Center in left part
        text_y = bar_y + (bar_height - text_surface.get_height()) // 2 + 10  # Center vertically and move down 10px
        self.screen.blit(text_surface, (text_x, text_y))
        
        # Return True if health is 0 and object doesn't have infinite health
        return current_health <= 0 and max_health != -1

    def get_left_area_rect(self):
        """Get the rectangle for the left area of the panel"""
        return pygame.Rect(
            self.left_area_pos[0],
            self.current_y + self.left_area_pos[1],
            self.left_area_size,
            self.area_height
        ) 