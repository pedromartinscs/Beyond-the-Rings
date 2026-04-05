import pygame

from Core.Game.vertical_panel import VerticalPanel
from Core.UI.panel import Panel


class GameInterface:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen

        self.bottom_panel = Panel(self.screen, game.object_collection)
        self.bottom_panel.game = game
        self.side_panel = VerticalPanel(self.screen, game)

    @property
    def is_targeting(self):
        return self.bottom_panel.is_targeting

    @property
    def current_action(self):
        return self.bottom_panel.current_action

    def handle_events(self, event):
        bottom_result = self.bottom_panel.handle_events(event)
        if bottom_result:
            return True

        side_result = self.side_panel.handle_events(event)
        if side_result:
            return True

        return False

    def update(self):
        self.side_panel.update()

    def render_panels(self):
        self.side_panel.render()
        self.bottom_panel.render()

    def render_selected_object_card(self):
        selected_object = self.game.selected_object
        should_remove = self.bottom_panel.render_selected_object_card(selected_object)

        if should_remove and selected_object in self.game.objects:
            self.game.objects.remove(selected_object)
            self.game.game_world.remove_object_from_grid(selected_object)
            self.game.game_selection.clear_selection()

    def set_selected_object(self, obj):
        self.bottom_panel.set_selected_object(obj)

    def clear_selected_object(self):
        self.game.game_selection.clear_selection()

    def cancel_targeting(self):
        self.bottom_panel.cancel_targeting()

    def handle_target_selection(self, target_object):
        return self.bottom_panel.handle_target_selection(target_object)

    def is_click_on_panels(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos
        panel_y = self.bottom_panel.current_y
        panel_handle_height = self.bottom_panel.handle_height

        if self.bottom_panel.is_open or panel_y < self.game.screen_height - panel_handle_height:
            if mouse_y >= panel_y:
                return True

        if self.side_panel.is_open or self.side_panel.current_x > -self.side_panel.width:
            if 0 <= mouse_x <= self.side_panel.width:
                return True

        return False

    def sync_cursor(self, cursor_manager, event):
        if self.bottom_panel.is_targeting:
            if self.bottom_panel.current_action == "attack":
                cursor_manager.set_cursor("aim")
            elif self.bottom_panel.current_action == "build":
                cursor_manager.set_cursor("build")
        elif event.type == pygame.MOUSEMOTION:
            cursor_manager.set_cursor("normal")
