import os

import pygame

from Core.UI.button import Button


class PanelActionGrid:
    def __init__(self, middle_area_width, object_collection):
        self.middle_area_width = middle_area_width
        self.object_collection = object_collection

        self.button_width = 32
        self.button_height = 32
        self.spacing_x = 8
        self.spacing_y = 8
        self.max_cols = 6
        self.start_y = 30
        self.box_color = (48, 82, 101)
        self.box_margin = 1
        self.title_font = pygame.font.Font(None, 16)
        self.description_font = pygame.font.Font(None, 14)

        self.middle_buttons = []
        self.description_boxes = []
        self.current_tooltip = None

    def update_for_object(self, selected_object):
        self.middle_buttons = []
        self.description_boxes = []

        if not selected_object:
            return

        metadata = self.object_collection.get_object_metadata(selected_object['type'], selected_object['id'])
        if not metadata or 'buttons' not in metadata or not metadata['buttons']:
            return

        total_buttons = len(metadata['buttons'])
        actual_cols = min(self.max_cols, total_buttons)
        if actual_cols == 0:
            return

        total_width = self.middle_area_width - (self.spacing_x * (actual_cols - 1))
        box_width = (total_width - (self.button_width * actual_cols)) // actual_cols
        start_x = (
            self.middle_area_width
            - (actual_cols * (self.button_width + box_width + self.spacing_x) - self.spacing_x)
        ) // 2

        for i, button_data in enumerate(metadata['buttons']):
            col = i % actual_cols
            row = i // actual_cols
            x = start_x + col * (self.button_width + self.spacing_x + box_width)
            y = self.start_y + row * (self.button_height + self.spacing_y)

            action = button_data['action']
            default_button = "Images/tiny_button_basic.png"
            default_button_hover = "Images/tiny_button_basic_hover.png"
            action_button = f"Images/{action}_tiny_button_basic.png"
            action_button_hover = f"Images/{action}_tiny_button_basic_hover.png"
            button_image = action_button if os.path.exists(action_button) else default_button
            button_hover_image = (
                action_button_hover if os.path.exists(action_button_hover) else default_button_hover
            )

            button = Button(
                x,
                y,
                0,
                0,
                self.button_width,
                self.button_height,
                "",
                None,
                button_image,
                button_hover_image,
            )

            box = {
                'rect': pygame.Rect(
                    x + self.button_width + self.box_margin,
                    y,
                    box_width,
                    self.button_height,
                ),
                'title': button_data['name'],
                'description': button_data['description'],
                'button': button,
                'action': button_data['action'],
                'lines': [],
                'is_wrapped': False,
            }
            box['surface'] = pygame.Surface((box_width, self.button_height), pygame.SRCALPHA)
            box['surface'].fill(self.box_color)

            title_surface = self.title_font.render(box['title'], True, (255, 255, 255))
            desc_surface = self.description_font.render(box['description'], True, (200, 200, 200))
            title_x = (box_width - title_surface.get_width()) // 2
            desc_x = (box_width - desc_surface.get_width()) // 2
            title_y = 5
            desc_y = title_y + title_surface.get_height() + 2
            box['surface'].blit(title_surface, (title_x, title_y))
            box['surface'].blit(desc_surface, (desc_x, desc_y))

            self.middle_buttons.append(button)
            self.description_boxes.append(box)

    def render(self, screen, middle_x, middle_y):
        mouse_pos = pygame.mouse.get_pos()
        self.current_tooltip = None

        for box in self.description_boxes:
            button = box['button']
            original_x = button.rect.x
            original_y = button.rect.y

            button.rect.x = middle_x + original_x
            button.rect.y = middle_y + original_y
            button.draw(screen)

            desc_rect = box['rect'].copy()
            desc_rect.x = middle_x + box['rect'].x
            desc_rect.y = middle_y + box['rect'].y
            screen.blit(box['surface'], desc_rect)

            if button.rect.collidepoint(mouse_pos):
                self.current_tooltip = box['description']

            button.rect.x = original_x
            button.rect.y = original_y

    def get_clicked_box(self, mouse_pos, middle_x, middle_y):
        for button in self.middle_buttons:
            temp_rect = pygame.Rect(
                middle_x + button.rect.x,
                middle_y + button.rect.y,
                button.rect.width,
                button.rect.height,
            )
            if temp_rect.collidepoint(mouse_pos):
                return next((box for box in self.description_boxes if box['button'] == button), None)
        return None
