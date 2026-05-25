"""
For the team:
    daivd and quentin, if you read this a property is for create of get type.
    This will allow us to not have to put "()" every time we want to call a method


class CompteBancaire:
    @property
    def numero(self):
        return "83947382738"

compte = CompteBancaire()
# On peut accéder à la valeur retournée par la méthode numero sans utiliser les parenthèses
print(compte.numero)

This site is very well explain if you guys want to understand it deeply: https://www.docstring.fr/glossaire/propriete/


And the super() is in order to avoid retaping the same code as a another class, you can just get it, but I think you guys already knew it
"""

WET_DURATION = 5000
DISABLED_DURATION = 5000
PUSH_DURATION = 500
PUSH_SPEED = 5
BUBBLE_DRIFT = 0.5
OILED_DURATION = 5000
GRAB_MAX_SPD = 18
GRAB_GRWTH = 1.09
BURN_DURATION = 5000
BURN_TICK_INTERVAL = 1000
BURN_TICK_DAMAGE = 1
WEAKENED_DURATION = 5000


class StatusEffect:
    def __init__(self, duration):
        self.duration = duration
        self.timer = 0
        self.is_active = True

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.duration:
            self.is_active = False


WET_SLIDE_FACTOR = 0.6  # fraction of speed kept as slide drift

class WetStatus(StatusEffect):
    def __init__(self):
        super().__init__(WET_DURATION)
        self.drft_x = 0.0
        self.drft_y = 0.0
        self._acc_x = 0.0
        self._acc_y = 0.0

    def set_drift(self, nx, ny, spd):
        self.drft_x = nx * spd * WET_SLIDE_FACTOR
        self.drft_y = ny * spd * WET_SLIDE_FACTOR

    def get_drift(self, dt):
        if not self.is_active:
            return 0, 0
        decay = 0.97 ** (dt / 16.0)
        self.drft_x *= decay
        self.drft_y *= decay
        self._acc_x += self.drft_x
        self._acc_y += self.drft_y
        px = int(self._acc_x)
        py = int(self._acc_y)
        self._acc_x -= px
        self._acc_y -= py
        return px, py


class DisabledStatus(StatusEffect):
    def __init__(self, direction):
        super().__init__(DISABLED_DURATION)
        self.direction = direction
        self.bubble_offset = 0.0

    def update(self, dt):
        super().update(dt)
        if self.is_active:
            drift = BUBBLE_DRIFT * dt
            self.bubble_offset += drift if self.direction == "right" else -drift


class PushedStatus(StatusEffect):
    def __init__(self, direction):
        super().__init__(PUSH_DURATION)
        self.direction = direction
        self._accum = 0.0

    def get_delta(self, dt):
        if not self.is_active:
            return 0
        ratio = max(0.0, 1.0 - self.timer / self.duration)
        self._accum += PUSH_SPEED * ratio * (dt / 16.0)
        px = int(self._accum)
        self._accum -= px
        return px if self.direction == "right" else -px


class StunStatus(StatusEffect):
    def __init__(self, duration):
        super().__init__(duration)


class OiledStatus(StatusEffect):
    def __init__(self):
        super().__init__(OILED_DURATION)
        self.drft_x = 0.0
        self.drft_y = 0.0
        self._acc_x = 0.0
        self._acc_y = 0.0

    def set_drift(self, nx, ny, spd):
        self.drft_x = nx * spd * 0.4
        self.drft_y = ny * spd * 0.4

    def get_drift(self, dt):
        if not self.is_active:
            return 0, 0
        decay = 0.95 ** (dt / 16.0)
        self.drft_x *= decay
        self.drft_y *= decay
        self._acc_x += self.drft_x
        self._acc_y += self.drft_y
        px = int(self._acc_x)
        py = int(self._acc_y)
        self._acc_x -= px
        self._acc_y -= py
        return px, py


class BurnStatus(StatusEffect):
    def __init__(self):
        super().__init__(BURN_DURATION)
        self.tick_timer = 0
        self.pending_damage = 0

    def update(self, dt):
        super().update(dt)
        if self.is_active:
            self.tick_timer += dt
            while self.tick_timer >= BURN_TICK_INTERVAL:
                self.tick_timer -= BURN_TICK_INTERVAL
                self.pending_damage += BURN_TICK_DAMAGE

    def consume_damage(self):
        dmg = self.pending_damage
        self.pending_damage = 0
        return dmg


class WeakenedStatus(StatusEffect):
    def __init__(self):
        super().__init__(WEAKENED_DURATION)


class GrabStatus(StatusEffect):
    def __init__(self, src_char):
        super().__init__(5000)
        self.src = src_char
        self.cur_spd = 1.5

    def get_pull_delta(self, tgt_pos, dt):
        if not self.is_active:
            return 0.0, 0.0
        self.cur_spd = min(GRAB_MAX_SPD, self.cur_spd * (GRAB_GRWTH ** (dt / 16.0)))
        tx, ty = self.src.position
        cx, cy = tgt_pos
        dx = tx - cx
        dy = ty - cy
        dist = (dx * dx + dy * dy) ** 0.5
        if dist < 3:
            return 0.0, 0.0
        return (dx / dist) * self.cur_spd, (dy / dist) * self.cur_spd


class StatusManager:
    def __init__(self):
        self.effects = {}

    def apply_wet(self):
        self.effects["wet"] = WetStatus()

    def apply_disabled(self, direction):
        self.effects["disabled"] = DisabledStatus(direction)

    def apply_pushed(self, direction):
        self.effects["pushed"] = PushedStatus(direction)

    def apply_stun(self, duration):
        self.effects["stun"] = StunStatus(duration)

    def apply_oiled(self):
        self.effects["oiled"] = OiledStatus()

    def apply_grabbed(self, src_char):
        self.effects["grabbed"] = GrabStatus(src_char)

    def apply_burn(self):
        existing = self.effects.get("burn")
        if existing and existing.is_active:
            existing.timer = 0
        else:
            self.effects["burn"] = BurnStatus()

    def apply_weakened(self):
        self.effects["weakened"] = WeakenedStatus()

    def update(self, dt):
        for key, effect in list(self.effects.items()):
            effect.update(dt)
            if not effect.is_active:
                del self.effects[key]

    @property
    def is_wet(self):
        e = self.effects.get("wet")
        return e is not None and e.is_active

    @property
    def is_disabled(self):
        e = self.effects.get("disabled")
        return e is not None and e.is_active

    @property
    def is_pushed(self):
        e = self.effects.get("pushed")
        return e is not None and e.is_active

    @property
    def is_stunned(self):
        e = self.effects.get("stun")
        return e is not None and e.is_active

    @property
    def is_oiled(self):
        e = self.effects.get("oiled")
        return e is not None and e.is_active

    @property
    def is_grabbed(self):
        e = self.effects.get("grabbed")
        return e is not None and e.is_active

    @property
    def is_burning(self):
        e = self.effects.get("burn")
        return e is not None and e.is_active

    @property
    def is_weakened(self):
        e = self.effects.get("weakened")
        return e is not None and e.is_active

    def get_burn_damage(self):
        b = self.effects.get("burn")
        return b.consume_damage() if b and b.is_active else 0

    @property
    def bubble_offset(self):
        d = self.effects.get("disabled")
        return d.bubble_offset if d and d.is_active else 0.0

    def get_push_delta(self, dt):
        p = self.effects.get("pushed")
        return p.get_delta(dt) if p else 0

    def get_grab_delta(self, tgt_pos, dt):
        g = self.effects.get("grabbed")
        return g.get_pull_delta(tgt_pos, dt) if g else (0.0, 0.0)

    def clear(self):
        self.effects = {}
