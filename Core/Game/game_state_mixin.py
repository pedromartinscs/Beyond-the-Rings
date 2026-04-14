import sys

import pygame
import random

from Core.Game.animation_manager import AnimationManager
from Core.Game.game_combat import GameCombat
from Core.Game.game_economy import GameEconomy
from Core.Game.game_object_factory import GameObjectFactory
from Core.Game.game_production import GameProduction
from Core.Game.game_selection import GameSelection
from Core.Game.game_world import GameWorld
from Core.Game.object_collection import ObjectCollection


class GameStateMixin:
    def _initialize_audio(self):
        pygame.mixer.init()
        current_track = random.randint(1, 5)
        self.music_file = f"Music/Beyond The Rings Ambience_{current_track}.ogg"
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        pygame.mixer.music.load(self.music_file)
        pygame.mixer.music.play(-1, 0.0)

    def _initialize_credits(self):
        self._economy = GameEconomy(self.object_collection)

    def _initialize_object_system(self):
        self.object_collection = ObjectCollection()
        self.animation_manager = AnimationManager()
        self.object_factory = GameObjectFactory(self.object_collection, self.animation_manager)
        self._world = GameWorld(self)

    def _initialize_combat_state(self):
        self._combat = GameCombat(self)
        self._production = GameProduction(self)

    def _initialize_input_state(self):
        self._selection = GameSelection(self)

    @property
    def game_world(self):
        return self._world

    @property
    def game_combat(self):
        return self._combat

    @property
    def game_selection(self):
        return self._selection

    @property
    def game_production(self):
        return self._production

    @property
    def game_economy(self):
        return self._economy

    @property
    def selected_object(self):
        return self._selection.selected_object

    @selected_object.setter
    def selected_object(self, value):
        self._selection.set_selected_object(value)

    @property
    def active_attacks(self):
        return self._combat.active_attacks

    @property
    def attack_cooldown(self):
        return self._combat.attack_cooldown

    @property
    def objects(self):
        return self._world.objects

    @objects.setter
    def objects(self, value):
        self._world.objects = value

    @property
    def spatial_grid(self):
        return self._world.spatial_grid

    @spatial_grid.setter
    def spatial_grid(self, value):
        self._world.spatial_grid = value

    @property
    def grid_cell_size(self):
        return self._world.grid_cell_size

    @grid_cell_size.setter
    def grid_cell_size(self, value):
        self._world.grid_cell_size = value

    @property
    def tiles(self):
        return self._world.tiles

    @tiles.setter
    def tiles(self, value):
        self._world.tiles = value

    @property
    def tile_cache(self):
        return self._world.tile_cache

    @tile_cache.setter
    def tile_cache(self, value):
        self._world.tile_cache = value

    @property
    def map(self):
        return self._world.map

    @map.setter
    def map(self, value):
        self._world.map = value

    @property
    def map_width(self):
        return self._world.map_width

    @map_width.setter
    def map_width(self, value):
        self._world.map_width = value

    @property
    def map_height(self):
        return self._world.map_height

    @map_height.setter
    def map_height(self, value):
        self._world.map_height = value

    @property
    def map_surface(self):
        return self._world.map_surface

    @map_surface.setter
    def map_surface(self, value):
        self._world.map_surface = value

    def _initialize_render_state(self):
        self.dirty_rects = []
        self.visible_objects_cache = []
        self.last_camera_x = 0
        self.last_camera_y = 0
        self.camera_moved = True
        self.last_camera_pos = (0, 0)
        self.visible_area = None
        self.background_surface = pygame.Surface((self.screen_width, self.screen_height))
        self.background_surface.fill((0, 0, 0))

    def handle_next_action(self):
        if not self.next_action:
            return None

        action = self.next_action
        self.next_action = None

        if action == "main_menu":
            from Core.Menu.main_menu import MainMenu

            return MainMenu(self.screen)
        if action == "options":
            raise NotImplementedError("Options menu not yet implemented")
        if action == "quit":
            pygame.quit()
            sys.exit()

        return None

    @property
    def credits(self):
        return self._economy.credits

    @credits.setter
    def credits(self, value):
        self._economy.credits = value

    def add_credits(self, amount):
        self._economy.add_credits(amount)

    def remove_credits(self, amount):
        return self._economy.remove_credits(amount)

    def has_enough_credits(self, amount):
        return self._economy.has_enough_credits(amount)

    def update_object_charge_bars(self, current_time):
        for obj in self.objects:
            if obj.get('charge_percent', 1.0) >= 1.0:
                continue

            metadata = self.object_collection.get_object_metadata(obj['type'], obj['id'])
            cooldown_duration = obj.get('charge_duration')
            if cooldown_duration is None:
                cooldown_duration = (
                    metadata.get('properties', {}).get('cooldown', 1000)
                    if metadata
                    else 1000
                )

            if cooldown_duration <= 0:
                obj['charge_percent'] = 1.0
                continue

            elapsed = current_time - obj.get('last_charge_time', 0)
            obj['charge_percent'] = min(1.0, elapsed / cooldown_duration)
