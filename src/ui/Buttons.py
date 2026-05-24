import pygame as pyg
from utils.paths import get_asset_path


def _load_sheet(filename, n_frames, frame_w, frame_h):
    """Load n_frames horizontal sprite frames from a sheet in buttons/21-MENUS/."""
    path = get_asset_path("buttons", "21-MENUS", filename)
    sheet = pyg.image.load(path).convert_alpha()
    frames = []
    for i in range(n_frames):
        frames.append(sheet.subsurface(i * frame_w, 0, frame_w, frame_h))
    return frames


# Common dimensions for all main-menu buttons
_H          = 32
_IDLE_W     = 1260 // 12   # 105 px  — 12 frames
_PRESS_W    = 420  // 4    # 105 px  —  4 frames
_UNPRESS_W  = 420  // 4    # 105 px  —  4 frames


class PlayButton:
    def __init__(self):
        self.play_button_frames           = _load_sheet("BUTTONS-IDLE-PLAY-Sheet.png",       12, _IDLE_W,    _H)
        self.play_button_frames_pressed   = _load_sheet("BUTTONS-PRESSED-PLAY-Sheet.png",     4, _PRESS_W,   _H)
        self.play_button_frames_unpressed = _load_sheet("BUTTONS-UNPRESSED-PLAY-Sheet.png",   4, _UNPRESS_W, _H)


class OptionsButton:
    def __init__(self):
        self.settings_button_frames           = _load_sheet("BUTTONS-IDLE-OPTIONS-Sheet.png",       12, _IDLE_W,    _H)
        self.settings_button_frames_pressed   = _load_sheet("BUTTONS-PRESSED-OPTIONS-Sheet.png",     4, _PRESS_W,   _H)
        self.settings_button_frames_unpressed = _load_sheet("BUTTONS-UNPRESSED-OPTIONS-Sheet.png",   4, _UNPRESS_W, _H)


class ExitButton:
    def __init__(self):
        self.exit_button_frames           = _load_sheet("BUTTONS-IDLE-EXIT-Sheet.png",   12, _IDLE_W,  _H)
        self.exit_button_frames_pressed   = _load_sheet("BUTTONS-PRESSED-EXIT-Sheet.png", 4, _PRESS_W, _H)
        # No UNPRESSED sheet for Exit → action fires right after PRESSED
        self.exit_button_frames_unpressed = []
