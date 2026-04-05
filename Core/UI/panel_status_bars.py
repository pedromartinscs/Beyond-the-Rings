import pygame

from config import FONT_SIZES


class PanelStatusBars:
    def __init__(self, screen, left_area_size):
        self.screen = screen
        self.left_area_size = left_area_size

        self.life_bar_left = pygame.image.load("Images/life_bar_left.png").convert_alpha()
        self.life_bar_right = pygame.image.load("Images/life_bar_right.png").convert_alpha()
        self.life_bar_energy_stretch = pygame.image.load("Images/life_bar_energy_stretch.png").convert_alpha()
        self.life_bar_energy_tip = pygame.image.load("Images/life_bar_energy_tip.png").convert_alpha()
        self.life_bar_charge_stretch = pygame.image.load("Images/life_bar_charge_stretch.png").convert_alpha()
        self.life_bar_charge_tip = pygame.image.load("Images/life_bar_charge_tip.png").convert_alpha()
        self.life_bar_font = pygame.font.Font(None, FONT_SIZES['small'])

    def render(self, obj, left_area_rect):
        if not obj or 'health' not in obj or 'max_health' not in obj:
            return False

        bar_width = self.left_area_size - 20
        bar_height = 10
        bar_x = left_area_rect.x + 10
        bar_y = left_area_rect.y + self.left_area_size - bar_height + 12

        current_health = obj['health']
        max_health = obj['max_health']
        charge_percent = obj.get('charge_percent', 0)

        if max_health == -1:
            health_percent = 1.0
            text_surface = self.life_bar_font.render("8", True, (255, 255, 255))
            text_surface = pygame.transform.rotate(text_surface, 90)
        else:
            health_percent = min(1.0, max(0.0, current_health / max_health))
            health_text = f"{int(health_percent * 100)}%"
            text_surface = self.life_bar_font.render(health_text, True, (255, 255, 255))

        left_width = self.life_bar_left.get_width()
        background_x = bar_x - 10
        self.screen.blit(self.life_bar_left, (background_x, bar_y))
        right_pos = (background_x + left_width, bar_y)
        self.screen.blit(self.life_bar_right, right_pos)

        fill_width = int((bar_width - 19) * health_percent)
        if fill_width > 0:
            energy_x = bar_x + 20
            self.screen.blit(self.life_bar_energy_tip, (energy_x, bar_y))

            for x in range(energy_x + 2, energy_x + fill_width - 2):
                self.screen.blit(self.life_bar_energy_stretch, (x, bar_y))

            self.screen.blit(self.life_bar_energy_tip, (energy_x + fill_width - 2, bar_y))

        charge_stretch_width = int(96 * charge_percent)
        charge_x = right_pos[0]

        for x in range(charge_x, charge_x + charge_stretch_width):
            self.screen.blit(self.life_bar_charge_stretch, (x, bar_y))

        if charge_stretch_width > 0:
            self.screen.blit(self.life_bar_charge_tip, (charge_x + charge_stretch_width, bar_y))

        text_x = background_x + (left_width - text_surface.get_width()) // 2
        text_y = bar_y + (bar_height - text_surface.get_height()) // 2 + 10
        self.screen.blit(text_surface, (text_x, text_y))

        return current_health <= 0 and max_health != -1
