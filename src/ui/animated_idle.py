import pygame

from utils.paths import get_asset_path


# ============================================================================
# CONSTANTS - Animation configuration
# ============================================================================
DEFAULT_SCALE = 1
DEFAULT_ANIMATION_SPEED = 100  # milliseconds between frames (default ~10 FPS)


class AnimatedCharacter:
    def __init__(
        self,
        frames,
        scale=DEFAULT_SCALE,
        animation_speed_ms=DEFAULT_ANIMATION_SPEED,
        loop=True,
    ):
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
        if not self.frames:
            return

        frame = self.frames[self.current_frame]
        if flip_x or flip_y:
            frame = pygame.transform.flip(frame, flip_x, flip_y)

        surface.blit(frame, pos)

    def reset(self):
        self.current_frame = 0
        self._accumulator = 0