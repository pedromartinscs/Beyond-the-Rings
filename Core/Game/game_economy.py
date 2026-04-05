import pygame


class GameEconomy:
    def __init__(self, object_collection):
        self.object_collection = object_collection
        self.credits = 5000
        self.credit_image = pygame.image.load("Images/credit.png").convert_alpha()
        self.credit_font = pygame.font.Font(None, 32)
        self.last_credit_update = pygame.time.get_ticks()

    def update_credits(self, objects, current_time):
        if current_time - self.last_credit_update < 1000:
            return

        for obj in objects:
            if obj['type'] != 'building' or obj['health'] <= 0:
                continue

            metadata = self.object_collection.get_object_metadata(obj['type'], obj['id'])
            properties = metadata.get('properties', {}) if metadata else {}

            if properties.get('is_ore_gold', False) or properties.get('is_ore_iron', False):
                profit_rate = properties.get('profit_rate', 0)
                self.add_credits(profit_rate)

        self.last_credit_update = current_time

    def add_credits(self, amount):
        self.credits += amount

    def remove_credits(self, amount):
        if self.credits >= amount:
            self.credits -= amount
            return True
        return False

    def has_enough_credits(self, amount):
        return self.credits >= amount

    def render_credits(self, screen, dirty_rects):
        credit_x = 10
        credit_y = 15

        screen.blit(self.credit_image, (credit_x, credit_y))

        credit_text = f"$ {self.credits:,}"
        credit_surface = self.credit_font.render(credit_text, True, (255, 255, 255))
        text_x = credit_x + 20
        text_y = credit_y + (self.credit_image.get_height() - credit_surface.get_height()) // 2 + 2
        screen.blit(credit_surface, (text_x, text_y))

        credit_rect = pygame.Rect(
            credit_x,
            credit_y,
            self.credit_image.get_width(),
            self.credit_image.get_height(),
        )
        dirty_rects.append(credit_rect)
