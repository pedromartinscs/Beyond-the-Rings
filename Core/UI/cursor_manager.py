import pygame

class CursorManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CursorManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Load cursor spritesheet
        self.cursor_spritesheet = pygame.image.load("Images/cursors.png").convert_alpha()
        self.cursor_size = 32  # Size of each cursor in the spritesheet
        self.cursors = {
            'normal': self.cursor_spritesheet.subsurface((0, 0, self.cursor_size, self.cursor_size)),
            'hover': self.cursor_spritesheet.subsurface((self.cursor_size, 0, self.cursor_size, self.cursor_size)),
            'aim': self.cursor_spritesheet.subsurface((self.cursor_size * 2, 0, self.cursor_size, self.cursor_size))
        }
        self.current_cursor = 'normal'
        self.last_cursor = None
        self.last_pos = None
        self.last_rect = None
        self.background = None  # Store the background under the cursor
        pygame.mouse.set_visible(False)  # Hide the default cursor
        self._initialized = True

    def set_cursor(self, cursor_type):
        """Set the current cursor type"""
        if cursor_type in self.cursors:
            self.current_cursor = cursor_type

    def get_current_cursor(self):
        """Get the current cursor surface"""
        return self.cursors[self.current_cursor]

    def render(self, screen):
        """Render the cursor on the screen"""
        # Get current mouse position
        current_pos = pygame.mouse.get_pos()
        screen_width, screen_height = screen.get_size()
        
        # Get current cursor
        cursor = self.cursors[self.current_cursor]
        
        # Calculate cursor position (centered on mouse)
        cursor_x = current_pos[0] - self.cursor_size // 2
        cursor_y = current_pos[1] - self.cursor_size // 2
        
        # Clamp cursor position to screen boundaries
        cursor_x = max(0, min(cursor_x, screen_width - self.cursor_size))
        cursor_y = max(0, min(cursor_y, screen_height - self.cursor_size))
        
        # Create current cursor rect
        current_rect = pygame.Rect(cursor_x, cursor_y, self.cursor_size, self.cursor_size)
        
        # If cursor moved or changed type, restore the background
        if self.last_rect and (current_pos != self.last_pos or self.current_cursor != self.last_cursor):
            if self.background:
                screen.blit(self.background, self.last_rect)
        
        try:
            # Store the background under the current cursor position
            self.background = screen.subsurface(current_rect).copy()
            
            # Draw the cursor
            screen.blit(cursor, (cursor_x, cursor_y))
            
            # Update last position, cursor type, and rect
            self.last_pos = current_pos
            self.last_cursor = self.current_cursor
            self.last_rect = current_rect
        except ValueError:
            # If we can't create a subsurface (e.g., at screen edges), just draw the cursor
            screen.blit(cursor, (cursor_x, cursor_y))
            self.background = None
            self.last_rect = None 