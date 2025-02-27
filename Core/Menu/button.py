import pygame
import math

class Button:
    def __init__(self, x, y, number, spacing, width, height, text, action=None, image_path=None, glow_image_path=None):
        render_y = y + number * (height + spacing)
        self.rect = pygame.Rect(x, render_y, width, height)
        self.text = text
        self.action = action
        self.image_path = image_path  # Path to the button image (optional)
        self.glow_image_path = glow_image_path  # Path to the glow image (optional)
        self.font = pygame.font.Font(None, 36)
        self.text_surface = self.font.render(self.text, True, (0, 0, 0))
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)
        self.is_hovered = False
        self.clicked_state = False
        
        # Load the button image if provided
        if self.image_path:
            self.button_image = pygame.image.load(self.image_path)
            self.button_image = pygame.transform.scale(self.button_image, (self.rect.width, self.rect.height))  # Scale image to button size

        # Load the glow image if provided
        if self.glow_image_path:
            self.glow_image = pygame.image.load(self.glow_image_path)
            self.glow_image = pygame.transform.scale(self.glow_image, (self.rect.width, self.rect.height))  # Scale glow image to button size

        # Initial glow parameters
        self.glow_alpha = 200  # Initial glow transparency
        self.glow_speed = 10  # Higher speed = faster glow
        self.glow_width = self.rect.width + 3  # Glow width larger than the button
        self.glow_height = self.rect.height + 3  # Glow height larger than the button

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()

        # Check if the button is being hovered over or clicked
        if self.rect.collidepoint(mouse_pos):
            self.is_hovered = True

            # Get the current time in milliseconds (since Pygame was initialized)
            time_elapsed = pygame.time.get_ticks() / 1000.0  # Convert to seconds

            # Calculate a pulsing effect based on the time elapsed
            pulse_factor = math.sin(time_elapsed * self.glow_speed)  # Use sine wave for smooth pulsing

            # Modify the glow width and height based on the time-based pulse factor
            self.glow_width = self.rect.width + 3 + int(abs(pulse_factor) * 5)  # Adjust max pulse size (e.g., 20)
            self.glow_height = self.rect.height + 3 + int(abs(pulse_factor) * 5)
            
            # Calculate the glow transparency based on pulse factor
            self.glow_alpha = 200 + int(abs(pulse_factor) * 20)  # You can tweak the alpha range (e.g., 60 to 90)

            # Ensure alpha stays within valid range (0 to 255)
            self.glow_alpha = min(255, max(0, self.glow_alpha))

            # Resize the glow image (using pygame.transform.scale to resize)
            glow_scaled = pygame.transform.scale(self.glow_image, (self.glow_width, self.glow_height))
            glow_scaled.set_alpha(self.glow_alpha)  # Apply transparency to glow image

            # Position the glow effect behind the button
            glow_rect = glow_scaled.get_rect(center=self.rect.center)
            screen.blit(glow_scaled, glow_rect)  # Draw the glow

            # Draw the button image
            screen.blit(self.button_image, self.rect.topleft)

            if mouse_pressed[0]:  # Left-click pressed
                self.clicked_state = True
            else:
                self.clicked_state = False
        else:
            self.is_hovered = False
            self.clicked_state = False
            # Draw the button image when not hovered
            screen.blit(self.button_image, self.rect.topleft)

        # Draw the button text on top of the image (if desired)
        screen.blit(self.text_surface, self.text_rect)

    def is_clicked(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        if self.rect.collidepoint(mouse_pos) and mouse_pressed[0]:
            return True
        return False
