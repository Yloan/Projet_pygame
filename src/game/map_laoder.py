import os

import pygame as pyg

from ui.console import print_info

COLLISION_THICKNESS = 10
MAP1_COLLISIONS = [
    pyg.Rect(0, 0, 142, 723),
    pyg.Rect(0, 556, 1139, COLLISION_THICKNESS),
    pyg.Rect(1139, 0, COLLISION_THICKNESS, 723),
    pyg.Rect(0, 221 - COLLISION_THICKNESS, 1279, COLLISION_THICKNESS),
]

MAP_PATHS = {
    1: {
        "back": "assets/maps/map_1/map-1-BACKGROUND-Sheet.png",
        "fore": "assets/maps/map_1/map-1-FOREGROUND-Sheet.png",
    },
}

MAP_FALLBACK_BACK = "assets/maps/map-1-BACKGROUND-Sheet.png"
MAP_FALLBACK_FORE = "assets/maps/map-1-FOREGROUND-Sheet.png"


class MapLoader:
    def __init__(self, map_data, index=1):
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        print_info(f"MapLoader initialized. Base path: {base_path}")

        paths = MAP_PATHS.get(index)
        if paths:
            back = paths["back"]
            fore = paths["fore"]
        else:
            back = MAP_FALLBACK_BACK
            fore = MAP_FALLBACK_FORE

        self.map_path_back = os.path.join(base_path, back)
        self.map_path_fore = os.path.join(base_path, fore)

        if not os.path.exists(self.map_path_back):
            self.map_path_back = os.path.join(base_path, MAP_FALLBACK_BACK)
        if not os.path.exists(self.map_path_fore):
            self.map_path_fore = os.path.join(base_path, MAP_FALLBACK_FORE)

    def load_map(self):
        background = pyg.image.load(self.map_path_back)
        if pyg.display.get_surface() is not None:
            background = background.convert()
        foreground = pyg.image.load(self.map_path_fore)
        if pyg.display.get_surface() is not None:
            foreground = foreground.convert_alpha()

        print_info("Map layers loaded successfully")
        return background, foreground
