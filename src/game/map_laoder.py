import os

import pygame as pyg

from ui.console import print_info

MAP_PATH_BACKGROUND = "assets/maps/map-1-BACKGROUND-Sheet.png"
MAP_PATH_FOREGROUND = "assets/maps/map-1-FOREGROUND-Sheet.png"
COLLISION_THICKNESS = 10
MAP1_COLLISIONS = [
    pyg.Rect(0, 0, 142, 723),
    pyg.Rect(0, 556, 1139, COLLISION_THICKNESS),
    pyg.Rect(1139, 0, COLLISION_THICKNESS, 723),
    pyg.Rect(0, 221 - COLLISION_THICKNESS, 1279, COLLISION_THICKNESS),
]


class MapLoader:
    def __init__(self, map_data):

        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        print_info(f"MapLoader initialized. Base path: {base_path}")

        self.map_path_back = os.path.join(base_path, MAP_PATH_BACKGROUND)
        self.map_path_fore = os.path.join(base_path, MAP_PATH_FOREGROUND)

    def load_map(self):
        background = pyg.image.load(self.map_path_back)
        if pyg.display.get_surface() is not None:
            background = background.convert()
        foreground = pyg.image.load(self.map_path_fore)
        if pyg.display.get_surface() is not None:
            foreground = foreground.convert_alpha()

        print_info("Map layers loaded successfully")
        return background, foreground
