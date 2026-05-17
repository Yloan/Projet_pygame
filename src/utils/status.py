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


And the super() is in order to avoid retaping the same code as a another class, you can just get it, but I think you guys knew it
"""

WET_DURATION = 5000
DISABLED_DURATION = 5000
PUSH_DURATION = 300
PUSH_SPEED = 4
BUBBLE_DRIFT = 0.5


class StatusEffect:
    def __init__(self, duration):
        self.duration = duration
        self.timer = 0
        self.is_active = True

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.duration:
            self.is_active = False


class WetStatus(StatusEffect):
    def __init__(self):
        super().__init__(WET_DURATION)


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

    def get_delta(self, dt):
        if not self.is_active:
            return 0
        ratio = max(0.0, 1.0 - self.timer / self.duration)
        delta = int(PUSH_SPEED * ratio * (dt / 16))
        return delta if self.direction == "right" else -delta


class StatusManager:
    def __init__(self):
        self.effects = {}

    def apply_wet(self):
        self.effects["wet"] = WetStatus()

    def apply_disabled(self, direction):
        self.effects["disabled"] = DisabledStatus(direction)

    def apply_pushed(self, direction):
        self.effects["pushed"] = PushedStatus(direction)

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
    def bubble_offset(self):
        d = self.effects.get("disabled")
        return d.bubble_offset if d and d.is_active else 0.0

    def get_push_delta(self, dt):
        p = self.effects.get("pushed")
        return p.get_delta(dt) if p else 0

    def clear(self):
        self.effects = {}
