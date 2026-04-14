import math

import pygame


class SmokeParticle:
    def __init__(self, position):
        self.position = list(position)
        self.radius = 2
        self.alpha = 200
        self.color = (120, 120, 120)

    def update(self):
        self.alpha -= 20
        self.radius += 0.5
        return self.alpha > 0

    def render(self, surface, position=None):
        if self.alpha <= 0:
            return

        smoke_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            smoke_surface,
            (*self.color, int(self.alpha)),
            (int(self.radius), int(self.radius)),
            int(self.radius),
        )
        draw_position = position if position is not None else self.position
        surface.blit(smoke_surface, (draw_position[0] - self.radius, draw_position[1] - self.radius))


class MissileProjectile:
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
        self.direction = (0, 0) if dist == 0 else (dx / dist, dy / dist)

    def update(self):
        if self.finished:
            return

        self.position[0] += self.direction[0] * self.speed
        self.position[1] += self.direction[1] * self.speed

        dx = self.target_position[0] - self.position[0]
        dy = self.target_position[1] - self.position[1]
        if math.hypot(dx, dy) < self.speed:
            self.finished = True

        self.smoke.append(SmokeParticle(tuple(self.position)))
        self.smoke = [particle for particle in self.smoke if particle.update()]

    def render(self, surface, image, camera_x=0, camera_y=0):
        for particle in self.smoke:
            smoke_x = particle.position[0] - camera_x
            smoke_y = particle.position[1] - camera_y
            particle.render(surface, (smoke_x, smoke_y))

        if not self.finished:
            missile_x = self.position[0] - camera_x
            missile_y = self.position[1] - camera_y
            surface.blit(image, (missile_x - 8, missile_y - 8))


class ExplosionEffect:
    def __init__(self, position, frames, frame_duration=2):
        self.frames = frames
        self.frame_duration = frame_duration
        self.current_frame = 0
        self.timer = 0
        self.position = position
        self.finished = False

    def update(self):
        self.timer += 1
        if self.timer >= self.frame_duration:
            self.timer = 0
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                self.finished = True

    def render(self, surface, camera_x=0, camera_y=0):
        if self.finished:
            return

        image = self.frames[self.current_frame]
        screen_x = self.position[0] - camera_x
        screen_y = self.position[1] - camera_y
        rect = image.get_rect(center=(screen_x, screen_y))
        surface.blit(image, rect)


class GameCombat:
    def __init__(self, game):
        self.game = game
        self.active_attacks = {}
        self.attack_cooldown = 1000
        self.projectiles = []
        self.active_explosions = []
        self.projectile_images = self._load_projectile_images()
        self.explosion_images = self._load_explosion_images()

    def update_attacks(self):
        for attacker_unique_id, attack_data in list(self.active_attacks.items()):
            target_unique_id = attack_data['target_unique_id']

            attacker = self.game.game_world.get_object_by_unique_id(attacker_unique_id)
            target = self.game.game_world.get_object_by_unique_id(target_unique_id)

            if attacker and target:
                if attacker.get('is_attacking') is False:
                    self.game.animation_manager.set_animation_state(attacker_unique_id, "static")
                    if attacker_unique_id in self.active_attacks:
                        del self.active_attacks[attacker_unique_id]
                    attacker.pop('is_attacking', None)
                    attacker['charge_percent'] = 1.0
                    continue

                if target['health'] <= 0 and target.get('max_health', 100) != -1:
                    self.game.animation_manager.set_animation_state(attacker_unique_id, "static")
                    del self.active_attacks[attacker_unique_id]
                    self.game.animation_manager.set_animation_state(target_unique_id, "destruction")
                    attacker['charge_percent'] = 1.0
                    continue

                attacker_metadata = self.game.object_collection.get_object_metadata(
                    attacker['type'],
                    attacker['id'],
                )
                if not attacker_metadata:
                    del self.active_attacks[attacker_unique_id]
                    continue

                properties = attacker_metadata.get('properties', {})
                attack_range = properties.get('attack_range', 0)

                dx = target['x'] - attacker['x']
                dy = target['y'] - attacker['y']
                distance = (dx * dx + dy * dy) ** 0.5

                if distance > attack_range:
                    self.game.animation_manager.set_animation_state(attacker_unique_id, "static")
                    del self.active_attacks[attacker_unique_id]
                    continue

                current_time = pygame.time.get_ticks()
                time_since_last_shot = current_time - attack_data['last_attack_time']
                cooldown = properties.get('cooldown', self.attack_cooldown)
                attacker['charge_percent'] = min(1.0, time_since_last_shot / cooldown)

                if time_since_last_shot >= cooldown:
                    angle = self.calculate_angle(attacker['x'], attacker['y'], target['x'], target['y'])
                    nearest_direction = self.get_nearest_direction(
                        angle,
                        attacker_metadata['visuals']['directions'],
                    )
                    attacker['turret_direction'] = self.game.animation_manager.get_current_direction(
                        attacker_unique_id
                    )

                    if nearest_direction != attacker['turret_direction']:
                        self.game.animation_manager.set_target_direction(attacker_unique_id, nearest_direction)
                    else:
                        self.game.animation_manager.set_animation_state(attacker_unique_id, "fire")
                        attack_data['last_attack_time'] = current_time
                        attacker['last_charge_time'] = current_time

                        attacker_world_x, attacker_world_y = self.calculate_projectile_origin(attacker)
                        target_world_x = target['x'] * self.game.tile_size + self.game.tile_size // 2
                        target_world_y = target['y'] * self.game.tile_size + self.game.tile_size // 2

                        self.spawn_projectile(
                            (attacker_world_x, attacker_world_y),
                            (target_world_x, target_world_y),
                            attacker,
                            target,
                            speed=10,
                            orientation=nearest_direction,
                        )
            else:
                self.game.animation_manager.set_animation_state(attacker_unique_id, "static")
                del self.active_attacks[attacker_unique_id]

    def update_effects(self):
        self.update_projectiles()
        self.update_explosions()

    def update_projectiles(self):
        remaining_projectiles = []

        for projectile in self.projectiles:
            projectile.update()
            if projectile.finished:
                self.active_explosions.append(
                    ExplosionEffect(tuple(projectile.position), self.explosion_images)
                )
                if projectile.target and projectile.target['max_health'] != -1:
                    projectile.target['health'] -= projectile.origin.get('damage', 1)
                    if projectile.target['health'] <= 0:
                        projectile.origin['charge_percent'] = 1.0
            else:
                remaining_projectiles.append(projectile)

        self.projectiles = remaining_projectiles

    def update_explosions(self):
        for explosion in self.active_explosions:
            explosion.update()

    def render_effects(self, screen, camera_x=0, camera_y=0):
        self.render_projectiles(screen, camera_x, camera_y)
        self.render_explosions(screen, camera_x, camera_y)

    def render_projectiles(self, screen, camera_x=0, camera_y=0):
        for projectile in self.projectiles:
            image_index = projectile.orientation // 45
            projectile.render(screen, self.projectile_images[image_index], camera_x, camera_y)

    def render_explosions(self, screen, camera_x=0, camera_y=0):
        remaining_explosions = []

        for explosion in self.active_explosions:
            explosion.render(screen, camera_x, camera_y)
            if not explosion.finished:
                remaining_explosions.append(explosion)

        self.active_explosions = remaining_explosions

    def handle_attack_command(self, attack_result):
        attacker = attack_result['attacker']
        target = attack_result['target']
        metadata = self.game.object_collection.get_object_metadata(attacker['type'], attacker['id'])
        if not metadata:
            return

        if attack_result['in_range']:
            cooldown = metadata.get('properties', {}).get('cooldown', self.attack_cooldown)
            self.active_attacks[attacker['unique_id']] = {
                'attacker_type': attacker['type'],
                'attacker_id': attacker['id'],
                'attacker_unique_id': attacker['unique_id'],
                'target_type': target['type'],
                'target_id': target['id'],
                'target_unique_id': target['unique_id'],
                'last_attack_time': pygame.time.get_ticks() - cooldown,
                'cooldown': cooldown,
            }
            attacker['is_attacking'] = True
        elif attack_result['is_unit']:
            pass
        else:
            pass

    def calculate_angle(self, start_x, start_y, target_x, target_y):
        dx = target_x - start_x
        dy = target_y - start_y
        angle = math.degrees(math.atan2(-dy, dx)) + 90
        return (angle + 360) % 360

    def get_nearest_direction(self, angle, directions):
        return min(directions, key=lambda direction: min(abs(direction - angle), 360 - abs(direction - angle)))

    def calculate_projectile_origin(self, attacker):
        angle_map_x = {0: 0, 45: 13, 90: 32, 135: 21, 180: 0, 225: -21, 270: -32, 315: -13}
        angle_map_y = {0: -7, 45: -8, 90: -16, 135: -32, 180: -32, 225: -32, 270: -16, 315: -8}
        attacker_world_x = (
            attacker['x'] * self.game.tile_size
            + self.game.tile_size // 2
            + angle_map_x[attacker['turret_direction']]
        )
        attacker_world_y = (
            attacker['y'] * self.game.tile_size
            + self.game.tile_size // 2
            + angle_map_y[attacker['turret_direction']]
        )
        return attacker_world_x, attacker_world_y

    def spawn_projectile(self, origin_position, target_position, origin, target, speed=4, orientation=0):
        projectile = MissileProjectile(
            origin_position,
            target_position,
            origin,
            target,
            speed,
            orientation,
        )
        self.projectiles.append(projectile)

    def _load_projectile_images(self):
        projectile_images = []
        for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
            projectile_image = pygame.image.load(f"Images/Missiles/{angle}.png")
            projectile_images.append(projectile_image)
        return projectile_images

    def _load_explosion_images(self):
        explosion_sheet = pygame.image.load("Images/Missiles/Explosion/spritesheet.png").convert_alpha()
        explosion_images = []
        for index in range(4):
            frame = explosion_sheet.subsurface((index * 32, 0, 32, 32))
            explosion_images.append(frame)
        return explosion_images
