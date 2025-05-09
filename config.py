"""
Configuration file for Beyond the Rings game.
Contains all constants, paths, and settings used throughout the game.
"""

import os

# Screen settings
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Asset paths
ASSETS_DIR = "Assets"
IMAGES_DIR = os.path.join(ASSETS_DIR, "Images")
MUSIC_DIR = os.path.join(ASSETS_DIR, "Music")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "Sounds")
MAPS_DIR = os.path.join(ASSETS_DIR, "Maps")

# UI settings
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
BUTTON_SPACING = 20
PANEL_HEIGHT = 200
PANEL_HANDLE_HEIGHT = 20
PANEL_ANIMATION_SPEED = 10

# Panel settings
PANEL = {
    'height': 200,
    'handle_height': 20,
    'animation_speed': 10,
    'cap_width': 60,
    'arrow_width': 20,
    'margin': 20,
    'left_area_size': 150,
    'right_area_width': 100,
    'area_height': 150,
    'box_margin': 1,
    'box_color': (48, 82, 101),
    'tooltip': {
        'delay': 1500,
        'padding': 8,
        'margin': 5,
        'bg_color': (40, 40, 40),
        'text_color': (255, 255, 255),
        'border_color': (100, 100, 100),
        'border_width': 1,
        'max_width': 300
    }
}

# Vertical Panel settings
VERTICAL_PANEL = {
    'width': 200,
    'height': 350,
    'handle_width': 20,
    'animation_speed': 20,
    'button': {
        'width': 180,
        'height': 40,
        'spacing': 12,
        'start_x': 10,
        'start_y': 30
    }
}

# Cursor settings
CURSOR_SIZE = 32
CURSOR_TYPES = {
    'normal': (0, 0),
    'hover': (32, 0),
    'aim': (64, 0),
    'build': (96, 0)
}

# Game settings
TILE_SIZE = 32
CAMERA_SPEED = 5
MINIMAP_SIZE = 150

# Colors
COLORS = {
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'gray': (200, 200, 200),
    'dark_gray': (50, 50, 50),
    'selection_ring': (255, 255, 0)
}

# Font sizes
FONT_SIZES = {
    'small': 12,
    'medium': 16,
    'large': 20,
    'title': 24
}

# Music and sound settings
MUSIC_VOLUME = 0.5
SOUND_VOLUME = 0.7
HOVER_SOUND = "hover.wav"
BACKGROUND_MUSIC = "672781__bertsz__cyberpunk_dump.flac" 