import pygame
from config import CURSOR_SIZE, CURSOR_TYPES

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
        self.cursor_size = CURSOR_SIZE  # Use configured cursor size
        self.cursors = {
            cursor_type: self.cursor_spritesheet.subsurface((x, y, self.cursor_size, self.cursor_size))
            for cursor_type, (x, y) in CURSOR_TYPES.items()
        }
        self.current_cursor = 'normal'
        
        # Create a dedicated surface for the cursor
        self.cursor_surface = pygame.Surface((self.cursor_size, self.cursor_size), pygame.SRCALPHA)
        self.cursor_surface.fill((0, 0, 0, 0))  # Make it transparent
        self.cursor_surface.blit(self.cursors['normal'], (0, 0))  # Initialize with normal cursor
        
        # Hide the default cursor
        pygame.mouse.set_visible(False)
        
        self._initialized = True

    def set_cursor(self, cursor_type: str) -> None:
        """
        Set the current cursor type.
        
        Args:
            cursor_type: The type of cursor to display ('normal', 'hover', or 'aim')
        """
        if cursor_type in self.cursors and cursor_type != self.current_cursor:
            self.current_cursor = cursor_type
            # Update cursor surface with new cursor
            self.cursor_surface.fill((0, 0, 0, 0))  # Clear the surface
            self.cursor_surface.blit(self.cursors[cursor_type], (0, 0))

    def get_current_cursor(self) -> pygame.Surface:
        """
        Get the current cursor surface.
        
        Returns:
            pygame.Surface: The current cursor surface
        """
        return self.cursors[self.current_cursor]

    def render(self, screen: pygame.Surface) -> None:
        """
        Render the cursor on the screen.
        
        Args:
            screen: The pygame surface to render on
        """
        # Get current mouse position
        current_pos = pygame.mouse.get_pos()
        screen_width, screen_height = screen.get_size()
        
        # Calculate cursor position (centered on mouse)
        cursor_x = current_pos[0] - self.cursor_size // 2
        cursor_y = current_pos[1] - self.cursor_size // 2
        
        # Clamp cursor position to screen boundaries
        cursor_x = max(0, min(cursor_x, screen_width - self.cursor_size))
        cursor_y = max(0, min(cursor_y, screen_height - self.cursor_size))
        
        # Draw the cursor
        screen.blit(self.cursor_surface, (cursor_x, cursor_y)) 