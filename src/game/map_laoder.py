"""
MAP LOADER MODULE - Game map loading and management

This module handles loading game maps from files:
- Loading background and foreground layers
- Resolving asset paths correctly
- Sprite caching and optimization
- Collision detection setup

Current Map Layers:
- Background: Decorative elements (mountains, sky, etc.)
- Foreground: Interactive elements (walls, obstacles, etc.)

Recommendations:
1. Implement map tiling system for larger maps
2. Add collision detection based on foreground layer
3. Implement map data format (JSON/XML) for easier editing
4. Add support for multiple map levels
5. Implement parallel loading to avoid freezing
"""

import pygame as pyg
import os
from ui.console import print_info


# ============================================================================
# MAP FILE PATHS AND CONFIGURATION
# ============================================================================
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
        # ====================================================================
        # RESOLVE BASE PATH
        # ====================================================================
        # Navigate up two levels from this file to project root
        base_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..')
        )
        print_info(f"MapLoader initialized. Base path: {base_path}")

        # ====================================================================
        # CONSTRUCT FULL MAP PATHS
        # ====================================================================
        self.map_path_back = os.path.join(base_path, MAP_PATH_BACKGROUND)
        self.map_path_fore = os.path.join(base_path, MAP_PATH_FOREGROUND)

    def load_map(self):
        """
        Load map background and foreground layers.
        
        Returns:
            tuple: (background_surface, foreground_surface) pygame Surfaces
                   Both surfaces are converted for optimal rendering
        """
        # ====================================================================
        # LOAD BACKGROUND LAYER
        # ====================================================================
        background = pyg.image.load(self.map_path_back)
        # Convert to display format for faster rendering
        # Only convert if display surface is available
        if pyg.display.get_surface() is not None:
            background = background.convert()

        # ====================================================================
        # LOAD FOREGROUND LAYER
        # ====================================================================
        foreground = pyg.image.load(self.map_path_fore)
        # Convert with alpha channel for transparency support
        if pyg.display.get_surface() is not None:
            foreground = foreground.convert_alpha()
            
        print_info("Map layers loaded successfully")
        return background, foreground
