import pygame


class SmokeParticle:
    def __init__(self, position):
        self.position = list(position)
        self.radius = 4
        self.alpha = 200
        self.color = (120, 120, 120)

    def update(self):
        self.alpha -= 20
        self.radius += 0.25  # opcional
        return self.alpha > 0

    def draw(self, surface):
        if self.alpha > 0:
            s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, int(self.alpha)), (int(self.radius), int(self.radius)), int(self.radius))
            surface.blit(s, (self.position[0] - self.radius, self.position[1] - self.radius))