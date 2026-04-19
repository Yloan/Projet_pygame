import pygame as pyg

from utils.paths import get_asset_path

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

        sprite_path_IDLE = get_asset_path("sprites", "Character-1", "FIRE-IDLE-Sheet.png")
        sprite_path_WALK = get_asset_path("sprites", "Character-1", "FIRE-WALK-Sheet.png")

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
        self.sprite_IDLE = get_asset_path("sprites", "Character-2", "IDLE-Sheet.png")
        self.sprite_MOVE = get_asset_path("sprites", "Character-2", "MOVE-Sheet.png")
        self.sprite_HURT = get_asset_path("sprites", "Character-2", "HURT-Sheet.png")
        self.sprite_DEATH = get_asset_path("sprites", "Character-2", "DEAD-Sheet.png")

        self.sprite_character_skill1 = get_asset_path(
            "sprites", "Character-2", "S1-Sheet.png"
        )
        self.sprite_skill1 = get_asset_path(
            "sprites", "Character-2", "effect-Bash-Sheet.png"
        )

        self.sprite_character_skill2 = get_asset_path(
            "sprites", "Character-2", "S2-Sheet.png"
        )
        self.sprite_skill2 = get_asset_path(
            "sprites", "Character-2", "effect-Bash-Sheet.png"
        )

        self.sprite_character_skill3 = get_asset_path(
            "sprites", "Character-2", "S3-1-Sheet.png"
        )
        self.sprite_skill3 = get_asset_path(
            "sprites", "Character-2", "effect-Bash-Sheet.png"
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
    """
    Generic character class for all 9 characters.
    Each Character-N folder must contain IDLE-Sheet.png and MOVE-Sheet.png.
    Optional sprites (loaded if present):
      HURT-Sheet.png, DEAD-Sheet.png
      S1-Sheet.png, S2-Sheet.png, S3-Sheet.png  (fallback: S3-1-Sheet.png)
      effect-S1-Sheet.png, effect-S2-Sheet.png, effect-S3-Sheet.png
    Frame counts are auto-detected from spritesheet width.
    Hitbox is inset by HITBOX_INSET pixels on each side (28x28 inside a 40x40 sprite).
    """

    FRAME_SIZE = 40
    HITBOX_INSET = 6

    # Milliseconds per frame for each animation state
    ANIM_SPEED = {
        'idle':    100,
        'move':    200,
        'hurt':    120,
        'dead':    150,
        'skill1':  100,
        'skill2':  100,
        'skill3':  100,
        'effect1':  80,
        'effect2':  80,
        'effect3':  80,
    }

    # Standard filenames — same across all Character-N folders
    SPRITE_FILES = {
        'idle':    'IDLE-Sheet.png',
        'move':    'MOVE-Sheet.png',
        'hurt':    'HURT-Sheet.png',
        'dead':    'DEAD-Sheet.png',
        'skill1':  'S1-Sheet.png',
        'skill2':  'S2-Sheet.png',
        'skill3':  'S3-Sheet.png',
        'effect1': 'effect-S1-Sheet.png',
        'effect2': 'effect-S2-Sheet.png',
        'effect3': 'effect-S3-Sheet.png',
    }

    # Fallback filenames tried when primary name is missing
    SPRITE_FILES_FALLBACK = {
        'skill3': 'S3-1-Sheet.png',
    }

    def __init__(self, char_number, position=(400, 400), health=100, speed=2):
        self.char_number = char_number
        self.char_folder = f"Character-{char_number}"
        self.health = health
        self.max_health = health
        self.speed = speed
        self.position = list(position)
        self.direction = "right"

        self.is_moving = False
        self.is_hurt = False
        self.is_dead = False
        self.is_attacking = {1: False, 2: False, 3: False}

        # frames[key] = {'right': [Surface, ...], 'left': [Surface, ...]}
        self.frames = {}
        self.timers  = {k: 0 for k in self.ANIM_SPEED}
        self.indices = {k: 0 for k in self.ANIM_SPEED}

        self._load_sprites()

    # ------------------------------------------------------------------
    # SPRITE LOADING
    # ------------------------------------------------------------------

    def _load_sheet(self, key, filename):
        try:
            path = get_asset_path("sprites", self.char_folder, filename)
            sheet = pyg.image.load(path)
            frame_count = sheet.get_width() // self.FRAME_SIZE
            right_frames, left_frames = [], []
            for i in range(frame_count):
                frame = sheet.subsurface(
                    (i * self.FRAME_SIZE, 0, self.FRAME_SIZE, self.FRAME_SIZE)
                )
                right_frames.append(frame)
                left_frames.append(pyg.transform.flip(frame, True, False))
            self.frames[key] = {'right': right_frames, 'left': left_frames}
            return True
        except Exception:
            return False

    def _load_sprites(self):
        for key, filename in self.SPRITE_FILES.items():
            if not self._load_sheet(key, filename):
                fallback = self.SPRITE_FILES_FALLBACK.get(key)
                if fallback:
                    self._load_sheet(key, fallback)

        if 'idle' not in self.frames:
            raise FileNotFoundError(
                f"Required IDLE-Sheet.png not found for {self.char_folder}"
            )
        if 'move' not in self.frames:
            self.frames['move'] = self.frames['idle']

    # ------------------------------------------------------------------
    # HITBOX
    # ------------------------------------------------------------------

    def get_hitbox(self):
        """Returns a pygame.Rect slightly smaller than the sprite."""
        x, y = int(self.position[0]), int(self.position[1])
        inset = self.HITBOX_INSET
        size = self.FRAME_SIZE - 2 * inset
        return pyg.Rect(x + inset, y + inset, size, size)

    # ------------------------------------------------------------------
    # MOVEMENT & STATS
    # ------------------------------------------------------------------

    def move(self, direction):
        if direction == "up":
            self.position[1] -= self.speed
        elif direction == "down":
            self.position[1] += self.speed
        elif direction == "left":
            self.position[0] -= self.speed
            self.direction = "left"
        elif direction == "right":
            self.position[0] += self.speed
            self.direction = "right"

    def take_damage(self, amount):
        if self.is_dead:
            return
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.is_dead = True
            self.indices['dead'] = 0
            self.timers['dead'] = 0
        else:
            self.is_hurt = True
            self.indices['hurt'] = 0
            self.timers['hurt'] = 0

    def heal(self, amount):
        if not self.is_dead:
            self.health = min(self.health + amount, self.max_health)

    def get_status(self):
        return {"health": self.health, "position": tuple(self.position)}

    # ------------------------------------------------------------------
    # ANIMATION HELPERS
    # ------------------------------------------------------------------

    def _advance(self, key, delta_time, loop=True):
        """
        Advance animation timer and index.
        Returns True when a non-looping animation has reached its last frame.
        """
        frames = self.frames.get(key, {}).get('right', [])
        if not frames:
            return True
        # Stay frozen on last frame for non-looping animations that finished
        if not loop and self.indices.get(key, 0) >= len(frames) - 1:
            return True
        self.timers[key] += delta_time
        if self.timers[key] < self.ANIM_SPEED[key]:
            return False
        self.timers[key] = 0
        self.indices[key] += 1
        if self.indices[key] >= len(frames):
            if loop:
                self.indices[key] = 0
            else:
                self.indices[key] = len(frames) - 1
                return True
        return False

    def _get_frame(self, key):
        """Current frame Surface for *key* in the current facing direction."""
        frames = self.frames.get(key, {}).get(self.direction, [])
        if not frames:
            return None
        return frames[min(self.indices.get(key, 0), len(frames) - 1)]

    # ------------------------------------------------------------------
    # ANIMATION UPDATE  (same signature as Water.update_animation)
    # ------------------------------------------------------------------

    def update_animation(
        self,
        delta_time,
        is_moving,
        is_attacking_skill1=False,
        is_attacking_skill2=False,
        is_attacking_skill3=False,
    ):
        self.is_moving = is_moving

        if self.is_dead:
            if 'dead' in self.frames:
                self._advance('dead', delta_time, loop=False)
            return

        skill_inputs = (is_attacking_skill1, is_attacking_skill2, is_attacking_skill3)

        # Mirror Water's behaviour: set attack flag each frame from input,
        # then advance the animation and clear the flag when it finishes.
        for n, pressed in enumerate(skill_inputs, 1):
            key     = f'skill{n}'
            eff_key = f'effect{n}'
            self.is_attacking[n] = pressed and key in self.frames

            if self.is_attacking[n]:
                done = self._advance(key, delta_time, loop=False)
                if done:
                    self.indices[key] = 0
                    if eff_key in self.frames:
                        self.indices[eff_key] = 0
                    self.is_attacking[n] = False
                elif eff_key in self.frames:
                    self._advance(eff_key, delta_time, loop=True)

        # Hurt plays once then clears
        if self.is_hurt:
            if 'hurt' in self.frames:
                if self._advance('hurt', delta_time, loop=False):
                    self.is_hurt = False
            else:
                self.is_hurt = False

        # Base locomotion
        if is_moving:
            self._advance('move', delta_time, loop=True)
        else:
            self._advance('idle', delta_time, loop=True)

    # ------------------------------------------------------------------
    # SPRITE GETTERS
    # ------------------------------------------------------------------

    def get_current_sprite(self):
        """Returns the character sprite for the current animation state."""
        if self.is_dead:
            return self._get_frame('dead') or self._get_frame('idle')

        for n in (1, 2, 3):
            if self.is_attacking[n]:
                frame = self._get_frame(f'skill{n}')
                if frame:
                    return frame

        if self.is_hurt:
            frame = self._get_frame('hurt')
            if frame:
                return frame

        if self.is_moving:
            return self._get_frame('move') or self._get_frame('idle')
        return self._get_frame('idle')

    def get_effect_sprite(self):
        """Returns the effect/projectile sprite for the active skill, or None."""
        for n in (1, 2, 3):
            if self.is_attacking[n]:
                frame = self._get_frame(f'effect{n}')
                if frame:
                    return frame
        return None

    # ------------------------------------------------------------------
    # SKILL TRIGGERS (can also be called directly instead of via flags)
    # ------------------------------------------------------------------

    def skill1(self):
        if not self.is_attacking[1] and 'skill1' in self.frames:
            self.is_attacking[1] = True
            self.indices['skill1'] = 0
            self.timers['skill1'] = 0

    def skill2(self):
        if not self.is_attacking[2] and 'skill2' in self.frames:
            self.is_attacking[2] = True
            self.indices['skill2'] = 0
            self.timers['skill2'] = 0

    def skill3(self):
        if not self.is_attacking[3] and 'skill3' in self.frames:
            self.is_attacking[3] = True
            self.indices['skill3'] = 0
            self.timers['skill3'] = 0

    def update(self):
        pass


def load_all_characters():
    """Load every Character-N folder that contains at least IDLE-Sheet.png."""
    characters = {}
    for i in range(1, 10):
        try:
            characters[f"Character-{i}"] = Character(i)
        except FileNotFoundError:
            pass
    return characters
