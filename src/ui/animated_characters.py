import pygame as py

from utils.paths import get_asset_path


# CONSTANTS - Animation configuration
DEFAULT_SCALE = 1
DEFAULT_ANIMATION_SPEED = 100
FRAME_SIZE = 40

class IDLE:
    def __init__(self, perso, spritesheet_idle, number_frames):
    
        self.current_frame = 0
        self.IDLE_frames = []
        self.current_delta = 0

        if perso is not None:
            self.image = get_asset_path(
                "sprites", perso, spritesheet_idle
            )
        else :
            self.image = None

        for i in range(number_frames):
            if self.image is not None:
                frame = py.image.load(self.image).subsurface(
                    (i * FRAME_SIZE, 0, FRAME_SIZE, FRAME_SIZE)
                )
                self.IDLE_frames.append(frame)

    def update_animation(self, delta_time):

        # Update idle animation
        self.current_delta += delta_time
        if self.current_delta >= DEFAULT_ANIMATION_SPEED:
            self.current_delta = 0

            if self.current_frame >= len(self.IDLE_frames) - 1:
                self.current_frame = 0
            else:
                self.current_frame += 1

idle_animation = None

if character_clicked == 'Furnace' or 'Water':
    idle_animation = IDLE('Furnace', 'FIRE-IDLE-Sheet.png', 12)

x= 1
y = 1
delta_time = 0
clock = py.clock()

delta_time = delta_time + clock
idle_animation.update_animation(delta_time)

self.screen.blit(idle_animation.IDLE_frames[idle_animation.current_frame], (x,y))
