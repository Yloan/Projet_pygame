import os

import pygame as pyg

from ui.console import print_info, print_warning

COLLISION_THICKNESS = 10


MAP1_COLLISIONS = [
    pyg.Rect(0, 0, 142, 723),
    pyg.Rect(0, 556, 1139, COLLISION_THICKNESS),
    pyg.Rect(1139, 0, COLLISION_THICKNESS, 723),
    pyg.Rect(0, 221 - COLLISION_THICKNESS, 1279, COLLISION_THICKNESS),
]

# Map 2 — collisions réelles de la map désert
MAP2_COLLISIONS = [
    pyg.Rect(0, 0, 9, 723),  # left wall
    pyg.Rect(0, 700, 1267, COLLISION_THICKNESS),  # floor
    pyg.Rect(1269, 0, COLLISION_THICKNESS, 723),  # right wall
    pyg.Rect(0, 200 - COLLISION_THICKNESS, 1279, COLLISION_THICKNESS),  # top platform
    pyg.Rect(1064, 511, 1202 - 1064, 646 - 511),  # plateforme droite
    pyg.Rect(781, 565, 673 - 565, 1202 - 1064 - 26),  # plateforme centre-droite
    pyg.Rect(66, 200, 673 - 565, 1202 - 1064 - 26),  # plateforme gauche
    pyg.Rect(91, 528, 229 - 91, 650 - 528),  # bloc bas-gauche
    pyg.Rect(1122, 220, 1202 - 1064, 646 - 511),  # bloc haut-droite
]

# Map 3 — grotte
MAP3_COLLISIONS = MAP1_COLLISIONS

MAP_COLLISIONS = {
    1: MAP1_COLLISIONS,
    2: MAP2_COLLISIONS,
    3: MAP3_COLLISIONS,
}

ACTIVE_COLLISIONS = MAP1_COLLISIONS

MAP_PATHS = {
    1: {
        "back": "assets/maps/map_1/map-1-BACKGROUND-Sheet.png",
        "fore": "assets/maps/map_1/map-1-FOREGROUND-Sheet.png",
    },
    2: {
        "back": "assets/maps/map_2/map-2.png",
        "fore": None,
    },
    3: {
        "back": "assets/maps/map_3/map-3.png",
        "fore": None,
    },
}

MAP_FALLBACK_BACK = "assets/maps/map-1-BACKGROUND-Sheet.png"
MAP_FALLBACK_FORE = "assets/maps/map-1-FOREGROUND-Sheet.png"


class MapLoader:
    def __init__(self, map_data, index=1):
        global ACTIVE_COLLISIONS

        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        print_info(f"MapLoader initialized for map {index}.")

        paths = MAP_PATHS.get(index)
        if paths:
            back = paths["back"]
            fore = paths["fore"]
        else:
            print_warning(f"Map index {index} not found — falling back to map 1")
            back = MAP_FALLBACK_BACK
            fore = MAP_FALLBACK_FORE

        self.map_path_back = os.path.join(base_path, back)
        self.map_path_back = os.path.join(base_path, back)
        if not os.path.exists(self.map_path_back):
            print_warning(f"Background not found: {back} — using fallback")
            self.map_path_back = os.path.join(base_path, MAP_FALLBACK_BACK)

        if fore is None:
            self.map_path_fore = None
        else:
            self.map_path_fore = os.path.join(base_path, fore)
            if not os.path.exists(self.map_path_fore):
                print_warning(f"Foreground not found: {fore} — using fallback")
                self.map_path_fore = os.path.join(base_path, MAP_FALLBACK_FORE)

        # Switch active collisions for this map
        ACTIVE_COLLISIONS = MAP_COLLISIONS.get(index, MAP1_COLLISIONS)
        print_info(
            f"Active collisions set for map {index} ({len(ACTIVE_COLLISIONS)} rects)"
        )

    def load_map(self):
        background = pyg.image.load(self.map_path_back)
        if pyg.display.get_surface() is not None:
            background = background.convert()

        if self.map_path_fore is None:
            foreground = pyg.Surface(background.get_size(), pyg.SRCALPHA)
        else:
            foreground = pyg.image.load(self.map_path_fore)
            if pyg.display.get_surface() is not None:
                foreground = foreground.convert_alpha()

        print_info("Map layers loaded successfully")
        return background, foreground
