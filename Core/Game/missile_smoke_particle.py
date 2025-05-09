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

    def draw(self, surface, position=None):
        if self.alpha > 0:
            s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, int(self.alpha)), (int(self.radius), int(self.radius)), int(self.radius))
            pos = position if position is not None else self.position
            surface.blit(s, (pos[0] - self.radius, pos[1] - self.radius))