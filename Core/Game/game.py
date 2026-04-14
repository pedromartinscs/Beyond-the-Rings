import sys

import pygame

from Core.Game.game_camera import GameCamera
from Core.Game.game_interface import GameInterface
from Core.Game.game_minimap import GameMinimap
from Core.Game.game_state_mixin import GameStateMixin
from Core.UI.base_screen import BaseScreen


class Game(BaseScreen, GameStateMixin):
    def __init__(self, screen):
        super().__init__(screen)
        self._initialize_screen_state(screen)
        self._initialize_runtime_state()
        self._initialize_interface()
        self._initialize_world()
        self._finalize_initial_visibility()

    @property
    def game_camera(self):
        return self._camera

    @property
    def game_minimap(self):
        return self._minimap

    @property
    def game_interface(self):
        return self._interface

    def handle_events(self, event):
        if self._interface.handle_events(event):
            return

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        minimap_handled, world_position = self._minimap.handle_events(event)
        if minimap_handled:
            if world_position:
                self._camera.center_on_world_position(*world_position)
            return

        self._sync_cursor(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_button_down(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            self._handle_mouse_button_up()
        elif event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion()

    def update(self):
        current_time = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()

        self._economy.update_credits(self.objects, current_time)
        self._camera.update_edge_scroll(mouse_pos)
        self._combat.update_attacks()
        self.update_object_charge_bars(current_time)
        self._production.update()
        self._combat.update_effects()

        next_screen = self.handle_next_action()
        if next_screen:
            return next_screen

        self._interface.update()
        return None

    def render(self):
        self._begin_render_frame()
        self._world.render_map(self.screen)
        self._selection.render_back_overlay(self.screen, self.visible_objects_cache, self.dirty_rects)

        objects_to_remove = self._world.render_objects(self.screen, self.dirty_rects)
        self._selection.render_front_overlay(
            self.screen,
            self.visible_objects_cache,
            objects_to_remove,
            self.dirty_rects,
        )
        self._world.remove_destroyed_objects(objects_to_remove)

        self._combat.render_effects(self.screen, self.camera_x, self.camera_y)
        self._minimap.render(
            self.screen,
            self.camera_x,
            self.camera_y,
            self.camera_width,
            self.camera_height,
        )
        self.dirty_rects.append(self._minimap.get_rect())

        self._interface.render_panels()
        self._interface.render_selected_object_card()
        self._economy.render_credits(self.screen, self.dirty_rects)

        self._finish_render_frame()

    def _initialize_screen_state(self, screen):
        self.screen_height = screen.get_height()
        self.screen_width = screen.get_width()
        self.panel_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.tile_size = 32

    def _initialize_runtime_state(self):
        self._initialize_audio()
        self._initialize_object_system()
        self._initialize_credits()
        self._initialize_combat_state()
        self._initialize_render_state()
        self._initialize_input_state()
        self._camera = GameCamera(self)
        self._minimap = GameMinimap(self)

    def _initialize_interface(self):
        self._interface = GameInterface(self)

    def _initialize_world(self):
        self._world.initialize()
        self._minimap.set_map(
            self.map_surface,
            self.map_width * self.tile_size,
            self.map_height * self.tile_size,
        )
        self._camera.initialize()

    def _finalize_initial_visibility(self):
        self._camera.update_visible_area()
        self._camera.update_visible_objects()

    def _sync_cursor(self, event):
        self._interface.sync_cursor(self.cursor_manager, event)

    def _handle_mouse_button_down(self, event):
        mouse_pos = pygame.mouse.get_pos()

        if event.button == 1:
            self._handle_left_click(mouse_pos)
        elif event.button == 3:
            self._handle_right_click()

    def _handle_left_click(self, mouse_pos):
        if self._interface.is_targeting:
            target_object = self._selection.get_object_at_screen_position(mouse_pos[0], mouse_pos[1])

            if target_object:
                attack_result = self._interface.handle_target_selection(target_object)
                if attack_result and attack_result['action'] == 'attack':
                    self._combat.handle_attack_command(attack_result)
            else:
                self._interface.cancel_targeting()
                self.cursor_manager.set_cursor("normal")
            return

        if not self._interface.is_click_on_panels(mouse_pos):
            self._selection.select_object_at_screen_position(mouse_pos[0], mouse_pos[1])

    def _handle_right_click(self):
        if self._interface.is_targeting:
            self._interface.cancel_targeting()
            self.cursor_manager.set_cursor("normal")

    def _handle_mouse_button_up(self):
        pass

    def _handle_mouse_motion(self):
        pass

    def _begin_render_frame(self):
        self.screen.fill((0, 0, 0))
        self.dirty_rects = [pygame.Rect(0, 0, self.screen_width, self.screen_height)]

    def _finish_render_frame(self):
        self.cursor_manager.render(self.screen)

        cursor_size = self.cursor_manager.cursor_size
        cursor_x, cursor_y = pygame.mouse.get_pos()
        cursor_rect = pygame.Rect(
            cursor_x - cursor_size // 2,
            cursor_y - cursor_size // 2,
            cursor_size,
            cursor_size,
        )
        self.dirty_rects.append(cursor_rect)

        if self.dirty_rects:
            pygame.display.update(self.dirty_rects)

    def handle_builder_unit_action(self, selected_object):
        self._production.enqueue_builder_unit(selected_object)

    def cancel_production_queue_item(self, selected_object, queue_index):
        return self._production.cancel_queue_item(selected_object, queue_index)
