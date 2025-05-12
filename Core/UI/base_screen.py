import pygame
from typing import Optional, Any
from Core.UI.cursor_manager import CursorManager
from config import COLORS, FONT_SIZES

class BaseScreen:
    def __init__(self, screen: pygame.Surface) -> None:
        """
        Initialize the base screen.
        
        Args:
            screen: The pygame surface to render on
        """
        self.screen: pygame.Surface = screen
        self.cursor_manager: CursorManager = CursorManager()
        self.next_action: Optional[callable] = None
        # Initialize cursor to normal state
        self.set_cursor('normal')
        
    def set_cursor(self, cursor_type: str) -> None:
        """
        Set the current cursor type.
        
        Args:
            cursor_type: The type of cursor to display ('normal', 'hover', or 'aim')
        """
        self.cursor_manager.set_cursor(cursor_type)
        
    def handle_events(self, event: pygame.event.Event) -> None:
        """
        Handle events for the screen.
        
        Args:
            event: The pygame event to handle
        """
        if event.type == pygame.MOUSEMOTION:
            # Update cursor based on button interactions
            mouse_pos: tuple[int, int] = pygame.mouse.get_pos()
            # Default to normal cursor
            self.set_cursor('normal')
            
            # Check for buttons if they exist
            if hasattr(self, 'buttons'):
                for button in self.buttons:
                    if button.rect.collidepoint(event.pos):
                        self.set_cursor('hover')
                        break
            elif hasattr(self, 'back_button'):
                if self.back_button.rect.collidepoint(event.pos):
                    self.set_cursor('hover')
    
    def update(self) -> Optional[Any]:
        """
        Update the screen state.
        
        Returns:
            Optional[Any]: The next screen to switch to, or None if no change
        """
        if self.next_action:
            next_screen = self.next_action()
            self.next_action = None
            if next_screen:
                return next_screen
        return None
    
    def render(self) -> None:
        """
        Default implementation that handles cursor rendering.
        Child classes should override this method to add their own rendering logic
        and call super().render() at the end to ensure cursor is rendered on top.
        """
        self.cursor_manager.render(self.screen) 