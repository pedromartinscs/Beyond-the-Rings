import pygame
import os
from Core.Menu.button import Button

class Panel:
    def __init__(self, screen):
        self.screen = screen
        self.width = screen.get_width()
        self.height = 200  # Height of the panel
        self.color = (50, 50, 50)  # Color of the panel
        self.visible = False  # Start with the panel hidden
        self.current_y = self.screen.get_height()  # Panel starts off-screen (at the bottom)
        self.handle_height = 20  # Height of the visible handle when hidden
        self.speed = 10  # Animation speed
        self.cap_width = 60  # Width of the left and right caps
        self.arrow_width = 20  # Width of the arrow section

        # Define areas dimensions and margins
        self.margin = 20  # Margin between areas and edges
        self.left_area_size = 150  # Square area for unit/building display
        self.right_area_width = 100  # Width of strategy buttons area
        self.area_height = 150  # Height of all areas

        # Calculate middle area width
        self.middle_area_width = self.width - (self.left_area_size + self.right_area_width + (self.margin * 4))

        # Create surfaces for each area
        self.left_area = pygame.image.load(os.path.join('Images', 'game_menu_vertical_left_area.png'))
        self.left_area = pygame.transform.scale(self.left_area, (self.left_area_size, self.area_height))
        self.middle_area = pygame.Surface((self.middle_area_width, self.area_height), pygame.SRCALPHA)  # Make transparent
        self.right_area = pygame.Surface((self.right_area_width, self.area_height))
        self.right_area.fill((0, 0, 0))  # Black for now

        # Calculate area positions
        self.left_area_pos = (self.margin, self.margin + 5)
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
        self.middle = pygame.transform.scale(self.middle, (1, self.height))  # 1px wide, 200px tall

        # Load handle images
        self.handle_left_cap = pygame.image.load(os.path.join('Images', 'left_horizontal_handle_cap.png'))
        self.handle_left_cap = pygame.transform.scale(self.handle_left_cap, (self.cap_width, self.handle_height))
        self.handle_right_cap = pygame.image.load(os.path.join('Images', 'right_horizontal_handle_cap.png'))
        self.handle_right_cap = pygame.transform.scale(self.handle_right_cap, (self.cap_width, self.handle_height))
        self.handle_middle = pygame.image.load(os.path.join('Images', 'middle_horizontal_handle.png'))
        self.handle_middle = pygame.transform.scale(self.handle_middle, (1, self.handle_height))  # 1px wide, 20px tall
        self.handle_arrow_open = pygame.image.load(os.path.join('Images', 'middle_horizontal_handle_open.png'))
        self.handle_arrow_open = pygame.transform.scale(self.handle_arrow_open, (self.arrow_width, self.handle_height))
        self.handle_arrow_close = pygame.image.load(os.path.join('Images', 'middle_horizontal_handle_close.png'))
        self.handle_arrow_close = pygame.transform.scale(self.handle_arrow_close, (self.arrow_width, self.handle_height))

        # Tooltip properties
        self.tooltip_font = pygame.font.Font(None, 14)  # Font for tooltip text
        self.tooltip_padding = 8  # Padding around tooltip text
        self.tooltip_margin = 5  # Margin between box and tooltip
        self.tooltip_bg_color = (40, 40, 40)  # Dark gray background
        self.tooltip_text_color = (255, 255, 255)  # White text
        self.tooltip_border_color = (100, 100, 100)  # Light gray border
        self.tooltip_border_width = 1
        self.current_tooltip = None  # Currently displayed tooltip

        # Create cached surfaces
        self.create_cached_surfaces()

    def create_middle_area_buttons(self):
        # Button dimensions
        button_width = 32
        button_height = 32
        
        # Grid dimensions
        max_rows = 4
        max_cols = 6
        total_buttons = 12  # Only create 12 buttons
        
        # Calculate spacing between buttons
        spacing_x = 8  # Fixed spacing between buttons
        spacing_y = 8  # Fixed spacing between rows
        
        # Calculate actual number of columns needed (up to max_cols)
        actual_cols = min(max_cols, total_buttons)
        
        # Calculate column positions and box width
        column_positions = []
        total_width = self.middle_area_width - (spacing_x * (actual_cols - 1))
        box_width = (total_width - (button_width * actual_cols)) // actual_cols
        
        # Calculate starting x position to center the buttons
        start_x = (self.middle_area_width - (actual_cols * (button_width + box_width + spacing_x) - spacing_x)) // 2
        
        for col in range(actual_cols):
            x = start_x + col * (button_width + spacing_x + box_width)
            column_positions.append(x)
        
        # Create buttons and their description boxes
        self.middle_buttons = []
        self.description_boxes = []
        
        # Create fonts for title and description
        self.title_font = pygame.font.Font(None, 16)  # Bold font for title
        self.description_font = pygame.font.Font(None, 14)  # Regular font for description
        
        # Box color and margin
        self.box_color = (48, 82, 101)
        self.box_margin = 1
        
        for i in range(total_buttons):
            # Calculate row and column
            col = i % actual_cols
            row = i // actual_cols
            
            # Skip if we exceed max rows
            if row >= max_rows:
                break
                
            # Calculate button position
            x = column_positions[col]
            y = row * (button_height + spacing_y)
            
            # Create button
            button = Button(
                x, y, 0, 0, button_width, button_height,
                "", None,  # No text or action for now
                "Images/tiny_button_basic.png",
                "Images/tiny_button_basic.png"  # Using same image for both states for now
            )
            
            # Create description box
            box = {
                'rect': pygame.Rect(x + button_width + self.box_margin, y, box_width, button_height),
                'title': "Mock Title",
                'description': "Mock Description that might be longer than one line and needs to wrap, very important message that I'm making specially long to test the wrapping functionality",
                'button': button,
                'lines': [],  # Will store wrapped description lines
                'is_wrapped': False  # Flag to track if description was wrapped
            }
            
            self.middle_buttons.append(button)
            self.description_boxes.append(box)

    def wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width and add ellipsis if needed"""
        words = text.split(' ')
        lines = []
        current_line = []
        is_wrapped = False
        max_lines = 2  # Maximum number of lines we want to show
        
        for word in words:
            # Create a test line with the new word
            test_line = ' '.join(current_line + [word])
            test_width = font.size(test_line)[0]
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    if len(lines) >= max_lines:
                        is_wrapped = True
                        break
                current_line = [word]
        
        # Add the last line if we haven't reached max_lines
        if current_line and len(lines) < max_lines:
            lines.append(' '.join(current_line))
        
        # If we have more than max_lines, truncate and add ellipsis
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            is_wrapped = True
        
        # Add ellipsis to the last line if text was wrapped
        if is_wrapped and lines:
            last_line = lines[-1]
            while font.size(last_line + '...')[0] > max_width and last_line:
                last_line = last_line[:-1]
            lines[-1] = last_line + '...'
        
        return lines, is_wrapped

    def create_cached_surfaces(self):
        """Create and cache the panel and handle surfaces"""
        # Create the base panel surface
        self.base_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw left cap
        self.base_surface.blit(self.left_cap, (0, 0))
        
        # Draw right cap
        self.base_surface.blit(self.right_cap, (self.width - self.cap_width, 0))
        
        # Draw stretched middle
        middle_width = self.width - (self.cap_width * 2)  # 60px left + 60px right
        if middle_width > 0:
            stretched_middle = pygame.transform.scale(self.middle, (middle_width, self.height))
            self.base_surface.blit(stretched_middle, (self.cap_width, 0))

        # Create handle surfaces for open and closed states
        self.handle_open_surface = pygame.Surface((self.width, self.handle_height), pygame.SRCALPHA)
        self.handle_close_surface = pygame.Surface((self.width, self.handle_height), pygame.SRCALPHA)

        # Calculate the center position for the arrow
        center_x = (self.width - self.arrow_width) // 2

        # Draw handle for both states
        for surface, arrow_image in [(self.handle_open_surface, self.handle_arrow_open), 
                                   (self.handle_close_surface, self.handle_arrow_close)]:
            # Draw left cap
            surface.blit(self.handle_left_cap, (0, 0))
            
            # Draw left stretch
            left_stretch_width = center_x - self.cap_width
            if left_stretch_width > 0:
                left_stretch = pygame.transform.scale(self.handle_middle, (left_stretch_width, self.handle_height))
                surface.blit(left_stretch, (self.cap_width, 0))
            
            # Draw arrow
            surface.blit(arrow_image, (center_x, 0))
            
            # Draw right stretch
            right_stretch_x = center_x + self.arrow_width
            right_stretch_width = self.width - right_stretch_x - self.cap_width
            if right_stretch_width > 0:
                right_stretch = pygame.transform.scale(self.handle_middle, (right_stretch_width, self.handle_height))
                surface.blit(right_stretch, (right_stretch_x, 0))
            
            # Draw right cap
            surface.blit(self.handle_right_cap, (self.width - self.cap_width, 0))

    def show(self):
        # Show the panel (slide it in)
        self.visible = True

    def hide(self):
        # Hide the panel (slide it out)
        self.visible = False

    def is_handle_clicked(self, pos):
        # Calculate handle position
        if self.visible:
            # When panel is visible, handle is on top of panel
            handle_y = self.current_y - self.handle_height
        else:
            # When panel is hidden, handle touches bottom of screen
            handle_y = self.screen.get_height() - self.handle_height
            
        # Check if the click is within the handle area
        handle_rect = pygame.Rect(0, handle_y, self.width, self.handle_height)
        return handle_rect.collidepoint(pos)

    def animate_panel(self, target_y):
        # Smoothly animate the panel's Y position to the target Y position
        if self.visible:
            self.current_y = max(target_y, self.current_y - self.speed)
        else:
            self.current_y = min(target_y, self.current_y + self.speed)

    def render_tooltip(self, box, mouse_pos):
        """Render the tooltip for a box with truncated text"""
        if not box['is_wrapped']:
            return None

        # Calculate tooltip position relative to the box
        tooltip_x = box['rect'].x + self.middle_area_pos[0]
        
        # Position tooltip above the box, but not too far up
        # Use the panel's current_y position to determine available space
        panel_top = self.current_y
        box_top = box['rect'].y + self.middle_area_pos[1]
        available_space_above = box_top - panel_top
        
        # Wrap the full description for the tooltip (without ellipsis)
        tooltip_lines = []
        words = box['description'].split(' ')
        current_line = []
        max_width = 300  # Max width for tooltip
        
        for word in words:
            # Create a test line with the new word
            test_line = ' '.join(current_line + [word])
            test_width = self.tooltip_font.size(test_line)[0]
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    tooltip_lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            tooltip_lines.append(' '.join(current_line))
        
        # Calculate tooltip dimensions
        max_width = max(self.tooltip_font.size(line)[0] for line in tooltip_lines)
        total_height = len(tooltip_lines) * self.tooltip_font.get_height()
        
        # Create tooltip surface
        tooltip_width = max_width + (self.tooltip_padding * 2)
        tooltip_height = total_height + (self.tooltip_padding * 2)
        tooltip_surface = pygame.Surface((tooltip_width, tooltip_height))
        tooltip_surface.fill(self.tooltip_bg_color)
        
        # Draw border
        pygame.draw.rect(tooltip_surface, self.tooltip_border_color, 
                        (0, 0, tooltip_width, tooltip_height), self.tooltip_border_width)
        
        # Render text
        y_offset = self.tooltip_padding
        for line in tooltip_lines:
            text_surface = self.tooltip_font.render(line, True, self.tooltip_text_color)
            tooltip_surface.blit(text_surface, (self.tooltip_padding, y_offset))
            y_offset += self.tooltip_font.get_height()
        
        # Adjust position to ensure tooltip stays on screen and is close to the box
        if tooltip_x + tooltip_width > self.screen.get_width():
            tooltip_x = self.screen.get_width() - tooltip_width
        
        # Position tooltip above the box if there's enough space, otherwise below
        if available_space_above >= tooltip_height + self.tooltip_margin:
            tooltip_y = box_top - tooltip_height - self.tooltip_margin
        else:
            tooltip_y = box_top + box['rect'].height + self.tooltip_margin
        
        return (tooltip_surface, (tooltip_x, tooltip_y))

    def render(self):
        # Calculate target positions
        if self.visible:
            target_y = self.screen.get_height() - self.height
        else:
            target_y = self.screen.get_height() - self.handle_height

        # Animate the panel
        self.animate_panel(target_y)
        
        # Render the panel if visible or animating
        if self.visible or self.current_y < self.screen.get_height() - self.handle_height:
            # Draw the base panel
            self.screen.blit(self.base_surface, (0, self.current_y))
            
            # Draw the three areas
            panel_y = self.current_y
            self.screen.blit(self.left_area, (self.left_area_pos[0], panel_y + self.left_area_pos[1]))
            
            # Draw middle area and its buttons
            middle_x = self.middle_area_pos[0]
            middle_y = panel_y + self.middle_area_pos[1]
            self.screen.blit(self.middle_area, (middle_x, middle_y))
            
            # Get mouse position
            mouse_pos = pygame.mouse.get_pos()
            self.current_tooltip = None  # Reset current tooltip
            
            # Render buttons and boxes
            for box in self.description_boxes:
                button = box['button']
                button_rect = button.rect.copy()
                button_rect.x += middle_x
                button_rect.y += middle_y
                
                # Draw button
                self.screen.blit(button.image, button_rect)
                
                # Update box position
                box['rect'].x = button.rect.x + button.rect.width + self.box_margin
                box['rect'].y = button.rect.y
                
                # Wrap description text if needed
                if not box['lines']:
                    box['lines'], box['is_wrapped'] = self.wrap_text(box['description'], self.description_font, box['rect'].width - 8)
                
                # Calculate box height based on content
                title_height = self.title_font.get_height()
                desc_height = len(box['lines']) * self.description_font.get_height()
                box_height = title_height + desc_height + 8  # 8px padding
                box['rect'].height = max(box_height, button.rect.height)
                
                # Draw box background
                box_surface = pygame.Surface((box['rect'].width, box['rect'].height), pygame.SRCALPHA)
                box_surface.fill(self.box_color)
                
                # Render title
                title_surface = self.title_font.render(box['title'], True, (255, 255, 255))
                title_x = (box['rect'].width - title_surface.get_width()) // 2
                title_y = 4  # Small padding from top
                box_surface.blit(title_surface, (title_x, title_y))
                
                # Render description lines
                desc_y = title_y + title_height + 2
                for line in box['lines']:
                    desc_surface = self.description_font.render(line, True, (200, 200, 200))
                    desc_x = (box['rect'].width - desc_surface.get_width()) // 2
                    box_surface.blit(desc_surface, (desc_x, desc_y))
                    desc_y += self.description_font.get_height()
                
                # Draw box
                self.screen.blit(box_surface, (middle_x + box['rect'].x, middle_y + box['rect'].y))
                
                # Check if mouse is over box and text is wrapped
                box_rect = pygame.Rect(middle_x + box['rect'].x, middle_y + box['rect'].y, 
                                     box['rect'].width, box['rect'].height)
                if box_rect.collidepoint(mouse_pos) and box['is_wrapped']:
                    self.current_tooltip = self.render_tooltip(box, mouse_pos)
            
            self.screen.blit(self.right_area, (self.right_area_pos[0], panel_y + self.right_area_pos[1]))
            
            # Draw tooltip if needed
            if self.current_tooltip:
                tooltip_surface, tooltip_pos = self.current_tooltip
                self.screen.blit(tooltip_surface, tooltip_pos)
        
        # Calculate handle position
        if self.visible or self.current_y < self.screen.get_height() - self.handle_height:
            # When panel is visible or animating, handle follows panel
            handle_y = self.current_y - self.handle_height
        else:
            # When panel is fully hidden, handle touches bottom of screen
            handle_y = self.screen.get_height() - self.handle_height
            
        # Render the handle
        handle_image = self.handle_close_surface if self.visible else self.handle_open_surface
        self.screen.blit(handle_image, (0, handle_y))
