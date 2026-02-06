"""
CHARACTER MODULE - Defines all playable characters and their behavior

This module contains character classes for the game, each with:
- Stats management (health, speed, position)
- Animation system (idle, walk, hurt, death states)
- Movement and combat mechanics
- Skill system for special abilities

Recommendations:
1. Consider creating a base Character class to reduce code duplication
2. Add constants for animation frames and speeds at module level
3. Implement a state machine for better animation transitions
"""

import pygame as pyg

from utils.paths import get_asset_path


# ============================================================================
# CONSTANTS - Animation and sprite configuration
# ============================================================================
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
    """
    Furnace character class - A fire-type character with high speed.
    
    Attributes:
        health (int): Current health points (0-100)
        speed (int): Movement speed in pixels per frame
        position (tuple): Current (x, y) position on screen
        direction (str): Current facing direction ('left' or 'right')
        is_moving (bool): Whether the character is currently moving
        
    Animation States:
        - IDLE: Standing still animation (12 frames)
        - WALK: Moving animation (4 frames per direction)
    """
    
    def __init__(self):
        """Initialize Furnace character with default stats and load sprite assets."""
        
        # ====================================================================
        # CHARACTER STATS
        # ====================================================================
        self.health = 100
        self.speed = 2
        self.position = (400, 400)
        
        # ====================================================================
        # LOAD SPRITE ASSETS
        # ====================================================================
        sprite_path_IDLE = get_asset_path("sprites", "Furnace", "FIRE-IDLE-Sheet.png")
        sprite_path_WALK = get_asset_path("sprites", "Furnace", "FIRE-WALK-Sheet.png")

        self.player_spritesheet_IDLE = pyg.image.load(sprite_path_IDLE)
        self.player_spritesheet_WALK = pyg.image.load(sprite_path_WALK)

        # ====================================================================
        # EXTRACT IDLE ANIMATION FRAMES
        # ====================================================================
        self.frames_IDLE = []
        for i in range(FURNACE_IDLE_FRAMES):
            frame = self.player_spritesheet_IDLE.subsurface(
                (i * FURNACE_FRAME_WIDTH, 0, FURNACE_FRAME_WIDTH, FURNACE_FRAME_HEIGHT)
            )
            self.frames_IDLE.append(frame)

        # ====================================================================
        # EXTRACT WALK ANIMATION FRAMES (RIGHT DIRECTION)
        # ====================================================================
        self.fram_WALK = []
        for i in range(FURNACE_WALK_FRAMES):
            frame = self.player_spritesheet_WALK.subsurface(
                (i * FURNACE_FRAME_WIDTH, 0, FURNACE_FRAME_WIDTH, FURNACE_FRAME_HEIGHT)
            )
            self.fram_WALK.append(frame)

        # ====================================================================
        # EXTRACT WALK ANIMATION FRAMES (LEFT DIRECTION - FLIPPED)
        # ====================================================================
        self.frame_WALK_left = []
        for i in range(FURNACE_WALK_FRAMES):
            frame = self.player_spritesheet_WALK.subsurface(
                (i * FURNACE_FRAME_WIDTH, 0, FURNACE_FRAME_WIDTH, FURNACE_FRAME_HEIGHT)
            )
            frame_flipped = pyg.transform.flip(frame, True, False)
            self.frame_WALK_left.append(frame_flipped)

        # ====================================================================
        # EXTRACT IDLE ANIMATION FRAMES (LEFT DIRECTION - FLIPPED)
        # ====================================================================
        self.frame_IDLE_left = []
        for i in range(FURNACE_IDLE_FRAMES):
            frame = self.player_spritesheet_IDLE.subsurface(
                (i * FURNACE_FRAME_WIDTH, 0, FURNACE_FRAME_WIDTH, FURNACE_FRAME_HEIGHT)
            )
            frame_flipped = pyg.transform.flip(frame, True, False)
            self.frame_IDLE_left.append(frame_flipped)

        # ====================================================================
        # ANIMATION STATE VARIABLES
        # ====================================================================
        self.frame_IDLE = 0  # Current idle animation frame index
        self.frame_WALK = 0  # Current walk animation frame index
        self.tem_an_IDLE = 0  # Elapsed time for idle animation
        self.tem_an_WALK = 0  # Elapsed time for walk animation
        self.direction = "right"  # Current direction (left or right)
        self.is_moving = False  # Movement state flag


    # ========================================================================
    # MOVEMENT METHODS
    # ========================================================================
    
    def move(self, direction):
        """
        Move the character in the specified direction.
        
        Args:
            direction (str): Movement direction ('up', 'down', 'left', 'right')
        """
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

    # ========================================================================
    # HEALTH MANAGEMENT METHODS
    # ========================================================================

    def take_damage(self, amount):
        """
        Reduce character health by the specified amount.
        Health cannot go below 0.
        
        Args:
            amount (int): Damage amount to inflict
        """
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def heal(self, amount):
        """
        Increase character health by the specified amount.
        Health cannot exceed 100.
        
        Args:
            amount (int): Healing amount
        """
        self.health += amount
        if self.health > 100:
            self.health = 100

    # ========================================================================
    # STATUS AND INFORMATION METHODS
    # ========================================================================

    def get_status(self):
        """
        Get current character status.
        
        Returns:
            dict: Dictionary containing health and position
        """
        return {"health": self.health, "position": self.position}

    # ========================================================================
    # ANIMATION METHODS
    # ========================================================================

    def update_animation(self, delta_time, is_moving):
        """
        Update animation state based on movement and elapsed time.
        Handles transitions between idle and walk animations.
        
        Args:
            delta_time (int): Time elapsed since last frame in milliseconds
            is_moving (bool): Whether the character is currently moving
        """
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
        """
        Get the current sprite to be drawn based on animation state and direction.
        
        Returns:
            pygame.Surface: Current animation frame
        """
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

    # ========================================================================
    # SKILL SYSTEM
    # ========================================================================

    def skill1(self):
        """First special skill - To be implemented."""
        pass

    def skill2(self):
        """Second special skill - To be implemented."""
        pass

    def skill3(self):
        """Third special skill - To be implemented."""
        pass

    # ========================================================================
    # GAME LOOP UPDATE
    # ========================================================================

    def update(self):
        """
        Update method called during game loop.
        Used for continuous movement handling and state updates.
        """
        # This method can be extended for continuous movement handling
        pass


class Water:
    """
    Water character class - A water-type character with defensive abilities.
    
    Attributes:
        health (int): Current health points (0-100)
        speed (int): Movement speed in pixels per frame
        position (tuple): Current (x, y) position on screen
        direction (str): Current facing direction ('left' or 'right')
        
    Animation States:
        - IDLE: Standing still animation (12 frames)
        - MOVE: Moving animation (5 frames per direction)
        - HURT: Taking damage animation (5 frames)
        - DEATH: Character death animation (1 frame)
    """
    
    def __init__(self):
        """Initialize Water character with default stats and load sprite assets."""
        
        # ====================================================================
        # CHARACTER STATS
        # ====================================================================
        self.health = 100
        self.speed = 2
        self.position = (400, 400)
        self.direction = "right"
        
        # ====================================================================
        # LOAD SPRITE ASSET PATHS
        # ====================================================================
        self.sprite_IDLE = get_asset_path("sprites", "Water", "2-IDLE-Sheet.png")
        self.sprite_MOVE = get_asset_path("sprites", "Water", "2-MOVE-Sheet.png")
        self.sprite_HURT = get_asset_path("sprites", "Water", "2-HURT-Sheet.png")
        self.sprite_DEATH = get_asset_path("sprites", "Water", "2-DEAD-Sheet.png")

        
        self.sprite_character_skill1 = get_asset_path("sprites", "Water", "2-S1-Sheet.png")
        self.sprite_skill1 = get_asset_path("sprites", "Water", "effect-2-Bash-Sheet.png")

        self.sprite_character_skill2 = get_asset_path("sprites", "Water", "2-S2-Sheet.png")
        self.sprite_skill2 = get_asset_path("sprites", "Water", "effect-2-Bash-Sheet.png")

        self.sprite_character_skill3 = get_asset_path("sprites", "Water", "2-S3-1-Sheet.png")
        self.sprite_skill3 = get_asset_path("sprites", "Water", "effect-2-Bash-Sheet.png")
        


        # ====================================================================
        # INITIALIZE ANIMATION FRAME LISTS
        # ====================================================================
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


        # ====================================================================
        # EXTRACT IDLE ANIMATION FRAMES
        # ====================================================================
        for i in range(WATER_IDLE_FRAMES):
            frame = pyg.image.load(self.sprite_IDLE).subsurface(
                (i * WATER_FRAME_SIZE, 0, WATER_FRAME_SIZE, WATER_FRAME_SIZE)
            )
            self.frames_IDLE.append(frame)
            frame_flipped = pyg.transform.flip(frame, True, False)
            self.frames_IDLE_left.append(frame_flipped)
        

        # ====================================================================
        # EXTRACT MOVE ANIMATION FRAMES (BOTH DIRECTIONS)
        # ====================================================================
        for i in range(WATER_MOVE_FRAMES):
            frame = pyg.image.load(self.sprite_MOVE).subsurface(
                (i * WATER_FRAME_SIZE, 0, WATER_FRAME_SIZE, WATER_FRAME_SIZE)
            )
            self.frames_MOVE_right.append(frame)
            # Create flipped version for left direction
            frame_flipped = pyg.transform.flip(frame, True, False)
            self.frames_MOVE_left.append(frame_flipped)
        
        # ====================================================================
        # EXTRACT HURT ANIMATION FRAMES
        # ====================================================================
        for i in range(WATER_HURT_FRAMES):
            frame = pyg.image.load(self.sprite_HURT).subsurface(
                (i * WATER_FRAME_SIZE, 0, WATER_FRAME_SIZE, WATER_FRAME_SIZE)
            )
            self.frames_HURT.append(frame)

        # ====================================================================
        # EXTRACT ATTACK ANIMATION FRAMES
        # ====================================================================

        for i in range(WATER_SKILL1_FRAMES):
            frame = pyg.image.load(self.sprite_character_skill1).subsurface(i*WATER_FRAME_SIZE, 0, WATER_FRAME_SIZE, WATER_FRAME_SIZE)
            self.frames_character_skill1.append(frame)

            frame_flipped = pyg.transform.flip(frame, True, False)
            self.frames_character_skill1_left.append(frame_flipped)

        for i in range(WATER_SKILL2_FRAMES):
            frame = pyg.image.load(self.sprite_character_skill2).subsurface(i*WATER_FRAME_SIZE, 0, WATER_FRAME_SIZE, WATER_FRAME_SIZE)
            self.frames_character_skill2.append(frame)

            frame_flipped = pyg.transform.flip(frame, True, False)
            self.frames_character_skill2_left.append(frame_flipped)


        for i in range(WATER_SKILL3_FRAMES):
            frame = pyg.image.load(self.sprite_character_skill3).subsurface(i*WATER_FRAME_SIZE, 0, WATER_FRAME_SIZE, WATER_FRAME_SIZE)
            self.frames_character_skill3.append(frame)

            frame_flipped = pyg.transform.flip(frame, True, False)
            self.frames_character_skill3_left.append(frame_flipped)


        # ====================================================================
        # EXTRACT ATTACK ANIMATIONS OF THE PROJECTILE
        # ====================================================================


        for i in range(WATER_SKILL1_FRAMES):
            frame = pyg.image.load(self.sprite_skill1).subsurface(i*WATER_FRAME_SIZE, 0, WATER_FRAME_SIZE, WATER_FRAME_SIZE)
            self.effect_character_skill1.append(frame)

            frame_flipped = pyg.transofrm.flip(frame, True, False)
            self.effect_character_skill1_left.append(frame_flipped)

        for i in range(WATER_SKILL2_FRAMES):
            frame = pyg.image.load(self.effect_character_skill2).subsurface(i*WATER_FRAME_SIZE, 0, WATER_FRAME_SIZE, WATER_FRAME_SIZE)
            self.effect_character_skill2.append(frame)

            frame_flipped = pyg.transform.flip(frame, True, False)
            self.effect_character_skill2_left.append(frame_flipped)

        for i in range(WATER_SKILL3_FRAMES):
            frame = pyg.image.load(self.effect_character_skill3_1).subsurface(i*WATER_FRAME_SIZE, 0, WATER_FRAME_SIZE, WATER_FRAME_SIZE)
            self.effect_character_skill3_1.append(frame)

            frame_flipped = pyg.transform.flip(frame, True, False)
            self.effect_character_skill3_1_left.append(frame_flipped)


        

        
        # ====================================================================
        # ANIMATION STATE VARIABLES
        # ====================================================================
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



    # ========================================================================
    # MOVEMENT METHODS
    # ========================================================================

    def move(self, direction):
        """
        Move the character in the specified direction.
        
        Args:
            direction (str): Movement direction ('up', 'down', 'left', 'right')
        """
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

    # ========================================================================
    # STATUS AND INFORMATION METHODS
    # ========================================================================

    def get_status(self):
        """
        Get current character status.
        
        Returns:
            dict: Dictionary containing health and position
        """
        return {"health": self.health, "position": self.position}
    
    # ========================================================================
    # HEALTH AND COMBAT METHODS
    # ========================================================================

    def take_damage(self, amount):
        """
        Reduce character health by the specified amount.
        Triggers death sequence if health reaches 0.
        
        Args:
            amount (int): Damage amount to inflict
        """
        self.health -= amount
        if self.health < 0:
            self.health = 0
            self.death()

    def death(self):
        """
        Handle character death sequence.
        
        Returns:
            pygame.Surface: Death sprite frame
        """
        return pyg.image.load(self.sprite_DEATH)
    
    def heal(self, amount):
        """
        Increase character health by the specified amount.
        Health cannot exceed 100.
        
        Args:
            amount (int): Healing amount
        """
        self.health += amount
        if self.health > 100:
            self.health = 100

    # ========================================================================
    # ANIMATION METHODS
    # ========================================================================

    def update_animation(self, delta_time, is_moving, is_attacking_skill1, is_attacking_skill2, is_attacking_skill3):
        """
        Update animation state based on elapsed time.
        Handles idle and move animations.
        
        Args:
            delta_time (int): Time elapsed since last frame in milliseconds
            is_moving (bool): Whether the character is currently moving
        """

        self.is_attacking_skill1 = is_attacking_skill1
        self.is_attacking_skill2 = is_attacking_skill2
        self.is_attacking_skill3 = is_attacking_skill3
        self.is_moving = is_moving

        #SKILL 1
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
        """
        Get the current sprite to be drawn based on animation state and direction.
        
        Returns:
            pygame.Surface: Current animation frame
        """

        if self.is_attacking_skill1:
            if self.direction == 'left':
                return self.frames_character_skill1_left[self.frame_character_skill1]
            else:
                return self.frames_character_skill1[self.frame_character_skill1]
        
        if self.is_attacking_skill2:
            if self.direction == 'left':
                return self.frames_character_skill2_left[self.frame_character_skill2]
            else:
                return self.frames_character_skill2[self.frame_character_skill2]
        
        if self.is_attacking_skill3:
            if self.direction == 'left':
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
            

    
    # ========================================================================
    # SKILL SYSTEM
    # ========================================================================

    def skill1(self, delta_time, is_attacking_skill1):
        """First special skill - To be implemented."""

        pass



    def skill2(self):
        """Second special skill - To be implemented."""
        pass

    def skill3(self):
        """Third special skill - To be implemented."""
        pass
    
    # ========================================================================
    # GAME LOOP UPDATE
    # ========================================================================

    def update(self):
        """
        Update method called during game loop.
        Used for continuous state updates and animations.
        """
        pass
