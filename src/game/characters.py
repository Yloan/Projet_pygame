import pygame as pyg
import os

from utils.paths import get_asset_path
from ui.animated_idle import AnimatedCharacter

FURNACE_FRAME_WIDTH = 40
FURNACE_FRAME_HEIGHT = 40
FURNACE_IDLE_FRAMES = 12
FURNACE_WALK_FRAMES = 4
FURNACE_ANIMATION_IDLE_SPEED = 100  # milliseconds between frames
FURNACE_ANIMATION_WALK_SPEED = 200  # milliseconds between frames

WATER_FRAME_SIZE = 40
WATER_IDLE_FRAMES = 12
WATER_MOVE_FRAMES = 5
WATER_HURT_FRAMES = 5
WATER_SKILL1_FRAMES = 10
WATER_SKILL2_FRAMES = 11
WATER_SKILL3_FRAMES = 19
WATER_ANIMATION_IDLE_SPEED = 100  # milliseconds between frames
WATER_ANIMATION_MOVE_SPEED = 200  # milliseconds between frames
WATER_ANIMATION_SKILL1_SPEED = 100  # milliseconds between frames
WATER_ANIMATION_SKILL2_SPEED = 100  # milliseconds between frames
WATER_ANIMATION_SKILL3_SPEED = 100  # milliseconds between frames


class Furnace:
    def __init__(self):

        self.health = 100
        self.speed = 2
        self.position = (400, 400)

        sprite_path_IDLE = get_asset_path("sprites", "Furnace", "FIRE-IDLE-Sheet.png")
        sprite_path_WALK = get_asset_path("sprites", "Furnace", "FIRE-WALK-Sheet.png")

        self.player_spritesheet_IDLE = pyg.image.load(sprite_path_IDLE)
        self.player_spritesheet_WALK = pyg.image.load(sprite_path_WALK)

        self.frames_IDLE = []
        for i in range(FURNACE_IDLE_FRAMES):
            frame = self.player_spritesheet_IDLE.subsurface(
                (i * FURNACE_FRAME_WIDTH, 0, FURNACE_FRAME_WIDTH, FURNACE_FRAME_HEIGHT)
            )
            self.frames_IDLE.append(frame)

        self.fram_WALK = []
        for i in range(FURNACE_WALK_FRAMES):
            frame = self.player_spritesheet_WALK.subsurface(
                (i * FURNACE_FRAME_WIDTH, 0, FURNACE_FRAME_WIDTH, FURNACE_FRAME_HEIGHT)
            )
            self.fram_WALK.append(frame)

        self.frame_WALK_left = []
        for i in range(FURNACE_WALK_FRAMES):
            frame = self.player_spritesheet_WALK.subsurface(
                (i * FURNACE_FRAME_WIDTH, 0, FURNACE_FRAME_WIDTH, FURNACE_FRAME_HEIGHT)
            )
            frame_flipped = pyg.transform.flip(frame, True, False)
            self.frame_WALK_left.append(frame_flipped)

        self.frame_IDLE_left = []
        for i in range(FURNACE_IDLE_FRAMES):
            frame = self.player_spritesheet_IDLE.subsurface(
                (i * FURNACE_FRAME_WIDTH, 0, FURNACE_FRAME_WIDTH, FURNACE_FRAME_HEIGHT)
            )
            frame_flipped = pyg.transform.flip(frame, True, False)
            self.frame_IDLE_left.append(frame_flipped)
        self.frame_IDLE = 0
        self.frame_WALK = 0
        self.tem_an_IDLE = 0
        self.tem_an_WALK = 0
        self.direction = "right"
        self.is_moving = False

    def move(self, direction):
        if direction == "up":
            self.position = (self.position[0], self.position[1] - self.speed)
        elif direction == "down":
            self.position = (self.position[0], self.position[1] + self.speed)
        elif direction == "left":
            self.position = (self.position[0] - self.speed, self.position[1])
            self.direction = "left"
        elif direction == "right":
            self.position = (self.position[0] + self.speed, self.position[1])
            self.direction = "right"

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def heal(self, amount):
        self.health += amount
        if self.health > 100:
            self.health = 100

    def get_status(self):
        return {"health": self.health, "position": self.position}

    def update_animation(self, delta_time, is_moving):
        self.is_moving = is_moving

        if is_moving:
            # Update walking animation
            self.tem_an_WALK += delta_time
            if self.tem_an_WALK >= FURNACE_ANIMATION_WALK_SPEED:
                self.tem_an_WALK = 0
                if self.frame_WALK >= len(self.fram_WALK) - 1:
                    self.frame_WALK = 0
                else:
                    self.frame_WALK += 1
        else:
            # Update idle animation
            self.tem_an_IDLE += delta_time
            if self.tem_an_IDLE >= FURNACE_ANIMATION_IDLE_SPEED:
                self.tem_an_IDLE = 0
                if self.frame_IDLE >= len(self.frames_IDLE) - 1:
                    self.frame_IDLE = 0
                else:
                    self.frame_IDLE += 1

    def get_current_sprite(self):
        if self.is_moving:
            if self.direction == "left":
                return self.frame_WALK_left[self.frame_WALK]
            else:
                return self.fram_WALK[self.frame_WALK]
        else:
            if self.direction == "left":
                return self.frame_IDLE_left[self.frame_IDLE]
            else:
                return self.frames_IDLE[self.frame_IDLE]

    # SKILL SYSTEM

    def skill1(self):
        """First special skill - To be implemented."""
        pass

    def skill2(self):
        """Second special skill - To be implemented."""
        pass

    def skill3(self):
        """Third special skill - To be implemented."""
        pass

    # GAME LOOP UPDATE

    def update(self):
        pass


class Water:
    def __init__(self):
        # CHARACTER STATS
        self.health = 100
        self.speed = 2
        self.position = (400, 400)
        self.direction = "right"

        # LOAD SPRITE ASSET PATHS
        self.sprite_IDLE = get_asset_path("sprites", "Water", "2-IDLE-Sheet.png")
        self.sprite_MOVE = get_asset_path("sprites", "Water", "2-MOVE-Sheet.png")
        self.sprite_HURT = get_asset_path("sprites", "Water", "2-HURT-Sheet.png")
        self.sprite_DEATH = get_asset_path("sprites", "Water", "2-DEAD-Sheet.png")

        self.sprite_character_skill1 = get_asset_path(
            "sprites", "Water", "2-S1-Sheet.png"
        )
        self.sprite_skill1 = get_asset_path(
            "sprites", "Water", "effect-2-Bash-Sheet.png"
        )

        self.sprite_character_skill2 = get_asset_path(
            "sprites", "Water", "2-S2-Sheet.png"
        )
        self.sprite_skill2 = get_asset_path(
            "sprites", "Water", "effect-2-Bash-Sheet.png"
        )

        self.sprite_character_skill3 = get_asset_path(
            "sprites", "Water", "2-S3-1-Sheet.png"
        )
        self.sprite_skill3 = get_asset_path(
            "sprites", "Water", "effect-2-Bash-Sheet.png"
        )

        # INITIALIZE ANIMATION FRAME LISTS
        self.frames_IDLE = []
        self.frames_IDLE_left = []
        self.frames_MOVE_right = []
        self.frames_MOVE_left = []
        self.frames_HURT = []
        self.frames_DEATH = [pyg.image.load(self.sprite_DEATH)]

        self.frames_character_skill1 = []
        self.frames_character_skill2 = []
        self.frames_character_skill3 = []

        self.frames_character_skill1_left = []
        self.frames_character_skill2_left = []
        self.frames_character_skill3_left = []

        self.frames_effect_character_skill1 = []
        self.frames_effect_character_skill2 = []
        self.frames_effect_character_skill3_1 = []
        self.frames_effect_character_skill3_2 = []

        self.frames_effect_character_skill1_left = []
        self.frames_effect_character_skill2_left = []
        self.frames_effect_character_skill3_1_left = []
        self.frames_effect_character_skill3_2_left = []

        # EXTRACT IDLE ANIMATION FRAMES
        for i in range(WATER_IDLE_FRAMES):
            frame = pyg.image.load(self.sprite_IDLE).subsurface(
                (i * WATER_FRAME_SIZE, 0, WATER_FRAME_SIZE, WATER_FRAME_SIZE)
            )
            self.frames_IDLE.append(frame)
            frame_flipped = pyg.transform.flip(frame, True, False)
            self.frames_IDLE_left.append(frame_flipped)

        # EXTRACT MOVE ANIMATION FRAMES (BOTH DIRECTIONS)
        for i in range(WATER_MOVE_FRAMES):
            frame = pyg.image.load(self.sprite_MOVE).subsurface(
                (i * WATER_FRAME_SIZE, 0, WATER_FRAME_SIZE, WATER_FRAME_SIZE)
            )
            self.frames_MOVE_right.append(frame)
            # Create flipped version for left direction
            frame_flipped = pyg.transform.flip(frame, True, False)
            self.frames_MOVE_left.append(frame_flipped)

        # EXTRACT HURT ANIMATION FRAMES
        for i in range(WATER_HURT_FRAMES):
            frame = pyg.image.load(self.sprite_HURT).subsurface(
                (i * WATER_FRAME_SIZE, 0, WATER_FRAME_SIZE, WATER_FRAME_SIZE)
            )
            self.frames_HURT.append(frame)

        # EXTRACT ATTACK ANIMATION FRAMES

        for i in range(WATER_SKILL1_FRAMES):
            frame = pyg.image.load(self.sprite_character_skill1).subsurface(
                i * WATER_FRAME_SIZE, 0, WATER_FRAME_SIZE, WATER_FRAME_SIZE
            )
            self.frames_character_skill1.append(frame)

            frame_flipped = pyg.transform.flip(frame, True, False)
            self.frames_character_skill1_left.append(frame_flipped)

        for i in range(WATER_SKILL2_FRAMES):
            frame = pyg.image.load(self.sprite_character_skill2).subsurface(
                i * WATER_FRAME_SIZE, 0, WATER_FRAME_SIZE, WATER_FRAME_SIZE
            )
            self.frames_character_skill2.append(frame)

            frame_flipped = pyg.transform.flip(frame, True, False)
            self.frames_character_skill2_left.append(frame_flipped)

        for i in range(WATER_SKILL3_FRAMES):
            frame = pyg.image.load(self.sprite_character_skill3).subsurface(
                i * WATER_FRAME_SIZE, 0, WATER_FRAME_SIZE, WATER_FRAME_SIZE
            )
            self.frames_character_skill3.append(frame)

            frame_flipped = pyg.transform.flip(frame, True, False)
            self.frames_character_skill3_left.append(frame_flipped)

        # EXTRACT ATTACK ANIMATIONS OF THE PROJECTILE


        # ANIMATION STATE VARIABLES
        self.frame_MOVE = 0  # Current move animation frame index
        self.frame_IDLE = 0  # Current idle animation frame index
        self.tem_an_IDLE = 0  # Elapsed time for idle animation
        self.tem_an_MOVE = 0  # Elapsed time for move animation
        self.is_moving = False  # Movement state flag
        self.direction = "right"  # Current direction (left or right)

        # This is the time for the animations of the three skills
        self.frame_character_skill1 = 0
        self.frame_character_skill2 = 0
        self.frame_character_skill3 = 0
        self.tem_an_skill1 = 0
        self.tem_an_skill2 = 0
        self.tem_an_skill3 = 0
        self.is_attacking_skill1 = False
        self.is_attacking_skill2 = False
        self.is_attacking_skill3 = False

        self.frame_effect_skill1 = 0
        self.frame_effect_skill2 = 0
        self.frame_effect_skill3 = 0

        self.loop_animation_skill1 = 0
        self.loop_animation_skill2 = 0
        self.loop_animation_skill3 = 0

    # MOVEMENT METHODS

    def move(self, direction):
        if direction == "up":
            self.position = (self.position[0], self.position[1] - self.speed)
        elif direction == "down":
            self.position = (self.position[0], self.position[1] + self.speed)
        elif direction == "left":
            self.position = (self.position[0] - self.speed, self.position[1])
            self.direction = "left"
        elif direction == "right":
            self.position = (self.position[0] + self.speed, self.position[1])
            self.direction = "right"

    # STATUS AND INFORMATION METHODS

    def get_status(self):
        return {"health": self.health, "position": self.position}

    # HEALTH AND COMBAT METHODS

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0
            self.death()

    def death(self):
        return pyg.image.load(self.sprite_DEATH)

    def heal(self, amount):
        self.health += amount
        if self.health > 100:
            self.health = 100

    # ========================================================================
    # ANIMATION METHODS
    # ========================================================================

    def update_animation(
        self,
        delta_time,
        is_moving,
        is_attacking_skill1,
        is_attacking_skill2,
        is_attacking_skill3,
    ):

        self.is_attacking_skill1 = is_attacking_skill1
        self.is_attacking_skill2 = is_attacking_skill2
        self.is_attacking_skill3 = is_attacking_skill3
        self.is_moving = is_moving

        # SKILL 1
        if self.is_attacking_skill1:
            self.tem_an_skill1 += delta_time
            if self.tem_an_skill1 >= WATER_ANIMATION_SKILL1_SPEED:
                self.tem_an_skill1 = 0
                self.frame_character_skill1 += 1

                if self.frame_character_skill1 >= len(self.frames_character_skill1):
                    self.frame_character_skill1 = 0
                    self.frame_effect_character_skill1 = 0
                    self.is_attacking_skill1 = False

        # SKILL 2
        if self.is_attacking_skill2:
            self.tem_an_skill2 += delta_time
            if self.tem_an_skill2 >= WATER_ANIMATION_SKILL2_SPEED:
                self.tem_an_skill2 = 0
                self.frame_character_skill2 += 1

                if self.frame_character_skill2 >= len(self.frames_character_skill2):
                    self.frame_character_skill2 = 0
                    self.is_attacking_skill2 = False

        # SKILL 3
        if self.is_attacking_skill3:
            self.tem_an_skill3 += delta_time
            if self.tem_an_skill3 >= WATER_ANIMATION_SKILL3_SPEED:
                self.tem_an_skill3 = 0
                # On incrémente l'INDEX
                self.frame_character_skill3 += 1

                # On compare l'index avec la longueur de la LISTE d'images
                if self.frame_character_skill3 >= len(self.frames_character_skill3):
                    self.frame_character_skill3 = 0
                    self.is_attacking_skill3 = False

        if is_moving:
            # Update move animation
            self.tem_an_MOVE += delta_time
            if self.tem_an_MOVE >= WATER_ANIMATION_MOVE_SPEED:
                self.tem_an_MOVE = 0
                if self.frame_MOVE >= len(self.frames_MOVE_right) - 1:
                    self.frame_MOVE = 0
                else:
                    self.frame_MOVE += 1
        else:
            # Update idle animation
            self.tem_an_IDLE += delta_time
            if self.tem_an_IDLE >= WATER_ANIMATION_IDLE_SPEED:
                self.tem_an_IDLE = 0
                if self.frame_IDLE >= len(self.frames_IDLE) - 1:
                    self.frame_IDLE = 0
                else:
                    self.frame_IDLE += 1

    def get_current_sprite(self):

        if self.is_attacking_skill1:
            if self.direction == "left":
                return self.frames_character_skill1_left[self.frame_character_skill1]
            else:
                return self.frames_character_skill1[self.frame_character_skill1]

        if self.is_attacking_skill2:
            if self.direction == "left":
                return self.frames_character_skill2_left[self.frame_character_skill2]
            else:
                return self.frames_character_skill2[self.frame_character_skill2]

        if self.is_attacking_skill3:
            if self.direction == "left":
                return self.frames_character_skill3_left[self.frame_character_skill3]
            else:
                return self.frames_character_skill3[self.frame_character_skill3]

        if self.is_moving:
            if self.direction == "left":
                return self.frames_MOVE_left[self.frame_MOVE]
            else:
                return self.frames_MOVE_right[self.frame_MOVE]
        else:
            if self.direction == "left":
                return self.frames_IDLE_left[self.frame_IDLE]
            else:
                return self.frames_IDLE[self.frame_IDLE]

    # SKILL SYSTEM

    def skill1(self, delta_time, is_attacking_skill1):
        """First special skill - To be implemented."""

        pass

    def skill2(self):
        """Second special skill - To be implemented."""
        pass

    def skill3(self):
        """Third special skill - To be implemented."""
        pass

    # GAME LOOP UPDATE

    def update(self):
        pass


class Character:
    def __init__(self, character_name, config, position=(400, 400), health=100, speed=2):
        self.character_name = character_name
        self.health = health
        self.speed = speed
        self.position = position
        self.direction = "right"
        self.is_moving = False
        self.current_state = 'idle'

        # Config is a dict like:
        # {
        #     'idle': {'filename': 'IDLE-Sheet.png', 'frame_count': 12, 'speed': 100},
        #     'move': {'filename': 'MOVE-Sheet.png', 'frame_count': 5, 'speed': 200},
        # }

        self.animations = {}
        for anim_name, anim_config in config.items():
            self.animations[anim_name] = AnimatedCharacter.from_spritesheet(
                "sprites", character_name, anim_config['filename'],
                frame_width=40, frame_height=40, frame_count=anim_config['frame_count'],
                animation_speed_ms=anim_config['speed']
            )

    def move(self, direction):
        if direction == "up":
            self.position = (self.position[0], self.position[1] - self.speed)
        elif direction == "down":
            self.position = (self.position[0], self.position[1] + self.speed)
        elif direction == "left":
            self.position = (self.position[0] - self.speed, self.position[1])
            self.direction = "left"
        elif direction == "right":
            self.position = (self.position[0] + self.speed, self.position[1])
            self.direction = "right"

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def heal(self, amount):
        self.health += amount
        if self.health > 100:
            self.health = 100

    def get_status(self):
        return {"health": self.health, "position": self.position}

    def update_animation(self, delta_time, is_moving):
        self.is_moving = is_moving
        if is_moving:
            self.current_state = 'move'
        else:
            self.current_state = 'idle'
        self.animations[self.current_state].update(delta_time)

    def get_current_sprite(self):
        anim = self.animations[self.current_state]
        frame = anim.frames[anim.current_frame]
        if self.direction == "left":
            frame = pyg.transform.flip(frame, True, False)
        return frame

    # SKILL SYSTEM - to be implemented per character or generically

    def skill1(self):
        """First special skill - To be implemented."""
        pass

    def skill2(self):
        """Second special skill - To be implemented."""
        pass

    def skill3(self):
        """Third special skill - To be implemented."""
        pass

    # GAME LOOP UPDATE

    def update(self):
        pass


def load_all_characters():
    characters = {}
    base_path = get_asset_path("sprites")
    for i in range(1, 19):  # 1 to 18
        char_name = f"Character-{i}"
        char_path = os.path.join(base_path, char_name)
        if os.path.exists(char_path):
            # Assume standard config if files exist
            idle_file = os.path.join(char_path, "IDLE-Sheet.png")
            move_file = os.path.join(char_path, "MOVE-Sheet.png")
            if os.path.exists(idle_file) and os.path.exists(move_file):
                config = {
                    'idle': {'filename': 'IDLE-Sheet.png', 'frame_count': 12, 'speed': 100},
                    'move': {'filename': 'MOVE-Sheet.png', 'frame_count': 5, 'speed': 200},
                }
                characters[char_name] = Character(char_name, config)
    return characters
