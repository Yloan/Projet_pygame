import pygame as pyg

from utils.paths import get_asset_path

# =============================================================================
# CONSTANTS
# =============================================================================

FRAME_SIZE = 40          # All character sprites use 40×40 px frames

# Animation playback speeds (milliseconds per frame)
ANIM_SPEED_IDLE  = 100
ANIM_SPEED_MOVE  = 150
ANIM_SPEED_HURT  = 80
ANIM_SPEED_SKILL = 100

# Per-character base stats and placeholder rectangle color.
# Add / update entries as more characters are implemented by the art team.
CHAR_STATS = {
    1: {"speed": 3, "health": 100, "color": (220,  80,  20)},  # Fire
    2: {"speed": 2, "health": 100, "color": ( 20, 120, 220)},  # Water
    3: {"speed": 2, "health": 100, "color": (200, 200,  50)},
    4: {"speed": 4, "health":  80, "color": (255, 230,   0)},  # Electric
    5: {"speed": 2, "health": 100, "color": (100, 200, 100)},
    6: {"speed": 2, "health": 100, "color": (200, 130,  50)},  # Food
    7: {"speed": 2, "health": 100, "color": (150, 150, 150)},
    8: {"speed": 3, "health":  80, "color": (180, 100, 255)},  # Ghost
    9: {"speed": 2, "health": 100, "color": (100, 200,  50)},
}
_DEFAULT_STATS = {"speed": 2, "health": 100, "color": (128, 128, 128)}


class Character:
    """
    Unified character class for all 9 playable characters in Blitzkrieg.

    Sprites are loaded from  assets/sprites/Character-<num>/  following the
    naming convention defined by Aegon:

        IDLE-Sheet.png    MOVE-Sheet.png    HURT-Sheet.png    DEAD-Sheet.png
        S1-Sheet.png      S2-Sheet.png      S3-1-Sheet.png

    Every file is optional. If a sheet is missing the animation falls back to:
        - the IDLE frames  (for MOVE, HURT, S1, S2, S3)
        - a solid-color 40×40 rectangle  (for IDLE itself and DEAD)

    This means the game always runs, even for characters whose art is not
    yet available (they will display a colored rectangle).

    Args:
        char_num (int): Character identifier 1–9.
    """

    def __init__(self, char_num: int):
        stats = CHAR_STATS.get(char_num, _DEFAULT_STATS)

        # ── Core attributes ────────────────────────────────────────────────
        self.char_num   = char_num
        self.health     = stats["health"]
        self.max_health = stats["health"]
        self.speed      = stats["speed"]
        self._ph_color  = stats["color"]    # placeholder rectangle color

        # ── Spatial state ──────────────────────────────────────────────────
        self.position  = (400, 400)
        self.direction = "right"            # "left" | "right"

        # ── Sprite loading ─────────────────────────────────────────────────
        self._load_animations()

        # ── Animation frame counters ───────────────────────────────────────
        self.frame_IDLE = 0
        self.frame_MOVE = 0
        self.frame_HURT = 0
        self.frame_S1   = 0
        self.frame_S2   = 0
        self.frame_S3   = 0

        # ── Animation accumulators (ms) ────────────────────────────────────
        self.tem_IDLE = 0
        self.tem_MOVE = 0
        self.tem_HURT = 0
        self.tem_S1   = 0
        self.tem_S2   = 0
        self.tem_S3   = 0

        # ── State flags ────────────────────────────────────────────────────
        self.is_moving       = False
        self.is_attacking_s1 = False
        self.is_attacking_s2 = False
        self.is_attacking_s3 = False
        self.is_hurt         = False
        self.is_dead         = False

    # =========================================================================
    # Private helpers
    # =========================================================================

    def _placeholder(self, color: tuple = None) -> list:
        """Return a single-element list with a solid-color 40×40 surface."""
        surf = pyg.Surface((FRAME_SIZE, FRAME_SIZE))
        surf.fill(color if color is not None else self._ph_color)
        return [surf]

    def _load_sheet(self, filename: str):
        """
        Try to load a sprite sheet and split it into 40-px frames.

        Returns:
            list[pygame.Surface] if the file exists, None otherwise.
        """
        try:
            path = get_asset_path("sprites", f"Character-{self.char_num}", filename)
            sheet = pyg.image.load(path).convert_alpha()
            count = max(1, sheet.get_width() // FRAME_SIZE)
            return [
                sheet.subsurface((i * FRAME_SIZE, 0, FRAME_SIZE, FRAME_SIZE))
                for i in range(count)
            ]
        except Exception:
            return None

    @staticmethod
    def _flip(frames: list) -> list:
        """Return horizontally mirrored copies of a frames list."""
        return [pyg.transform.flip(f, True, False) for f in frames]

    def _load_animations(self):
        """
        Load all animation sheets. Substitute a placeholder for each missing
        file so every character is always renderable.
        """
        # IDLE is the primary fallback — check availability once.
        _idle_raw     = self._load_sheet("IDLE-Sheet.png")
        self.has_sprites = _idle_raw is not None   # True only when real art exists

        idle = _idle_raw                            or self._placeholder()
        move = self._load_sheet("MOVE-Sheet.png")  or idle
        hurt = self._load_sheet("HURT-Sheet.png")  or idle
        dead = self._load_sheet("DEAD-Sheet.png")  or self._placeholder((80, 0, 0))
        s1   = self._load_sheet("S1-Sheet.png")    or idle
        s2   = self._load_sheet("S2-Sheet.png")    or idle
        s3   = self._load_sheet("S3-1-Sheet.png")  or idle

        # Right-facing originals
        self.frames_IDLE = idle
        self.frames_MOVE = move
        self.frames_HURT = hurt
        self.frames_DEAD = dead
        self.frames_S1   = s1
        self.frames_S2   = s2
        self.frames_S3   = s3

        # Left-facing mirrors (horizontally flipped)
        self.frames_IDLE_left = self._flip(idle)
        self.frames_MOVE_left = self._flip(move)
        self.frames_HURT_left = self._flip(hurt)
        self.frames_S1_left   = self._flip(s1)
        self.frames_S2_left   = self._flip(s2)
        self.frames_S3_left   = self._flip(s3)

    # =========================================================================
    # Movement
    # =========================================================================

    def move(self, direction: str):
        """Move one step in the given direction and update facing."""
        x, y = self.position
        if direction == "up":
            self.position = (x, y - self.speed)
        elif direction == "down":
            self.position = (x, y + self.speed)
        elif direction == "left":
            self.position = (x - self.speed, y)
            self.direction = "left"
        elif direction == "right":
            self.position = (x + self.speed, y)
            self.direction = "right"

    # =========================================================================
    # Health / combat
    # =========================================================================

    def take_damage(self, amount: int):
        """
        Inflict *amount* damage.
        Sets is_dead when health reaches 0; otherwise triggers hurt animation.
        """
        self.health = max(0, self.health - amount)
        if self.health == 0:
            self.is_dead = True
        else:
            self.is_hurt    = True
            self.frame_HURT = 0
            self.tem_HURT   = 0

    def heal(self, amount: int):
        """Restore *amount* health, capped at max_health."""
        self.health = min(self.max_health, self.health + amount)

    def get_status(self) -> dict:
        """Return a snapshot of this character's current state."""
        return {
            "char_num": self.char_num,
            "health":   self.health,
            "position": self.position,
        }

    # =========================================================================
    # Skills
    # =========================================================================

    def use_skill(self, skill_num: int) -> bool:
        """
        Trigger skill *skill_num* (1, 2 or 3) if it is not already active.

        Returns:
            True  – skill was triggered (caller should notify the server).
            False – skill already in progress, nothing happened.
        """
        if skill_num == 1 and not self.is_attacking_s1:
            self.is_attacking_s1 = True
            self.frame_S1 = 0
            self.tem_S1   = 0
            return True
        if skill_num == 2 and not self.is_attacking_s2:
            self.is_attacking_s2 = True
            self.frame_S2 = 0
            self.tem_S2   = 0
            return True
        if skill_num == 3 and not self.is_attacking_s3:
            self.is_attacking_s3 = True
            self.frame_S3 = 0
            self.tem_S3   = 0
            return True
        return False

    # =========================================================================
    # Animation update
    # =========================================================================

    def update_animation(self, delta_time: int, is_moving: bool):
        """
        Advance all active animation timers by *delta_time* milliseconds.
        Call once per game frame, before get_current_sprite().

        Args:
            delta_time: ms elapsed since the previous frame (clock.tick value).
            is_moving:  True when movement arrow keys are currently held.
        """
        self.is_moving = is_moving

        # ── Skill 1 (plays once then auto-clears) ─────────────────────────
        if self.is_attacking_s1:
            self.tem_S1 += delta_time
            if self.tem_S1 >= ANIM_SPEED_SKILL:
                self.tem_S1 = 0
                self.frame_S1 += 1
                if self.frame_S1 >= len(self.frames_S1):
                    self.frame_S1 = 0
                    self.is_attacking_s1 = False

        # ── Skill 2 ────────────────────────────────────────────────────────
        if self.is_attacking_s2:
            self.tem_S2 += delta_time
            if self.tem_S2 >= ANIM_SPEED_SKILL:
                self.tem_S2 = 0
                self.frame_S2 += 1
                if self.frame_S2 >= len(self.frames_S2):
                    self.frame_S2 = 0
                    self.is_attacking_s2 = False

        # ── Skill 3 ────────────────────────────────────────────────────────
        if self.is_attacking_s3:
            self.tem_S3 += delta_time
            if self.tem_S3 >= ANIM_SPEED_SKILL:
                self.tem_S3 = 0
                self.frame_S3 += 1
                if self.frame_S3 >= len(self.frames_S3):
                    self.frame_S3 = 0
                    self.is_attacking_s3 = False

        # ── Hurt (plays once then clears) ─────────────────────────────────
        if self.is_hurt:
            self.tem_HURT += delta_time
            if self.tem_HURT >= ANIM_SPEED_HURT:
                self.tem_HURT = 0
                self.frame_HURT += 1
                if self.frame_HURT >= len(self.frames_HURT):
                    self.frame_HURT = 0
                    self.is_hurt = False

        # ── Movement / Idle (looping) ──────────────────────────────────────
        if is_moving:
            self.tem_MOVE += delta_time
            if self.tem_MOVE >= ANIM_SPEED_MOVE:
                self.tem_MOVE = 0
                self.frame_MOVE = (self.frame_MOVE + 1) % len(self.frames_MOVE)
        else:
            self.tem_IDLE += delta_time
            if self.tem_IDLE >= ANIM_SPEED_IDLE:
                self.tem_IDLE = 0
                self.frame_IDLE = (self.frame_IDLE + 1) % len(self.frames_IDLE)

    # =========================================================================
    # Rendering
    # =========================================================================

    def get_current_sprite(self) -> "pyg.Surface":
        """
        Return the surface that should be blitted this frame.

        Priority (highest first):
            dead > hurt > skill3 > skill2 > skill1 > move > idle
        """
        left = self.direction == "left"

        if self.is_dead:
            return self.frames_DEAD[-1]         # hold last death frame

        if self.is_hurt:
            frames = self.frames_HURT_left if left else self.frames_HURT
            return frames[min(self.frame_HURT, len(frames) - 1)]

        if self.is_attacking_s1:
            frames = self.frames_S1_left if left else self.frames_S1
            return frames[min(self.frame_S1, len(frames) - 1)]

        if self.is_attacking_s2:
            frames = self.frames_S2_left if left else self.frames_S2
            return frames[min(self.frame_S2, len(frames) - 1)]

        if self.is_attacking_s3:
            frames = self.frames_S3_left if left else self.frames_S3
            return frames[min(self.frame_S3, len(frames) - 1)]

        if self.is_moving:
            frames = self.frames_MOVE_left if left else self.frames_MOVE
            return frames[self.frame_MOVE]

        frames = self.frames_IDLE_left if left else self.frames_IDLE
        return frames[self.frame_IDLE]

    # =========================================================================
    # Network helpers
    # =========================================================================

    def apply_network_state(self, state: dict):
        """
        Apply a state snapshot received from the server to synchronise a
        remote player's character.

        Args:
            state: dict produced by the [EntityState] / [GameState] message.
        """
        if "pos" in state:
            self.position = tuple(state["pos"])
        if "direction" in state:
            self.direction = state["direction"]
        if "health" in state:
            self.health = int(state["health"])
            self.is_dead = self.health <= 0
        if "is_moving" in state:
            self.is_moving = bool(state["is_moving"])
        if "is_hurt" in state:
            self.is_hurt = bool(state["is_hurt"])

        atk = state.get("is_attacking", {})
        self.is_attacking_s1 = bool(atk.get("1", False))
        self.is_attacking_s2 = bool(atk.get("2", False))
        self.is_attacking_s3 = bool(atk.get("3", False))

        idx = state.get("anim_indices", {})
        self.frame_IDLE = int(idx.get("idle",   self.frame_IDLE))
        self.frame_MOVE = int(idx.get("move",   self.frame_MOVE))
        self.frame_HURT = int(idx.get("hurt",   self.frame_HURT))
        self.frame_S1   = int(idx.get("skill1", self.frame_S1))
        self.frame_S2   = int(idx.get("skill2", self.frame_S2))
        self.frame_S3   = int(idx.get("skill3", self.frame_S3))

    def get_effect_sprite(self):
        """
        Return the current skill-effect sprite (projectile / VFX) if any.
        Stub — will be implemented when effect sheets are available.
        """
        return None

    # =========================================================================
    # Game-loop hook
    # =========================================================================

    def update(self):
        """Reserved for future per-frame logic (AI, physics, status ticks…)."""
        pass


# =============================================================================
# LEGACY ALIASES — kept so existing imports don't break
# =============================================================================

class Furnace(Character):
    """Fire character — thin alias for Character(1)."""
    def __init__(self):
        super().__init__(1)


class Water(Character):
    """Water character — thin alias for Character(2)."""
    def __init__(self):
        super().__init__(2)
