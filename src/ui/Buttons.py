import pygame as pyg
from utils.paths import get_asset_path

class PlayButton:
    def __init__(self):
        self.play_button_frames = []
        frames_PlayButton = 12
        height = 32
        width_frame = 1260//frames_PlayButton

        path = get_asset_path("buttons", "21-MENUS", "BUTTONS-IDLE-PLAY-Sheet.png")

        for i in range(frames_PlayButton):
            self.play_button_frames.append(
                pyg.image.load(
                    path
                ).subsurface(i * width_frame, 0, width_frame, height)
            )



class OptionsButton:
    def __init__(self):
        self.settings_button_frames = []
        frames_OptionsButton = 12
        height = 32
        width_frame = 1260//frames_OptionsButton

        path = get_asset_path("buttons", "21-MENUS", "BUTTONS-IDLE-OPTIONS-Sheet.png")

        for i in range(frames_OptionsButton):
            self.settings_button_frames.append(
                pyg.image.load(
                    path
                ).subsurface(i * width_frame, 0, width_frame, height)
            )

class ExitButton:
    def __init__(self):
        self.exit_button_frames = []
        frames_ExitButton = 12
        height = 32
        width_frame = 1260//frames_ExitButton

        path = get_asset_path("buttons", "21-MENUS", "BUTTONS-IDLE-EXIT-Sheet.png")

        for i in range(frames_ExitButton):
            self.exit_button_frames.append(
                pyg.image.load(
                    path
                ).subsurface(i * width_frame, 0, width_frame, height)
            )

