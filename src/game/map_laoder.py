import os

import pygame as pyg

from ui.console import print_info


class MapLoader:
    def __init__(self, map_data, index):

        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        print_info(f"MapLoader initialized. Base path: {base_path}")

        self.maps = {
            1: [
                "assets/maps/map_1/map-1-BACKGROUND-Sheet.png",
                "assets/maps/map_1/map-1-FOREGROUND-Sheet.png",
            ]
        }

        bg = self.maps[index][0]
        fg = self.maps[index][1]

        self.map_path_back = os.path.join(base_path, bg)
        self.map_path_fore = os.path.join(base_path, fg)

    def load_map(self):
        background = pyg.image.load(self.map_path_back)
        if pyg.display.get_surface() is not None:
            background = background.convert()
        foreground = pyg.image.load(self.map_path_fore)
        if pyg.display.get_surface() is not None:
            foreground = foreground.convert_alpha()

        print_info("Map layers loaded successfully")
        return background, foreground
