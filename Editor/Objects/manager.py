import pygame
import sys
import os
import tkinter as tk
from tkinter import filedialog
import json
from typing import Dict, List, Optional, Tuple
from Core.UI.button import Button

class ObjectManager:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Colors
        self.background_color = (50, 50, 50)
        self.text_color = (255, 255, 255)
        self.button_color = (100, 100, 100)
        self.button_hover_color = (150, 150, 150)
        self.json_background = (30, 30, 30)
        self.json_text_color = (200, 255, 200)
        
        # Fonts
        self.title_font = pygame.font.Font(None, 36)
        self.text_font = pygame.font.Font(None, 24)
        self.json_font = pygame.font.Font(None, 20)
        
        # Object types list
        self.object_types = []
        self.selected_type = None
        self.selected_object = None
        self.json_data = None
        self.json_text = ""
        self.json_cursor_pos = 0
        self.json_scroll_y = 0
        self.json_scroll_x = 0
        self.json_active = False
        self.scrollbar_width = 20
        self.scrollbar_height = 20
        self.json_line_height = 20
        self.json_char_width = 10  # Approximate width of a character
        
        # UI elements
        self.type_list_rect = pygame.Rect(50, 100, 200, 400)
        self.palette_rect = pygame.Rect(300, 100, 400, 400)  # Made narrower
        self.json_editor_rect = pygame.Rect(750, 100, 250, 400)  # Added JSON editor
        self.json_content_rect = pygame.Rect(
            self.json_editor_rect.x + 10,
            self.json_editor_rect.y + 10,
            self.json_editor_rect.width - 30,  # Leave space for scrollbar
            self.json_editor_rect.height - 30   # Leave space for scrollbar
        )
        self.json_vscroll_rect = pygame.Rect(
            self.json_editor_rect.right - self.scrollbar_width,
            self.json_editor_rect.y,
            self.scrollbar_width,
            self.json_editor_rect.height - self.scrollbar_height  # Adjust height to not overlap with horizontal scrollbar
        )
        self.json_hscroll_rect = pygame.Rect(
            self.json_editor_rect.x,
            self.json_editor_rect.bottom - self.scrollbar_height,
            self.json_editor_rect.width - self.scrollbar_width,
            self.scrollbar_height
        )
        self.json_save_button_rect = pygame.Rect(
            self.json_editor_rect.x,
            self.json_editor_rect.bottom + 10,
            100,
            30
        )
        self.new_type_input_rect = pygame.Rect(50, 520, 200, 30)
        self.new_type_button_rect = pygame.Rect(260, 520, 100, 30)
        self.new_object_button_rect = pygame.Rect(370, 520, 150, 30)
        
        # Input text
        self.new_type_text = ""
        self.input_active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_blink_speed = 500  # milliseconds
        
        # Load object types
        self.load_object_types()
        
        # Create buttons
        self.create_buttons()

    def load_object_types(self):
        """Load all object types from the Objects directory"""
        objects_path = os.path.join("Maps", "Common", "Objects")
        if os.path.exists(objects_path):
            self.object_types = [d for d in os.listdir(objects_path) 
                               if os.path.isdir(os.path.join(objects_path, d))]
            self.object_types.sort()  # Sort alphabetically
            
            # Create default.json for each type if it doesn't exist
            for type_name in self.object_types:
                self.ensure_default_json(type_name)

    def ensure_default_json(self, type_name):
        """Ensure default.json exists for the given type"""
        type_path = os.path.join("Maps", "Common", "Objects", type_name)
        default_json_path = os.path.join(type_path, "default.json")
        
        if not os.path.exists(default_json_path):
            default_data = {
                "name": type_name,
                "description": f"Default {type_name} object",
                "properties": {
                    "health": 100,
                    "damage": 50,
                    "z_index": 0
                },
                "abilities": [],
                "visuals": {
                    "animation_speed": 0,
                    "frames": 1
                }
            }
            
            with open(default_json_path, 'w') as f:
                json.dump(default_data, f, indent=4)

    def load_object_json(self, type_name, object_name):
        """Load JSON data for an object, falling back to default.json if needed"""
        type_path = os.path.join("Maps", "Common", "Objects", type_name)
        object_json_path = os.path.join(type_path, f"{object_name}.json")
        default_json_path = os.path.join(type_path, "default.json")
        
        try:
            # Try to load object-specific JSON
            if os.path.exists(object_json_path):
                with open(object_json_path, 'r') as f:
                    self.json_data = json.load(f)
            # Fall back to default.json
            else:
                with open(default_json_path, 'r') as f:
                    self.json_data = json.load(f)
            
            # Convert to formatted string for display
            self.json_text = json.dumps(self.json_data, indent=4)
            
        except Exception as e:
            print(f"Error loading JSON: {e}")
            self.json_data = None
            self.json_text = ""

    def save_object_json(self):
        """Save the current JSON data for the selected object"""
        if not self.selected_type or not self.selected_object or not self.json_text:
            return
            
        try:
            # Parse the JSON text to validate it
            json_data = json.loads(self.json_text)
            
            # Save to file
            type_path = os.path.join("Maps", "Common", "Objects", self.selected_type)
            object_json_path = os.path.join(type_path, f"{self.selected_object}.json")
            
            with open(object_json_path, 'w') as f:
                json.dump(json_data, f, indent=4)
                
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}")
        except Exception as e:
            print(f"Error saving JSON: {e}")

    def create_buttons(self):
        """Create the UI buttons"""
        # New type button
        self.new_type_button = Button(
            self.new_type_button_rect.x, self.new_type_button_rect.y,
            0, 0, self.new_type_button_rect.width, self.new_type_button_rect.height,
            "New Type", self.add_new_type,
            "Images/menu_button.png", "Images/menu_button_glow.png"
        )
        
        # New object button
        self.new_object_button = Button(
            self.new_object_button_rect.x, self.new_object_button_rect.y,
            0, 0, self.new_object_button_rect.width, self.new_object_button_rect.height,
            "New Object", self.add_new_object,
            "Images/menu_button.png", "Images/menu_button_glow.png"
        )
        
        # JSON save button
        self.json_save_button = Button(
            self.json_save_button_rect.x, self.json_save_button_rect.y,
            0, 0, self.json_save_button_rect.width, self.json_save_button_rect.height,
            "Save JSON", self.save_object_json,
            "Images/menu_button.png", "Images/menu_button_glow.png"
        )

    def add_new_type(self):
        """Add a new object type"""
        if self.new_type_text:
            # Convert to lowercase and remove spaces
            type_name = self.new_type_text.lower().replace(" ", "_")
            
            # Create the directory if it doesn't exist
            type_path = os.path.join("Maps", "Common", "Objects", type_name)
            if not os.path.exists(type_path):
                os.makedirs(type_path)
                self.object_types.append(type_name)
                self.object_types.sort()
            
            # Clear the input
            self.new_type_text = ""
            self.input_active = False

    def add_new_object(self):
        """Add a new object to the selected type"""
        if not self.selected_type:
            return
            
        # Open file dialog
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            title="Select Object Image",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        root.destroy()
        
        if not file_path:
            return
            
        # Check image dimensions
        try:
            image = pygame.image.load(file_path)
            width, height = image.get_size()
            
            if (width, height) not in [(32, 32), (64, 64), (128, 128)]:
                print(f"Error: Image dimensions must be 32x32, 64x64, or 128x128 pixels")
                return
                
            # Find the next available ID
            type_path = os.path.join("Maps", "Common", "Objects", self.selected_type)
            existing_ids = set()
            
            for filename in os.listdir(type_path):
                if filename.endswith(".png"):
                    try:
                        # Extract ID from filename (type + 5 digits)
                        id_str = filename[len(self.selected_type):-4]
                        if id_str.isdigit():
                            existing_ids.add(int(id_str))
                    except:
                        continue
            
            # Find the first available ID starting from 0
            new_id = 0
            while new_id in existing_ids:
                new_id += 1
            
            # Create the new filename
            new_filename = f"{self.selected_type}{new_id:05d}.png"
            new_path = os.path.join(type_path, new_filename)
            
            # Copy the image
            pygame.image.save(image, new_path)
            
        except Exception as e:
            print(f"Error adding new object: {e}")

    def handle_events(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = event.pos
                
                # Check type list click
                if self.type_list_rect.collidepoint(mouse_pos):
                    # Calculate which type was clicked
                    relative_y = mouse_pos[1] - self.type_list_rect.y
                    type_index = relative_y // 30  # 30 pixels per type
                    
                    if 0 <= type_index < len(self.object_types):
                        self.selected_type = self.object_types[type_index]
                        self.selected_object = None
                        self.json_text = ""
                
                # Check palette click
                elif self.palette_rect.collidepoint(mouse_pos) and self.selected_type:
                    # Calculate which object was clicked
                    rel_x = mouse_pos[0] - self.palette_rect.x - 10
                    rel_y = mouse_pos[1] - self.palette_rect.y - 10
                    
                    # Get objects in the palette
                    type_path = os.path.join("Maps", "Common", "Objects", self.selected_type)
                    if os.path.exists(type_path):
                        x, y = 0, 0
                        for filename in sorted(os.listdir(type_path)):
                            if filename.endswith(".png"):
                                try:
                                    image = pygame.image.load(os.path.join(type_path, filename))
                                    img_rect = pygame.Rect(x, y, image.get_width(), image.get_height())
                                    
                                    if img_rect.collidepoint(rel_x, rel_y):
                                        self.selected_object = filename[:-4]  # Remove .png
                                        self.load_object_json(self.selected_type, self.selected_object)
                                        break
                                        
                                    x += image.get_width() + 10
                                    if x + image.get_width() > self.palette_rect.width - 20:
                                        x = 0
                                        y += image.get_height() + 10
                                except:
                                    continue
                
                # Check JSON editor click
                elif self.json_editor_rect.collidepoint(mouse_pos):
                    self.json_active = True
                    
                    # Check if clicking on scrollbars
                    if self.json_vscroll_rect.collidepoint(mouse_pos):
                        # Calculate scroll position based on click
                        rel_y = mouse_pos[1] - self.json_vscroll_rect.y
                        max_scroll = max(0, len(self.json_text.split('\n')) * self.json_line_height - self.json_content_rect.height)
                        self.json_scroll_y = int((rel_y / self.json_vscroll_rect.height) * max_scroll)
                    elif self.json_hscroll_rect.collidepoint(mouse_pos):
                        # Calculate horizontal scroll position based on click
                        rel_x = mouse_pos[0] - self.json_hscroll_rect.x
                        max_scroll = max(0, self.get_max_line_width() * self.json_char_width - self.json_content_rect.width)
                        self.json_scroll_x = int((rel_x / self.json_hscroll_rect.width) * max_scroll)
                    else:
                        # Calculate cursor position based on click
                        rel_y = mouse_pos[1] - self.json_content_rect.y
                        rel_x = mouse_pos[0] - self.json_content_rect.x
                        line_height = self.json_font.get_height()
                        clicked_line = (rel_y + self.json_scroll_y) // line_height
                        
                        # Find the closest valid cursor position
                        total_chars = 0
                        lines = self.json_text.split('\n')
                        for i, line in enumerate(lines):
                            if i == clicked_line:
                                # Find closest character position
                                for j, char in enumerate(line):
                                    char_width = self.json_font.size(line[:j+1])[0]
                                    if char_width > rel_x + self.json_scroll_x:
                                        self.json_cursor_pos = total_chars + j
                                        break
                                else:
                                    self.json_cursor_pos = total_chars + len(line)
                                break
                            total_chars += len(line) + 1  # +1 for newline
                else:
                    self.json_active = False
                
                # Check JSON save button
                if self.json_save_button_rect.collidepoint(mouse_pos):
                    self.save_object_json()
                
                # Check new type input
                if self.new_type_input_rect.collidepoint(mouse_pos):
                    self.input_active = True
                else:
                    self.input_active = False
                
                # Check buttons
                if self.new_type_button.rect.collidepoint(mouse_pos):
                    self.add_new_type()
                elif self.new_object_button.rect.collidepoint(mouse_pos):
                    self.add_new_object()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Mouse wheel up
                if self.json_editor_rect.collidepoint(event.pos):
                    self.json_scroll_y = max(0, self.json_scroll_y - 20)
            elif event.button == 5:  # Mouse wheel down
                if self.json_editor_rect.collidepoint(event.pos):
                    max_scroll = max(0, len(self.json_text.split('\n')) * self.json_line_height - self.json_content_rect.height)
                    self.json_scroll_y = min(max_scroll, self.json_scroll_y + 20)
            elif event.button == 6:  # Mouse wheel left
                if self.json_editor_rect.collidepoint(event.pos):
                    self.json_scroll_x = max(0, self.json_scroll_x - 20)
            elif event.button == 7:  # Mouse wheel right
                if self.json_editor_rect.collidepoint(event.pos):
                    max_scroll = max(0, self.get_max_line_width() * self.json_char_width - self.json_content_rect.width)
                    self.json_scroll_x = min(max_scroll, self.json_scroll_x + 20)
        
        elif event.type == pygame.KEYDOWN:
            if self.input_active:
                if event.key == pygame.K_RETURN:
                    self.add_new_type()
                elif event.key == pygame.K_BACKSPACE:
                    self.new_type_text = self.new_type_text[:-1]
                else:
                    self.new_type_text += event.unicode
            elif self.json_active and self.json_text is not None:
                if event.key == pygame.K_RETURN:
                    # Insert newline
                    self.json_text = (self.json_text[:self.json_cursor_pos] + '\n' + 
                                    self.json_text[self.json_cursor_pos:])
                    self.json_cursor_pos += 1
                elif event.key == pygame.K_BACKSPACE:
                    if self.json_cursor_pos > 0:
                        self.json_text = (self.json_text[:self.json_cursor_pos-1] + 
                                        self.json_text[self.json_cursor_pos:])
                        self.json_cursor_pos -= 1
                elif event.key == pygame.K_LEFT:
                    self.json_cursor_pos = max(0, self.json_cursor_pos - 1)
                elif event.key == pygame.K_RIGHT:
                    self.json_cursor_pos = min(len(self.json_text), self.json_cursor_pos + 1)
                elif event.key == pygame.K_s and event.mod & pygame.KMOD_CTRL:
                    self.save_object_json()
                else:
                    # Insert character at cursor position
                    if event.unicode.isprintable():
                        self.json_text = (self.json_text[:self.json_cursor_pos] + 
                                        event.unicode + 
                                        self.json_text[self.json_cursor_pos:])
                        self.json_cursor_pos += 1

    def get_max_line_width(self):
        """Get the width of the longest line in the JSON text"""
        max_width = 0
        for line in self.json_text.split('\n'):
            width = self.json_font.size(line)[0]
            max_width = max(max_width, width)
        return max_width

    def render(self):
        # Clear screen
        self.screen.fill(self.background_color)
        
        # Draw title
        title_surface = self.title_font.render("Object Manager", True, self.text_color)
        self.screen.blit(title_surface, (50, 50))
        
        # Draw type list
        pygame.draw.rect(self.screen, (70, 70, 70), self.type_list_rect)
        for i, type_name in enumerate(self.object_types):
            color = (200, 200, 200) if type_name == self.selected_type else self.text_color
            text_surface = self.text_font.render(type_name, True, color)
            self.screen.blit(text_surface, (self.type_list_rect.x + 10, self.type_list_rect.y + 10 + (i * 30)))
        
        # Draw palette area
        pygame.draw.rect(self.screen, (70, 70, 70), self.palette_rect)
        if self.selected_type:
            # Draw objects in the palette
            type_path = os.path.join("Maps", "Common", "Objects", self.selected_type)
            if os.path.exists(type_path):
                x, y = self.palette_rect.x + 10, self.palette_rect.y + 10
                for filename in sorted(os.listdir(type_path)):
                    if filename.endswith(".png"):
                        try:
                            image = pygame.image.load(os.path.join(type_path, filename))
                            # Draw selection rectangle if this is the selected object
                            if self.selected_object and filename.startswith(self.selected_object):
                                select_rect = pygame.Rect(x - 2, y - 2, 
                                                        image.get_width() + 4, 
                                                        image.get_height() + 4)
                                pygame.draw.rect(self.screen, (255, 255, 0), select_rect, 2)
                            self.screen.blit(image, (x, y))
                            x += image.get_width() + 10
                            if x + image.get_width() > self.palette_rect.right - 10:
                                x = self.palette_rect.x + 10
                                y += image.get_height() + 10
                        except:
                            continue
        
        # Draw JSON editor
        pygame.draw.rect(self.screen, self.json_background, self.json_editor_rect)
        if self.json_text:
            # Draw JSON content with line numbers
            y = self.json_content_rect.y - self.json_scroll_y
            line_height = self.json_font.get_height()
            lines = self.json_text.split('\n')
            
            # Create a clipping rect for the JSON editor
            clip_rect = self.json_content_rect.copy()
            
            for i, line in enumerate(lines):
                # Only render visible lines
                if y + line_height > self.json_content_rect.y and y < self.json_content_rect.bottom:
                    # Draw line number
                    line_num = self.json_font.render(f"{i+1:3d} ", True, (150, 150, 150))
                    self.screen.blit(line_num, (self.json_content_rect.x, y))
                    
                    # Draw line text
                    text_surface = self.json_font.render(line, True, self.json_text_color)
                    text_pos = (self.json_content_rect.x + 50 - self.json_scroll_x, y)
                    
                    # Only draw if within the clip rect
                    if clip_rect.collidepoint(text_pos):
                        # Calculate how much of the text to show
                        visible_width = min(text_surface.get_width(), 
                                          self.json_content_rect.width - 50)  # 50 for line numbers
                        
                        # Calculate the starting x position for the text
                        start_x = max(0, self.json_scroll_x)
                        if start_x < text_surface.get_width():
                            # Create a subsurface of the text surface
                            visible_text = text_surface.subsurface((
                                start_x,  # Start from the scrolled position
                                0,       # Start from the top
                                min(visible_width, text_surface.get_width() - start_x),  # Show only what fits
                                text_surface.get_height()
                            ))
                            self.screen.blit(visible_text, text_pos)
                
                y += line_height
            
            # Draw cursor if JSON editor is active
            if self.json_active and self.cursor_visible:
                # Calculate cursor position
                cursor_pos = 0
                cursor_x = self.json_content_rect.x + 50 - self.json_scroll_x
                cursor_y = self.json_content_rect.y - self.json_scroll_y
                
                for i, char in enumerate(self.json_text):
                    if i == self.json_cursor_pos:
                        if clip_rect.collidepoint((cursor_x, cursor_y)):
                            pygame.draw.line(self.screen, self.text_color,
                                           (cursor_x, cursor_y),
                                           (cursor_x, cursor_y + line_height))
                        break
                    
                    if char == '\n':
                        cursor_x = self.json_content_rect.x + 50 - self.json_scroll_x
                        cursor_y += line_height
                    else:
                        cursor_x += self.json_font.size(char)[0]
            
            # Draw scrollbars
            # Vertical scrollbar
            max_vscroll = max(0, len(lines) * line_height - self.json_content_rect.height)
            if max_vscroll > 0:
                vscroll_height = (self.json_content_rect.height / (len(lines) * line_height)) * self.json_vscroll_rect.height
                vscroll_y = (self.json_scroll_y / max_vscroll) * (self.json_vscroll_rect.height - vscroll_height)
                vscroll_rect = pygame.Rect(
                    self.json_vscroll_rect.x,
                    self.json_vscroll_rect.y + vscroll_y,
                    self.json_vscroll_rect.width,
                    vscroll_height
                )
                pygame.draw.rect(self.screen, (100, 100, 100), self.json_vscroll_rect)
                pygame.draw.rect(self.screen, (150, 150, 150), vscroll_rect)
            
            # Horizontal scrollbar
            max_hscroll = max(0, self.get_max_line_width() * self.json_char_width - self.json_content_rect.width)
            if max_hscroll > 0:
                hscroll_width = (self.json_content_rect.width / (self.get_max_line_width() * self.json_char_width)) * self.json_hscroll_rect.width
                hscroll_x = (self.json_scroll_x / max_hscroll) * (self.json_hscroll_rect.width - hscroll_width)
                hscroll_rect = pygame.Rect(
                    self.json_hscroll_rect.x + hscroll_x,
                    self.json_hscroll_rect.y,
                    hscroll_width,
                    self.json_hscroll_rect.height
                )
                pygame.draw.rect(self.screen, (100, 100, 100), self.json_hscroll_rect)
                pygame.draw.rect(self.screen, (150, 150, 150), hscroll_rect)
        
        # Draw JSON save button
        self.screen.blit(self.json_save_button.image, self.json_save_button.rect)
        text_surface = self.text_font.render("Save JSON", True, self.text_color)
        text_rect = text_surface.get_rect(center=self.json_save_button.rect.center)
        self.screen.blit(text_surface, text_rect)
        
        # Draw new type input
        pygame.draw.rect(self.screen, (100, 100, 100), self.new_type_input_rect)
        text_surface = self.text_font.render(self.new_type_text, True, self.text_color)
        self.screen.blit(text_surface, (self.new_type_input_rect.x + 5, self.new_type_input_rect.y + 5))
        
        # Draw blinking cursor if input is active
        if self.input_active:
            current_time = pygame.time.get_ticks()
            if current_time - self.cursor_timer > self.cursor_blink_speed:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = current_time
            
            if self.cursor_visible:
                cursor_x = self.new_type_input_rect.x + 5 + text_surface.get_width()
                cursor_y = self.new_type_input_rect.y + 5
                pygame.draw.line(self.screen, self.text_color,
                               (cursor_x, cursor_y),
                               (cursor_x, cursor_y + 20))
        
        # Draw buttons with text
        self.screen.blit(self.new_type_button.image, self.new_type_button.rect)
        text_surface = self.text_font.render("New Type", True, self.text_color)
        text_rect = text_surface.get_rect(center=self.new_type_button.rect.center)
        self.screen.blit(text_surface, text_rect)
        
        if self.selected_type:
            self.screen.blit(self.new_object_button.image, self.new_object_button.rect)
            text_surface = self.text_font.render("New Object", True, self.text_color)
            text_rect = text_surface.get_rect(center=self.new_object_button.rect.center)
            self.screen.blit(text_surface, text_rect)
        
        # Update display
        pygame.display.flip()

    def run(self):
        """Main loop for the object manager"""
        running = True
        while running:
            for event in pygame.event.get():
                self.handle_events(event)
            
            self.render()

# Add main block to run the manager
if __name__ == "__main__":
    # Initialize pygame
    pygame.init()
    
    # Create the screen with reduced height
    screen = pygame.display.set_mode((1024, 600))  # Reduced height from 768 to 600
    pygame.display.set_caption("Object Manager")
    
    # Create and run the object manager
    manager = ObjectManager(screen)
    manager.run() 