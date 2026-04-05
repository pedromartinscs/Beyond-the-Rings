import pygame


class GameMinimap:
    def __init__(self, game):
        self.game = game
        self.size = 150
        self.x = game.screen_width - self.size - 20
        self.y = 20
        self.surface = pygame.Surface((self.size, self.size))
        self.surface.fill((0, 0, 0))
        self.scale = 1.0
        self.map_surface = None
        self.is_dragging = False
        self.last_mouse_pos = None

    def set_map(self, map_surface, map_width, map_height):
        self.scale = min(self.size / map_width, self.size / map_height)
        scaled_width = int(map_width * self.scale)
        scaled_height = int(map_height * self.scale)
        self.map_surface = pygame.transform.scale(map_surface, (scaled_width, scaled_height))

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_clicked(event.pos):
                self.is_dragging = True
                self.last_mouse_pos = event.pos
                return True, self.get_world_position(event.pos)

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_dragging = self.is_dragging
            self.is_dragging = False
            self.last_mouse_pos = None
            return was_dragging, None

        if event.type == pygame.MOUSEMOTION and self.is_dragging and self.last_mouse_pos:
            if self.is_clicked(event.pos):
                self.last_mouse_pos = event.pos
                return True, self.get_world_position(event.pos)

        return False, None

    def is_clicked(self, pos):
        return self.get_rect().collidepoint(pos)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def get_world_position(self, screen_pos):
        if not self.map_surface:
            return None

        rel_x = screen_pos[0] - self.x
        rel_y = screen_pos[1] - self.y

        minimap_x = (self.size - self.map_surface.get_width()) // 2
        minimap_y = (self.size - self.map_surface.get_height()) // 2

        world_x = int((rel_x - minimap_x) / self.scale)
        world_y = int((rel_y - minimap_y) / self.scale)
        return world_x, world_y

    def render(self, screen, camera_x, camera_y, camera_width, camera_height):
        self.surface.fill((0, 0, 0))

        if self.map_surface:
            minimap_x = (self.size - self.map_surface.get_width()) // 2
            minimap_y = (self.size - self.map_surface.get_height()) // 2

            self.surface.blit(self.map_surface, (minimap_x, minimap_y))

            viewport_rect = pygame.Rect(
                minimap_x + camera_x * self.scale,
                minimap_y + camera_y * self.scale,
                camera_width * self.scale,
                camera_height * self.scale,
            )
            pygame.draw.rect(self.surface, (255, 255, 255), viewport_rect, 2)

        screen.blit(self.surface, (self.x, self.y))
