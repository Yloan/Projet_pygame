#Launcher des maps
import pygame as pyg
import os
from ui.console import print_info


class MapLoader:
    def __init__(self, map_data):
        # base_path: two levels up from this file -> project root where `assets/` is located
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        print_info(f"MapLoader initialized. Base path: {base_path}")

        self.map_path_back = os.path.join(base_path, 'assets', 'maps', 'map-1-BACKGROUND-Sheet.png')
        self.map_path_fore = os.path.join(base_path, 'assets', 'maps', 'map-1-FOREGROUND-Sheet.png')

    def load_map(self):
        # Charger les images de la carte
        background = pyg.image.load(self.map_path_back)
        # convertir seulement si une surface d'affichage est disponible
        if pyg.display.get_surface() is not None:
            background = background.convert()

        foreground = pyg.image.load(self.map_path_fore)
        if pyg.display.get_surface() is not None:
            foreground = foreground.convert_alpha()
        return background, foreground