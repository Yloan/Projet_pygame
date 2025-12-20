#Caractéristiques des characters
import os
import pygame as pyg
base_path = os.path.dirname(os.path.abspath(__file__))

class Furnace:
    def __init__(self):
        self.health = 100
        self.speed = 5
        self.position = (0, 0)

        #initialisation des assets
        sprite_path_IDLE = os.path.join(base_path, 'assets', 'sprites' , 'FIRE-IDLE-Sheet.png')
        sprite_path_WALK = os.path.join(base_path, 'assets', 'sprites' , 'FIRE-WALK-Sheet.png')

        self.player_spritesheet_IDLE = pyg.image.load(sprite_path_IDLE)
        self.player_spritesheet_WALK = pyg.image.load(sprite_path_WALK)

        self.frame_width = 40
        self.frame_height = 40

        self.frames_IDLE = []
        num_frames = 12

        for i in range(num_frames):
            frame = self.player_spritesheet_IDLE.subsurface((i * self.frame_width, 0, self.frame_width, self.frame_height))
            self.frames_IDLE.append(frame)

        self.fram_WALK = []
        num_frame = 4

        for i in range(num_frame):
            frame = self.player_spritesheet_WALK.subsurface((i * self.frame_width, 0, self.frame_width, self.frame_height))
            self.fram_WALK.append(frame)

        self.frame_WALK_left = []
        for i in range(num_frame):
            frame = self.player_spritesheet_WALK.subsurface((i * self.frame_width, 0, self.frame_width, self.frame_height))
            frame_flipped = pyg.transform.flip(frame, True, False)
            self.frame_WALK_left.append(frame_flipped)
        
        self.frame_IDLE_left = []
        for i in range(num_frames):
            frame = self.player_spritesheet_IDLE.subsurface((i * self.frame_width, 0, self.frame_width, self.frame_height))
            frame_flipped = pyg.transform.flip(frame, True, False)
            self.frame_IDLE_left.append(frame_flipped)

    def move(self, direction):
        if direction == "up":
            self.position = (self.position[0], self.position[1] - self.speed)
        elif direction == "down":
            self.position = (self.position[0], self.position[1] + self.speed)
        elif direction == "left":
            self.position = (self.position[0] - self.speed, self.position[1])
        elif direction == "right":
            self.position = (self.position[0] + self.speed, self.position[1])

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def heal(self, amount):
        self.health += amount
        if self.health > 100:
            self.health = 100

    def get_status(self):
        return {
            "health": self.health,
            "position": self.position
        }

    def skill1(self):
        pass
    
    def skill2(self):
        pass

    def skill3(self):
        pass