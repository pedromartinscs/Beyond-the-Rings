import math

import pygame

from Core.Game.missile_smoke_particle import SmokeParticle

class Missile:
    def __init__(self, origin_position, target_position, origin, target, speed=4, orientation=0):
        self.origin_position = origin_position
        self.target_position = target_position
        self.origin = origin
        self.target = target
        self.position = list(origin_position)
        self.speed = speed
        self.finished = False
        self.smoke = []
        self.orientation = orientation
        
        dx = target_position[0] - origin_position[0]
        dy = target_position[1] - origin_position[1]
        dist = math.hypot(dx, dy)
        self.direction = (dx / dist, dy / dist)

    def update(self):
        if self.finished:
            return

        # movimentação
        self.position[0] += self.direction[0] * self.speed
        self.position[1] += self.direction[1] * self.speed

        # distância até o alvo
        dx = self.target_position[0] - self.position[0]
        dy = self.target_position[1] - self.position[1]
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
