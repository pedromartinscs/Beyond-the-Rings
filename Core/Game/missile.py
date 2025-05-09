import math

import pygame

from Core.Game.missile_smoke_particle import SmokeParticle

class Missile:
    def __init__(self, origin, target, speed=4, orientation=0):
        self.origin = origin
        self.target = target
        self.position = list(origin)
        self.speed = speed
        self.finished = False
        self.smoke = []
        self.orientation = orientation
        
        dx = target[0] - origin[0]
        dy = target[1] - origin[1]
        dist = math.hypot(dx, dy)
        self.direction = (dx / dist, dy / dist)

    def update(self):
        if self.finished:
            return

        # movimentação
        self.position[0] += self.direction[0] * self.speed
        self.position[1] += self.direction[1] * self.speed

        # distância até o alvo
        dx = self.target[0] - self.position[0]
        dy = self.target[1] - self.position[1]
        if math.hypot(dx, dy) < self.speed:
            self.finished = True

        # gera fumaça
        self.smoke.append(SmokeParticle(tuple(self.position)))

        # atualiza partículas
        self.smoke = [s for s in self.smoke if s.update()]

    def render(self, surface, image, camera_x=0, camera_y=0):
        # desenha fumaça primeiro
        for s in self.smoke:
            # Adjust smoke position for camera offset
            smoke_x = s.position[0] - camera_x
            smoke_y = s.position[1] - camera_y
            s.draw(surface, (smoke_x, smoke_y))

        if not self.finished:
            # Adjust missile position for camera offset
            missile_x = self.position[0] - camera_x
            missile_y = self.position[1] - camera_y
            surface.blit(image, (missile_x - 8, missile_y - 8))
