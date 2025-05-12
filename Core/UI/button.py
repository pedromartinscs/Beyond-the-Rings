import pygame
import math
from typing import Tuple

class Button:
    def __init__(self, x, y, number, spacing, width, height, text, action=None, image_path=None, glow_image_path=None, glow_behind=False):
        render_y = y + number * (height + spacing)
        self.rect = pygame.Rect(x, render_y, width, height)
        self.text = text
        self.action = action
        self.image_path = image_path  # Path to the button image (optional)
        self.glow_image_path = glow_image_path  # Path to the glow image (optional)
        self.glow_behind = glow_behind  # Whether glow should be behind the button
        self.font = pygame.font.Font(None, 36)
        self.text_surface = self.font.render(self.text, True, (0, 0, 0))
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)
        self.is_hovered = False
        self.clicked_state = False
        
        # Load the button image if provided
        if self.image_path:
            self.image = pygame.image.load(self.image_path)
            self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))  # Scale image to button size
        else:
            self.image = None

        # Load the glow image if provided
        if self.glow_image_path:
            self.glow_image = pygame.image.load(self.glow_image_path)
            self.glow_image = pygame.transform.scale(self.glow_image, (self.rect.width, self.rect.height))  # Scale glow image to button size
        else:
            self.glow_image = None

        # Initial glow parameters
        self.glow_alpha = 200  # Initial glow transparency
        self.glow_speed = 10  # Higher speed = faster glow
        self.glow_width = self.rect.width + 3  # Glow width larger than the button
        self.glow_height = self.rect.height + 3  # Glow height larger than the button

    def render_text(self, surface):
        """Render the button text onto the given surface"""
        text_rect = self.text_surface.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
        surface.blit(self.text_surface, text_rect)

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()

        # Check if the button is being hovered over or clicked
        if self.rect.collidepoint(mouse_pos):
            self.is_hovered = True
            
            if self.glow_behind:
                # Draw glow behind the button
                if self.glow_image:
                    screen.blit(self.glow_image, self.rect.topleft)
                screen.blit(self.image, self.rect.topleft)
            else:
                # Draw glow instead of the button
                if self.glow_image:
                    screen.blit(self.glow_image, self.rect.topleft)
                else:
                    screen.blit(self.image, self.rect.topleft)

            if mouse_pressed[0]:  # Left-click pressed
                self.clicked_state = True
            else:
                self.clicked_state = False
        else:
            self.is_hovered = False
            self.clicked_state = False
            # Draw the button image when not hovered
            screen.blit(self.image, self.rect.topleft)

        # Draw the button text on top of the image (if desired)
        screen.blit(self.text_surface, self.text_rect)

    def is_clicked(self, mouse_pos: Tuple[int, int] = None) -> bool:
        """
        Check if the button is clicked.
        
        Args:
            mouse_pos: Optional mouse position tuple (x, y). If None, uses current mouse position.
            
        Returns:
            bool: True if the button is clicked, False otherwise
        """
        if mouse_pos is None:
            mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        if self.rect.collidepoint(mouse_pos) and mouse_pressed[0]:
            return True
        return False
