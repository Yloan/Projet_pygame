import pygame


DEFAULT_SCALE = 1
DEFAULT_ANIMATION_SPEED = 8  # frames per second for idle / hover loop


class AnimatedButton:
    """Button with 4 animation states.

    States
    ------
    STATIC    : mouse not over → shows first idle frame (frozen)
    HOVER     : mouse over     → loops through idle frames
    PRESSING  : mouse down     → plays pressed  frames once (holds last frame)
    RELEASING : mouse up       → plays unpressed frames once, then fires action
                                 (if no unpressed sheet, action fires on mouse-up)
    """

    _ST_STATIC    = 0
    _ST_HOVER     = 1
    _ST_PRESSING  = 2
    _ST_RELEASING = 3

    def __init__(self, x, y,
                 frames_idle,
                 frames_pressed=None,
                 frames_unpressed=None,
                 scale=DEFAULT_SCALE,
                 animation_speed=DEFAULT_ANIMATION_SPEED):

        def _scale(frames):
            if not frames:
                return []
            out = []
            for f in frames:
                w, h = f.get_width(), f.get_height()
                out.append(pygame.transform.scale(f, (int(w * scale), int(h * scale))))
            return out

        self.frames_idle      = _scale(frames_idle)
        self.frames_pressed   = _scale(frames_pressed)   if frames_pressed   else []
        self.frames_unpressed = _scale(frames_unpressed) if frames_unpressed else []

        self.scale           = scale
        self.animation_speed = max(1, animation_speed)

        self.rect = (
            self.frames_idle[0].get_rect(topleft=(x, y))
            if self.frames_idle
            else pygame.Rect(x, y, 0, 0)
        )

        self._state     = self._ST_STATIC
        self._frame     = 0
        self._accum     = 0.0          # ms accumulator for animation
        self._last_tick = pygame.time.get_ticks()
        self._mouse_was_down = False   # edge-detect for mouse press

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _current_image(self):
        if self._state == self._ST_PRESSING and self.frames_pressed:
            idx = min(self._frame, len(self.frames_pressed) - 1)
            return self.frames_pressed[idx]
        if self._state == self._ST_RELEASING and self.frames_unpressed:
            idx = min(self._frame, len(self.frames_unpressed) - 1)
            return self.frames_unpressed[idx]
        if self.frames_idle:
            return self.frames_idle[self._frame % len(self.frames_idle)]
        return None

    def _advance_frames(self, dt, n_frames, fps_multiplier=1.0):
        """Advance frame counter; returns True when the last frame is reached."""
        fps = self.animation_speed * fps_multiplier
        dur = 1000.0 / fps
        self._accum += dt
        while self._accum >= dur:
            self._accum -= dur
            if self._frame < n_frames - 1:
                self._frame += 1
            else:
                return True   # animation finished
        return False

    # ------------------------------------------------------------------ #
    #  Public draw — call once per frame                                   #
    # ------------------------------------------------------------------ #

    def draw(self, surface):
        """Draw the button and return True exactly once when a click fires."""
        if not self.frames_idle:
            return False

        now        = pygame.time.get_ticks()
        dt         = now - self._last_tick
        self._last_tick = now

        pos        = pygame.mouse.get_pos()
        hovered    = self.rect.collidepoint(pos)
        mouse_down = pygame.mouse.get_pressed()[0] == 1
        just_pressed  = mouse_down and not self._mouse_was_down
        just_released = (not mouse_down) and self._mouse_was_down
        self._mouse_was_down = mouse_down

        action = False

        # ── State transitions ─────────────────────────────────────────── #
        if self._state == self._ST_STATIC:
            if hovered:
                self._state = self._ST_HOVER
                self._frame = 0
                self._accum = 0.0

        elif self._state == self._ST_HOVER:
            if not hovered:
                self._state = self._ST_STATIC
                self._frame = 0
                self._accum = 0.0
            elif just_pressed:
                self._state = self._ST_PRESSING
                self._frame = 0
                self._accum = 0.0

        elif self._state == self._ST_PRESSING:
            if just_released:
                if self.frames_unpressed:
                    self._state = self._ST_RELEASING
                    self._frame = 0
                    self._accum = 0.0
                else:
                    # No release animation → fire action immediately
                    action = True
                    self._state = self._ST_HOVER if hovered else self._ST_STATIC
                    self._frame = 0
                    self._accum = 0.0

        elif self._state == self._ST_RELEASING:
            if just_pressed and hovered:
                # Player clicked again before animation finished
                self._state = self._ST_PRESSING
                self._frame = 0
                self._accum = 0.0

        # ── Animation tick ────────────────────────────────────────────── #
        if self._state == self._ST_HOVER:
            # Loop idle animation
            fps = self.animation_speed
            dur = 1000.0 / fps
            self._accum += dt
            while self._accum >= dur:
                self._accum -= dur
                self._frame = (self._frame + 1) % len(self.frames_idle)

        elif self._state == self._ST_PRESSING and self.frames_pressed:
            # Play pressed once, hold on last frame
            self._advance_frames(dt, len(self.frames_pressed), fps_multiplier=2.0)

        elif self._state == self._ST_RELEASING and self.frames_unpressed:
            # Play unpressed once, then fire
            finished = self._advance_frames(dt, len(self.frames_unpressed), fps_multiplier=2.0)
            if finished:
                action = True
                self._state = self._ST_HOVER if hovered else self._ST_STATIC
                self._frame = 0
                self._accum = 0.0

        # ── Draw ──────────────────────────────────────────────────────── #
        img = self._current_image()
        if img:
            surface.blit(img, self.rect.topleft)

        return action

    # Backward-compat stub
    def presse(self):
        pass
