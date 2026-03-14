import pygame as pyg
import os
from ui.console import print_info


MAP_PATH_BACKGROUND = 'assets/maps/map-1-BACKGROUND-Sheet.png'
MAP_PATH_FOREGROUND = 'assets/maps/map-1-FOREGROUND-Sheet.png'


class MapLoader:
    """
    Map loader class responsible for loading game maps and layers.
    
    Attributes:
        base_path (str): Base path to project assets
        map_path_back (str): Full path to background sprite sheet
        map_path_fore (str): Full path to foreground sprite sheet
    """
    
    def __init__(self, map_data):
        """
        Initialize map loader and resolve asset paths.
        
        Args:
            map_data: Map configuration data (can be None for default map)
        """

        base_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..')
        )
        print_info(f"MapLoader initialized. Base path: {base_path}")

        self.map_path_back = os.path.join(base_path, MAP_PATH_BACKGROUND)
        self.map_path_fore = os.path.join(base_path, MAP_PATH_FOREGROUND)

    def load_map(self):
        """
        Load map background and foreground layers.
        
        Returns:
            tuple: (background_surface, foreground_surface) pygame Surfaces
                   Both surfaces are converted for optimal rendering
        """
        background = pyg.image.load(self.map_path_back)
        if pyg.display.get_surface() is not None:
            background = background.convert()
        foreground = pyg.image.load(self.map_path_fore)
        if pyg.display.get_surface() is not None:
            foreground = foreground.convert_alpha()
            
        print_info("Map layers loaded successfully")
        return background, foreground
