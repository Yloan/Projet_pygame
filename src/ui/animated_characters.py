"""
ANIMATED CHARACTERS MODULE - Animated UI chracacters implementation

This module provides the AnimatedCharacter class for creating animated characters.
Animated characters automatically handle:
- Frame-by-frame animation from a list of surfaces
- Animation timing control
"""

import pygame

from utils.paths import get_asset_path


# ============================================================================
# CONSTANTS - Animation configuration
# ============================================================================
DEFAULT_SCALE = 1
DEFAULT_ANIMATION_SPEED = 100  # milliseconds between frames (default ~10 FPS)


class AnimatedCharacter:
    """Animated character helper.

    This class loads a sprite sheet (horizontal strip) and plays it as an animation.

    Example:
        # load the Water idle animation (12 frames) and draw it in the game loop
        anim = AnimatedCharacter.from_spritesheet(
            folder="sprites",
            subfolder="Water",
            filename="2-IDLE-Sheet.png",
            frame_width=40,
            frame_height=40,
            frame_count=12,
            animation_speed_ms=80,
            scale=3,
        )

        # in the game loop:
        delta = clock.tick(60)
        anim.update(delta)
        anim.draw(screen, (100, 100))
    """

    def __init__(
        self,
        frames,
        scale=DEFAULT_SCALE,
        animation_speed_ms=DEFAULT_ANIMATION_SPEED,
        loop=True,
    ):
        """Initialize animated character.

        Args:
            frames (list[pygame.Surface]): List of preloaded frames.
            scale (float): Scale factor applied to each frame.
            animation_speed_ms (int): Time in ms between frame changes.
            loop (bool): If True, animation loops. Otherwise it stays on last frame.
        """
        self.frames = [pygame.transform.scale(f, (int(f.get_width() * scale), int(f.get_height() * scale))) for f in frames]
        self.scale = scale
        self.animation_speed_ms = animation_speed_ms
        self.loop = loop

        self.current_frame = 0
        self._accumulator = 0

    # ------------------------------------------------------------------------
    # Factory helpers
    # ------------------------------------------------------------------------
    @classmethod
    def from_spritesheet(
        cls,
        folder: str,
        subfolder: str,
        filename: str,
        frame_width: int,
        frame_height: int,
        frame_count: int,
        scale: float = DEFAULT_SCALE,
        animation_speed_ms: int = DEFAULT_ANIMATION_SPEED,
        loop: bool = True,
    ):
        """Create an AnimatedCharacter from a horizontal spritesheet.

        Args:
            folder (str): Top-level asset folder (e.g. "sprites").
            subfolder (str): Subfolder inside the asset folder (e.g. "Water").
            filename (str): Filename of the sprite sheet.
            frame_width (int): Width of each frame in pixels.
            frame_height (int): Height of each frame in pixels.
            frame_count (int): Number of frames in the sprite sheet.
            scale (float): Scale factor applied to frames.
            animation_speed_ms (int): Milliseconds between frames.
            loop (bool): Whether to loop the animation.
        """
        sprite_path = get_asset_path(folder, subfolder, filename)
        sheet = pygame.image.load(sprite_path).convert_alpha()

        frames = []
        for i in range(frame_count):
            frame = sheet.subsurface(
                (i * frame_width, 0, frame_width, frame_height)
            )
            frames.append(frame)

        return cls(frames, scale=scale, animation_speed_ms=animation_speed_ms, loop=loop)

    # ------------------------------------------------------------------------
    # Runtime methods
    # ------------------------------------------------------------------------
    def update(self, delta_ms: int):
        """Advance animation based on elapsed time (ms)."""
        if not self.frames:
            return

        self._accumulator += delta_ms
        if self._accumulator >= self.animation_speed_ms:
            self._accumulator -= self.animation_speed_ms
            if self.current_frame >= len(self.frames) - 1:
                if self.loop:
                    self.current_frame = 0
            else:
                self.current_frame += 1

    def draw(self, surface, pos, flip_x=False, flip_y=False):
        """Draw the current frame at the given position.

        Args:
            surface (pygame.Surface): Target surface to draw on.
            pos (tuple[int,int]): (x, y) position.
            flip_x (bool): Mirror horizontally.
            flip_y (bool): Mirror vertically.
        """
        if not self.frames:
            return

        frame = self.frames[self.current_frame]
        if flip_x or flip_y:
            frame = pygame.transform.flip(frame, flip_x, flip_y)

        surface.blit(frame, pos)

    def reset(self):
        """Reset animation to the first frame."""
        self.current_frame = 0
        self._accumulator = 0
