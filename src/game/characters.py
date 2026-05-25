import pygame as pyg

import game.map_laoder as _map_mod  # use _map_mod.ACTIVE_COLLISIONS for per-map collisions
from ui.console import (
    print_debug,
    print_warning,
)
from utils.paths import get_asset_path
from utils.status import StatusManager

FRAME_SIZE = 40
CHARACTER_SCALE = 1.5
SCALED_FRAME_SIZE = int(FRAME_SIZE * CHARACTER_SCALE)  # logical cell size after scaling
IDLE_SPEED = 100
MOVE_SPEED = 150
HURT_SPEED = 180
SKILL_SPEED = 100
DISABLED_DURATION = 3000  # Durée de  disabled en ms

CHAR_STATS = {
    1: {"speed": 3, "health": 100, "color": (220, 80, 20)},
    2: {"speed": 2, "health": 100, "color": (20, 120, 220)},
    3: {"speed": 2, "health": 100, "color": (200, 200, 50)},
    4: {"speed": 4, "health": 80, "color": (255, 230, 0)},
    5: {"speed": 2, "health": 100, "color": (100, 200, 100)},
    6: {"speed": 2, "health": 100, "color": (200, 130, 50)},
    7: {"speed": 2, "health": 100, "color": (150, 150, 150)},
    8: {"speed": 3, "health": 80, "color": (180, 100, 255)},
    9: {"speed": 2, "health": 100, "color": (100, 200, 50)},
}
DEFAULT_STATS = {"speed": 2, "health": 100, "color": (128, 128, 128)}
COLLISION_THICKNESS = 10
TMP__GET_SURFACE_HITBOX_ATTACKS_ = False
DIMENS = {
    1: {"MOVE": (40, 40), "S1": (80, 60), "S2": (120, 50), "S3": (120, 60)},
    2: {
        "MOVE": (FRAME_SIZE, FRAME_SIZE),
        "S1": (168, 40),
        "S2": (112, 96),
        "S3": (200, 40),
        "S3_2": (176, 64),
    },
    3: {
        "MOVE": (60, 60),
        "S1": (64, 60),
        "S1_2": (120, 60),
        "S2": (80, 60),
        "S3": (120, 60),
    },
    4: {
        "MOVE": (64, 40),
        "S1": (75, 40),
        "S1_1": (75, 40),
        "S1_2": (75, 40),
        "S1_3": (75, 40),
        "S2": (160, 91),
        "S2_1": (160, 91),
        "S2_2": (160, 91),
        "S3": (176, 80),
    },
    5: {
        "S2": (122, 84),
    },
}

# Hitbox d'attaque par personnage et par skill
# "offset" : (x, y) par rapport a la position du perso (direction droite, c adapte quand c a gauche)
# "size" : (largeur, hauteur) de la hitbox
# "damage" : c assez evident
HITBOX_DATA = {
    1: {
        # S1 : feu — pixels attaque dans le frame à x=[46,79] y=[5,56]
        # frame dessiné à (body_x, body_y), frame 80×60
        1: {
            "offset": (42, 4),
            "size": (38, 47),
            "damage": 15,
            "frame_start": 2,
            "frame_end": 9,
            "status_applied": lambda atk, tgt: tgt.status.apply_burn(),
        },
        # S2 : sphère — n'apparaît qu'aux frames 4-6, x=[55,107] y=[4,41]
        # frame dessiné à (body_x, body_y), frame 120×50
        2: {
            "offset": (50, 3),
            "size": (58, 38),
            "damage": 25,
            "frame_start": 4,
            "frame_end": 6,
            "status_applied": lambda atk, tgt: tgt.status.apply_oiled(),
        },
        # S3 : lame de feu — attaque dès frame 1 jusqu'au 12, x=[46,105] y=[11,59]
        # frame dessiné à (body_x, body_y), frame 120×60
        3: {
            "offset": (44, 10),
            "size": (62, 38),
            "damage": 40,
            "frame_start": 1,
            "frame_end": 12,
            "status_applied": lambda atk, tgt: tgt.status.apply_burn(),
        },
    },
    2: {
        1: {
            "offset": (30, 20),
            "size": (150, 20),
            "damage": 12,
            "frame_start": 5,
            "frame_end": 99,
            "status_applied": lambda atk, tgt: tgt.status.apply_wet(),
        },
        2: {
            "offset": (40, 0),
            "size": (40, 40),
            "damage": 22,
            "frame_start": 5,
            "frame_end": 8,
            "status_applied": lambda atk, tgt: tgt.status.apply_pushed(atk.direction),
        },
        3: {
            "offset": (30, 20),
            "size": (150, 20),
            "damage": 35,
            "frame_start": 0,
            "frame_end": 99,
            "status_applied": lambda atk, tgt: (
                tgt.status.apply_wet(),
                tgt.status.apply_disabled(atk.direction),
            ),
        },
    },
    3: {
        1: {
            "offset": (70, 16),
            "size": (30, 20),
            "damage": 18,
            "frame_start": 0,
            "frame_end": 10,
        },
        2: {
            "offset": (30, 15),
            "size": (40, 40),
            "damage": 28,
            "frame_start": 7,
            "frame_end": 10,
            "status_applied": lambda atk, tgt: tgt.status.apply_pushed(atk.direction),
        },
        3: {
            "offset": (15, 3),
            "size": (90, 45),
            "damage": 1,
            "frame_start": 2,
            "frame_end": 10,
            "status_applied": lambda atk, tgt: tgt.status.apply_weakened(),
        },
    },
    4: {
        1: {
            "offset": (40, -5),
            "size": (42, 30),
            "damage": 10,
            "frame_start": 4,
            "frame_end": 99,
            "status_applied": lambda atk, tgt: tgt.status.apply_grabbed(atk),
        },
        2: {
            "offset": (-50, 0),
            "size": (160, 80),
            "damage": 30,
            "frame_start": 0,
            "frame_end": 99,
            "status_applied": lambda atk, tgt: tgt.status.apply_stun(2000),
        },
        3: {
            "offset": (50, 0),
            "size": (100, 50),
            "damage": 50,
            "frame_start": 0,
            "frame_end": 99,
        },
    },
    5: {
        1: {
            "offset": (0, 0),
            "size": (0, 0),
            "damage": 12,
            "frame_start": 0,
            "frame_end": 99,
        },
        2: {
            "offset": (-15, 30),
            "size": (85, 35),
            "damage": 24,
            "frame_start": 10,
            "frame_end": 14,
        },
        3: {
            "offset": (0, 0),
            "size": (0, 0),
            "damage": 0,
            "frame_start": 0,
            "frame_end": 99,
        },
    },
}
_DEFAULT_HITBOX = {"offset": (36, -8), "size": (40, 36), "damage": 10}

CHARACTER_RESISTANCES = {
    1: (1.0, 1.0, 1.0),
    2: (1.3, 1.0, 0.7),
    3: (1.5, 1.5, 1.5),
    4: (1.0, 1.0, 1.0),
    5: (0.6, 0.6, 0.6),
}
_DEFAULT_RESISTANCES = (1.0, 1.0, 1.0)


def _calc_damage(base_dmg, target, skill):
    res = CHARACTER_RESISTANCES.get(target.char_num, _DEFAULT_RESISTANCES)[skill - 1]
    if target.status.is_weakened:
        res = max(res, 1.5)
    return max(1, round(base_dmg * res))


# All the finfos ab the character's projectiles if there had some
PROJECTILES_INFOS = {
    5: {
        "s1": {
            "path": "assets/sprites/Character-5/PROJECTILE-1-1-Sheet.png",
            "frames": 4,
            "loops": 3,
            "stops": True,
            "speed": 5,
            "width": 20,
            "height": 20,
            "spawn_frame": 5,
            "sub": {
                "path": "assets/sprites/Character-5/PROJECTILE-1-2-Sheet.png",
                "frames": 1,
                "frame_duration": 150,
                "width": 20,
                "height": 20,
            },
        },
        "s2": {
            "path": "assets/sprites/Character-5/PROJECTILE-2-1-Sheet.png",
            "frames": 4,
            "loops": 3,
            "stops": True,
            "speed": 5,
            "width": 20,
            "height": 20,
            "spawn_frame": 5,
            "sub": {
                "path": "assets/sprites/Character-5/PROJECTILE-2-2-Sheet.png",
                "frames": 1,
                "frame_duration": 150,
                "width": 20,
                "height": 20,
            },
        },
    },
}

# 40x40 c la ref de base donc le offset serais a (0,0)
# En gros ce dictionnaire met un offset pour eviter un decalage l'hors de la position visuel du joueur quand on fait ue animations d'attaque
SPRITE_OFFSETS = {
    1: {
        "idle": (0, 0),
        "move": (0, 0),
        "hurt": (0, 0),
        "s1": (0, 0),
        "s2": (0, 0),
        "s3": (0, 0),
        "s3_2": (0, 0),
    },
    2: {
        "idle": (0, 0),
        "move": (0, 0),
        "hurt": (0, 0),
        "s1": (-5, 0),
        "s2": (0, -25),
        "s3": (0, 0),
        "s3_2": (0, -12),
    },
    3: {
        "idle": (0, 0),
        "move": (-10, -10),
        "hurt": (0, 0),
        "s1": (-10, -10),
        "s1_1": (-10, -10),
        "s1_2": (-10, -10),
        "s1_3": (-10, -10),
        "s2": (-10, -10),
        "s3": (-10, -10),
    },
    4: {
        "idle": (0, 0),
        "move": (-12, 0),
        "hurt": (0, 0),
        "s1": (-18, 0),
        "s1_1": (-18, 0),
        "s1_2": (-18, 0),
        "s1_3": (-18, 0),
        "s2": (-55, -12),
        "s2_1": (-55, -12),
        "s2_2": (-55, -12),
        "s3": (-30, -27),
    },
    5: {
        "idle": (0, 0),
        "move": (0, 0),
        "hurt": (0, 0),
        "s1": (0, 0),
        "s2": (-35, -15),
        "s3": (0, 0),
    },
}

CHAR6_CANS_HUD_POSITIONS = {
    1: (300, 12),
    2: (1143, 12),
    3: (300, 542),
    4: (1143, 542),
}
CHAR6_CANS_GAP = 50

# Data pour update les bubbles dans les remotes
BUBBLE_EFFECT_DATA = {
    2: {
        "path": "assets/sprites/Character-2/effect-2-S3-Sheet.png",
        "frames": 4,
        "frame_duration": 200,
        "width": 32,
        "height": 32,
        "loop": True,
    }
}

DIMENS_4_UPDATE = {
    "MOVE": (64, 40),
    "S1": (75, 40),
    "S1_1": (75, 40),
    "S1_2": (75, 40),
    "S1_3": (75, 40),
    "S2": (160, 91),
    "S2_1": (160, 91),
    "S2_2": (160, 91),
    "S3": (176, 80),
}

SPRITE_OFFSETS_4_UPDATE = {
    "idle": (0, 0),
    "move": (-12, 0),
    "hurt": (0, 0),
    "s1": (-18, 0),
    "s1_1": (-18, 0),
    "s1_2": (-18, 0),
    "s1_3": (-18, 0),
    "s2": (-55, -12),
    "s2_1": (-55, -12),
    "s2_2": (-55, -12),
    "s3": (-30, -27),
}

SOUNDS = {
    1: {
        "s1": "assets/sounds_effect/SFX 1.wav",
        "s2": "assets/sounds_effect/SFX 7.wav",
        "s3": "assets/sounds_effect/SFX 1.wav",
    },
    2: {
        "s1": "assets/sounds_effect/SFX 3.wav",
        "s2": "assets/sounds_effect/SFX 7.wav",
        "s3": "assets/sounds_effect/SFX 5.wav",
    },
    3: {
        "s1": "assets/sounds_effect/SFX 2.wav",
        "s2": "assets/sounds_effect/SFX 4.wav",
        "s3": "assets/sounds_effect/SFX 6.wav",
    },
    4: {
        "s1": "assets/sounds_effect/SFX 2.wav",
        "s2": "assets/sounds_effect/SFX 4.wav",
        "s3": "assets/sounds_effect/SFX 6.wav",
    },
    5: {
        "s1": "assets/sounds_effect/SFX 7.wav",
        "s2": "assets/sounds_effect/SFX 7.wav",
        "s3": "assets/sounds_effect/SFX 2.wav",
    },
}

COLOR_BODY = (0, 255, 0, 120)
COLOR_ATTACK = (255, 60, 60, 160)


class Character:
    def __init__(self, char_num):
        stats = CHAR_STATS.get(
            char_num, DEFAULT_STATS
        )  # If the character isn't implemnted yet, then we took the default stat
        self.char_num = char_num
        self.health = stats["health"]
        self.max_health = stats["health"]
        self.speed = stats["speed"]
        self.color = stats["color"]

        self.position = (400, 400)
        self.direction = "right"

        self.frames_S3_2 = []
        self.frames_S3_2_left = []

        self._load_animations()

        self.frame_IDLE = 0
        self.frame_MOVE = 0
        self.frame_HURT = 0

        self.is_hurt = False
        self.is_dead = False
        self.is_moving = False

        self.frame_S1 = 0
        self.frame_S2 = 0
        self.frame_S3 = 0

        self.is_attacking_s3 = False
        self.is_attacking_s1 = False
        self.is_attacking_s2 = False

        self.timer_IDLE = 0

        self.timer_MOVE = 0
        self.timer_HURT = 0
        self.timer_S1 = 0
        self.timer_S2 = 0
        self.timer_S3 = 0

        self._hit_this_swing = set()

        self.status = StatusManager()
        self.projectiles = []
        self.is_hidden = False

        self.s3_hit = False
        self.frame_S3_2 = 0
        self.timer_S3_2 = 0

        self._pending_projectiles = {}
        self._just_spawned_projectiles = []

    def _dims(self, anim, fallback=None):
        char_dimensi = DIMENS.get(self.char_num, {})
        if anim in char_dimensi:
            return char_dimensi[anim]
        if fallback is not None and fallback in char_dimensi:
            return char_dimensi[fallback]
        return (FRAME_SIZE, FRAME_SIZE)

    def _blank(self, color=None, w=None, h=None):
        w = w or FRAME_SIZE
        h = h or FRAME_SIZE
        surf = pyg.Surface((w, h))
        surf.fill(color if color else self.color)
        return [surf]

    def _maybe_spawn_projectile(self, skill_num):
        proj_data = self._pending_projectiles.get(skill_num)
        if proj_data is None:
            return
        current_frame = {1: self.frame_S1, 2: self.frame_S2, 3: self.frame_S3}.get(
            skill_num, 0
        )
        if current_frame >= proj_data.get("spawn_frame", 0):
            p = Projectile(
                self.char_num, skill_num, self.position, self.direction, proj_data
            )
            self.projectiles.append(p)
            self._just_spawned_projectiles.append((skill_num, p))
            del self._pending_projectiles[skill_num]

    def _load_sheet(self, filename, w=FRAME_SIZE, h=FRAME_SIZE):
        try:
            path = get_asset_path("sprites", f"Character-{self.char_num}", filename)
            sheet = pyg.image.load(path).convert_alpha()
            n = max(1, sheet.get_width() // w)
            frames = []
            for i in range(n):
                if (i + 1) * w <= sheet.get_width() and h <= sheet.get_height():
                    frame = sheet.subsurface((i * w, 0, w, h))
                    if CHARACTER_SCALE != 1.0:
                        sw = int(w * CHARACTER_SCALE)
                        sh = int(h * CHARACTER_SCALE)
                        frame = pyg.transform.scale(frame, (sw, sh))
                    frames.append(frame)
            if not frames:
                print_warning(
                    f"[LOAD] {filename} trouvé mais 0 frames extraites (sheet={sheet.get_size()}, w={w}, h={h})"
                )
            return frames if frames else None
        except (FileNotFoundError, pyg.error) as e:
            print_warning(
                f"[LOAD] {filename} introuvable pour char {self.char_num}: {e}"
            )
            return None

    @staticmethod
    def _flip(frames):
        return [pyg.transform.flip(f, True, False) for f in frames]

    def _load_animations(self):
        s3w2, s3h2 = self._dims("S3_2")
        s3_2 = self._load_sheet("S3-2-Sheet.png", s3w2, s3h2) or self._blank(
            w=s3w2, h=s3h2
        )
        self.frames_S3_2 = s3_2
        self.frames_S3_2_left = self._flip(s3_2)

        mw, mh = self._dims("MOVE")
        s1w, s1h = self._dims("S1")
        s2w, s2h = self._dims("S2")
        s3w, s3h = self._dims("S3")

        s3 = (
            self._load_sheet("S3-Sheet.png", s3w, s3h)
            or self._load_sheet("S3-1-Sheet.png", s3w, s3h)
            or self._blank(w=s3w, h=s3h)
        )

        raw_idle = self._load_sheet("IDLE-Sheet.png")
        self.has_sprites = raw_idle is not None

        idle = raw_idle or self._blank()
        move = self._load_sheet("MOVE-Sheet.png", mw, mh) or self._blank(w=mw, h=mh)
        hurt = self._load_sheet("HURT-Sheet.png") or idle
        dead = self._load_sheet("DEAD-Sheet.png") or self._blank((80, 0, 0))
        s1 = (
            self._load_sheet("S1-Sheet.png", s1w, s1h)
            or self._load_sheet("S1-1-Sheet.png", s1w, s1h)
            or self._blank(w=s1w, h=s1h)
        )
        s2 = (
            self._load_sheet("S2-Sheet.png", s2w, s2h)
            or self._load_sheet("S2-1-Sheet.png", s2w, s2h)
            or self._blank(w=s2w, h=s2h)
        )

        self.frames_IDLE = idle
        self.frames_MOVE = move
        self.frames_HURT = hurt
        self.frames_DEAD = dead
        self.frames_S1 = s1
        self.frames_S2 = s2
        self.frames_S3 = s3

        self.frames_IDLE_left = self._flip(idle)
        self.frames_MOVE_left = self._flip(move)
        self.frames_HURT_left = self._flip(hurt)
        self.frames_S1_left = self._flip(s1)
        self.frames_S2_left = self._flip(s2)
        self.frames_S3_left = self._flip(s3)

        self.bubble_source_char = None

        self.is_remote = False

        self._sounds = {}
        char_sounds = SOUNDS.get(self.char_num, {})
        for skill_key, path in char_sounds.items():
            try:
                snd = pyg.mixer.Sound(
                    get_asset_path(*path.replace("assets/", "").split("/"))
                )
                snd.set_volume(1)
                self._sounds[skill_key] = snd
            except (FileNotFoundError, pyg.error) as e:
                print_warning(
                    f"[SOUND] {path} introuvable pour char {self.char_num}: {e}"
                )

    def move(self, direction):
        if self.is_dead or self.is_hurt:
            return
        if self.status.is_disabled:
            return
        if self.status.is_stunned or self.status.is_grabbed:
            return
        if self.is_attacking_s1 or self.is_attacking_s2 or self.is_attacking_s3:
            return

        x, y = self.position
        nx, ny = 0, 0
        if direction == "up":
            nx, ny = 0, 1
            new_pos = (x, y - self.speed)
        elif direction == "down":
            nx, ny = 0, -1
            new_pos = (x, y + self.speed)
        elif direction == "left":
            nx, ny = -1, 0
            new_pos = (x - self.speed, y)
            self.direction = "left"
        elif direction == "right":
            nx, ny = 1, 0
            new_pos = (x + self.speed, y)
            self.direction = "right"
        else:
            return

        player_rect = pyg.Rect(
            int(new_pos[0]), int(new_pos[1]), SCALED_FRAME_SIZE, SCALED_FRAME_SIZE
        )
        if any(player_rect.colliderect(wall) for wall in _map_mod.ACTIVE_COLLISIONS):
            return

        self.position = new_pos

        if self.status.is_oiled:
            oild = self.status.effects.get("oiled")
            if oild:
                oild.set_drift(nx, ny, self.speed)

        if self.status.is_wet:
            wet = self.status.effects.get("wet")
            if wet:
                wet.set_drift(nx, ny, self.speed)

    def take_damage(self, amount, trigger_hurt=True, parriable=True):
        if self.status.is_disabled:
            return False

        self.health = max(0, self.health - amount)
        if self.health == 0:
            self.is_dead = True
            self.status.apply_disabled("right")
        elif trigger_hurt:
            self.is_hurt = True
            self.frame_HURT = 0
            self.timer_HURT = 0
        return True

    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)

    def get_status(self):
        return {
            "char_num": self.char_num,
            "health": self.health,
            "position": self.position,
        }

    def use_skill(self, skill_num):
        skill_key = f"s{skill_num}"
        frames_map = {
            1: ("is_attacking_s1", "frame_S1", "timer_S1"),
            2: ("is_attacking_s2", "frame_S2", "timer_S2"),
            3: ("is_attacking_s3", "frame_S3", "timer_S3"),
        }

        if self.is_dead or self.is_hurt:
            return False

        if skill_num not in frames_map:
            return False

        if self.status.is_stunned:
            return False

        flag, frame_attr, timer_attr = frames_map[skill_num]
        if getattr(self, flag):
            return False

        setattr(self, flag, True)
        setattr(self, frame_attr, 0)
        setattr(self, timer_attr, 0)
        self._hit_this_swing = set()

        if skill_num == 3:
            self.s3_hit = False
            self.frame_S3_2 = 0
            self.timer_S3_2 = 0

        # Son
        snd = getattr(self, "_sounds", {}).get(skill_key)
        if snd:
            snd.play()

        proj_data = PROJECTILES_INFOS.get(self.char_num, {}).get(skill_key)
        if proj_data:
            if proj_data.get("spawn_frame", 0) == 0:
                p = Projectile(
                    self.char_num, skill_num, self.position, self.direction, proj_data
                )
                self.projectiles.append(p)
                self._just_spawned_projectiles.append((skill_num, p))
            else:
                self._pending_projectiles[skill_num] = proj_data
        return True

    def update_projectiles(self, dt, targets):
        for p in self.projectiles:
            p.update(dt, targets)
        self.projectiles = [p for p in self.projectiles if not p.is_dead]

    def draw_projectiles(self, surface):
        for p in self.projectiles:
            p.draw(surface)

    def _handle_s1_update(self, dt):
        self.timer_S1 += dt
        if self.timer_S1 >= SKILL_SPEED:
            self.timer_S1 = 0
            self.frame_S1 += 1
            self._maybe_spawn_projectile(1)
            if self.frame_S1 >= len(self.frames_S1):
                self.frame_S1 = 0
                self.is_attacking_s1 = False
                self._hit_this_swing = set()
                self._pending_projectiles.pop(1, None)

    def update_animation(self, dt, is_moving):
        self.status.update(dt)

        burn_dmg = self.status.get_burn_damage()
        if burn_dmg > 0:
            if self.status.is_oiled:
                burn_dmg = int(burn_dmg * 2.0)
            self.take_damage(burn_dmg, trigger_hurt=False, parriable=False)

        if hasattr(self, "bubble_effect") and self.bubble_effect:
            self.bubble_effect.update(dt)
            if not self.status.is_disabled:
                self.bubble_effect = None
                self.is_hidden = False

        if self.status.is_disabled:
            is_moving = False
        push_delta = self.status.get_push_delta(dt)
        if push_delta != 0:
            x, y = self.position
            self.position = (x + push_delta, y)

        self.is_moving = is_moving

        grb_dx, grb_dy = self.status.get_grab_delta(self.position, dt)
        if grb_dx != 0.0 or grb_dy != 0.0:
            x, y = self.position
            self.position = (int(x + grb_dx), int(y + grb_dy))
        if self.status.is_stunned or self.status.is_grabbed:
            is_moving = False
        if self.status.is_oiled:
            oild = self.status.effects.get("oiled")
            if oild:
                odx, ody = oild.get_drift(dt)
                if odx != 0 or ody != 0:
                    x, y = self.position
                    self.position = (x + odx, y + ody)

        if self.status.is_wet:
            wet = self.status.effects.get("wet")
            if wet:
                wdx, wdy = wet.get_drift(dt)
                if wdx != 0 or wdy != 0:
                    x, y = self.position
                    self.position = (x + wdx, y + wdy)

        if self.is_attacking_s1:
            self._handle_s1_update(dt)

        if self.is_attacking_s2:
            self.timer_S2 += dt
            if self.timer_S2 >= SKILL_SPEED:
                self.timer_S2 = 0
                self.frame_S2 += 1
                self._maybe_spawn_projectile(2)
                if self.frame_S2 >= len(self.frames_S2):
                    self.frame_S2 = 0
                    self.is_attacking_s2 = False
                    self._hit_this_swing = set()

        if self.is_attacking_s3:
            if self.s3_hit:
                self.timer_S3_2 += dt
                if self.timer_S3_2 >= SKILL_SPEED:
                    self.timer_S3_2 = 0
                    self.frame_S3_2 += 1
                    self._maybe_spawn_projectile(3)
                    if self.frame_S3_2 >= len(self.frames_S3_2):
                        self.frame_S3_2 = 0
                        self.timer_S3_2 = 0
                        self.is_attacking_s3 = False
                        self.s3_hit = False
                        self._hit_this_swing = set()

            else:
                self.timer_S3 += dt
                if self.timer_S3 >= SKILL_SPEED:
                    self.timer_S3 = 0
                    self.frame_S3 += 1
                    if self.frame_S3 >= len(self.frames_S3):
                        self.frame_S3 = 0
                        self.is_attacking_s3 = False
                        self._hit_this_swing = set()
                        self.s3_hit = False
                        self.frame_S3_2 = 0
                        self.timer_S3_2 = 0

        if self.is_hurt:
            self.timer_HURT += dt
            if self.timer_HURT >= HURT_SPEED:
                self.timer_HURT = 0
                self.frame_HURT += 1
                if self.frame_HURT >= len(self.frames_HURT):
                    self.frame_HURT = 0
                    self.is_hurt = False

        if is_moving:
            self.timer_MOVE += dt
            if self.timer_MOVE >= MOVE_SPEED:
                self.timer_MOVE = 0
                self.frame_MOVE = (self.frame_MOVE + 1) % len(self.frames_MOVE)
        else:
            self.timer_IDLE += dt
            if self.timer_IDLE >= IDLE_SPEED:
                self.timer_IDLE = 0
                self.frame_IDLE = (self.frame_IDLE + 1) % len(self.frames_IDLE)

    def get_current_sprite(self):
        if self.is_hidden:
            return None  # in the buuble
        left = self.direction == "left"

        if self.is_dead:
            frames = self.frames_DEAD
            return frames[-1] if frames else None

        if self.is_hurt:
            frames = self.frames_HURT_left if left else self.frames_HURT
            if not frames:
                self.is_hurt = False
            else:
                return frames[min(self.frame_HURT, len(frames) - 1)]

        if self.is_attacking_s1:
            frames = self.frames_S1_left if left else self.frames_S1
            if frames:
                return frames[min(self.frame_S1, len(frames) - 1)]

        if self.is_attacking_s2:
            frames = self.frames_S2_left if left else self.frames_S2
            if frames:
                return frames[min(self.frame_S2, len(frames) - 1)]

        if self.is_attacking_s3:
            if self.s3_hit:
                frames = self.frames_S3_2_left if left else self.frames_S3_2
                if frames:
                    return frames[min(self.frame_S3_2, len(frames) - 1)]
            else:
                frames = self.frames_S3_left if left else self.frames_S3
                if frames:
                    return frames[min(self.frame_S3, len(frames) - 1)]

        if self.is_moving:
            frames = self.frames_MOVE_left if left else self.frames_MOVE
            if frames:
                return frames[self.frame_MOVE % len(frames)]

        frames = self.frames_IDLE_left if left else self.frames_IDLE
        if frames:
            return frames[self.frame_IDLE % len(frames)]
        return None

    def get_body_rect(self):
        x, y = self.position
        return pyg.Rect(x, y, SCALED_FRAME_SIZE, SCALED_FRAME_SIZE)

    def _active_skill(self):
        if self.is_attacking_s1:
            return 1  # skill 1
        if self.is_attacking_s2:
            return 2  # 2
        if self.is_attacking_s3:
            return 3  # and 3
        return None  # No skill activated

    def _current_skill_frame(self):
        skill = self._active_skill()
        return {1: self.frame_S1, 2: self.frame_S2, 3: self.frame_S3}.get(skill, 0)

    def get_attack_hitbox(self):
        skill = self._active_skill()
        if skill is None:
            return None

        data = HITBOX_DATA.get(self.char_num, {}).get(skill, _DEFAULT_HITBOX)

        current_frame = self._current_skill_frame()
        if current_frame < data.get("frame_start", 0):
            return None
        if data.get("frame_end") is not None and current_frame > data["frame_end"]:
            return None

        px, py = data["offset"]
        sw, sh = data["size"]
        px = int(px * CHARACTER_SCALE)
        py = int(py * CHARACTER_SCALE)
        sw = int(sw * CHARACTER_SCALE)
        sh = int(sh * CHARACTER_SCALE)
        x, y = self.position
        if self.direction == "left":
            px = SCALED_FRAME_SIZE - px - sw
        return pyg.Rect(x + px, y + py, sw, sh)

    def check_hits(self, targets):

        skill = self._active_skill()
        if skill is None:
            return

        hitbox = self.get_attack_hitbox()
        if hitbox is None:  # out of frame
            return

        dmg = HITBOX_DATA.get(self.char_num, {}).get(skill, _DEFAULT_HITBOX)["damage"]

        for target in targets:
            if target is self or target.is_dead:
                continue

            if skill == 3 and not self.s3_hit:
                if hitbox.colliderect(target.get_body_rect()) and not self.s3_hit:
                    if id(target) in self._hit_this_swing:
                        continue
                    if hasattr(target, "notify_incoming_hit"):
                        target.notify_incoming_hit(self.position, self)
                    hit = target.take_damage(_calc_damage(dmg, target, skill))
                    self._hit_this_swing.add(id(target))
                    if hit:
                        self._apply_status_on_hit(target, skill)
                    if not self.is_remote and getattr(self, "_s3_stops_on_hit", True):
                        self.s3_hit = True
                        self.frame_S3_2 = 0
                        self.timer_S3_2 = 0
                    return
                continue

            tid = id(target)
            if tid in self._hit_this_swing:
                continue
            if hitbox.colliderect(target.get_body_rect()):
                if hasattr(target, "notify_incoming_hit"):
                    target.notify_incoming_hit(self.position, self)
                hit = target.take_damage(_calc_damage(dmg, target, skill))
                if hit:
                    self._apply_status_on_hit(target, skill)
                self._hit_this_swing.add(tid)

    def draw_hitbox(self, surface):
        if not TMP__GET_SURFACE_HITBOX_ATTACKS_:
            return

        body = self.get_body_rect()
        atk = self.get_attack_hitbox()

        pyg.draw.rect(surface, (0, 255, 0), body, 2)
        if atk:
            pyg.draw.rect(surface, (255, 60, 60), atk, 2)

    @staticmethod
    def switch_TMP__GET_SURFACE_HITBOX_ATTACKS_():
        global TMP__GET_SURFACE_HITBOX_ATTACKS_
        TMP__GET_SURFACE_HITBOX_ATTACKS_ = not TMP__GET_SURFACE_HITBOX_ATTACKS_

    # petit helper
    def get_anim_state(self):
        if self.is_dead:
            return "dead"
        if self.is_hurt:
            return "hurt"
        if self.is_attacking_s1:
            return "s1"
        if self.is_attacking_s2:
            return "s2"
        if self.is_attacking_s3:
            return "s3_2" if self.s3_hit else "s3"
        if self.is_moving:
            return "move"
        return "idle"

    def get_blit_offset(self, sprite):
        anim = self.get_anim_state()
        raw_dx, raw_dy = SPRITE_OFFSETS.get(self.char_num, {}).get(anim, (0, 0))
        dx = int(raw_dx * CHARACTER_SCALE)
        dy = int(raw_dy * CHARACTER_SCALE)

        if self.direction == "left":
            frame_w = sprite.get_width()
            dx = -(frame_w - SCALED_FRAME_SIZE) - dx

        return dx, dy

    def get_network_state(self):
        return {}

    def apply_extra_network_state(self, extra):
        pass

    def apply_network_state(self, state):
        self.apply_extra_network_state(state.get("char_state", {}))
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

        if "is_hidden" in state:
            new_hidden = bool(state["is_hidden"])
            if new_hidden and not self.is_hidden:
                caster = state.get("bubble_caster")
                if caster is not None:
                    effect_data = BUBBLE_EFFECT_DATA.get(int(caster))
                    if effect_data:
                        self.bubble_effect = SubProjectile(
                            self.position[0], self.position[1], effect_data
                        )
            elif not new_hidden and self.is_hidden:
                self.bubble_effect = None
                self.bubble_source_char = None
            self.is_hidden = new_hidden

        if "s3_hit" in state:
            self.s3_hit = bool(state["s3_hit"])
        if "frame_s3_2" in state:
            self.frame_S3_2 = int(state["frame_s3_2"])

        ak = state.get("is_attacking", {})
        new_s1 = bool(ak.get("1", False))
        new_s2 = bool(ak.get("2", False))
        new_s3 = bool(ak.get("3", False))
        if (
            (new_s1 and not self.is_attacking_s1)
            or (new_s2 and not self.is_attacking_s2)
            or (new_s3 and not self.is_attacking_s3)
        ):
            self._hit_this_swing = set()
        self.is_attacking_s1 = new_s1
        self.is_attacking_s2 = new_s2
        self.is_attacking_s3 = new_s3

        i = state.get("anim_indices", {})
        self.frame_IDLE = int(i.get("idle", self.frame_IDLE))
        self.frame_MOVE = int(i.get("move", self.frame_MOVE))
        self.frame_HURT = int(i.get("hurt", self.frame_HURT))
        self.frame_S1 = int(i.get("skill1", self.frame_S1))
        self.frame_S2 = int(i.get("skill2", self.frame_S2))
        self.frame_S3 = int(i.get("skill3", self.frame_S3))

    def get_effect_sprite(self):
        return None

    def _apply_status_on_hit(self, target, skill):
        data = HITBOX_DATA.get(self.char_num, {}).get(skill, {})
        fn = data.get("status_applied")
        if fn:
            fn(self, target)


class Furnace(Character):
    _s3_stops_on_hit = False  # S3 animation continues even after hitting

    def __init__(self):
        super().__init__(1)


class Water(Character):
    def __init__(self):
        super().__init__(2)

    def get_attack_hitbox(self):
        if not self.is_attacking_s3 or self.s3_hit:
            return super().get_attack_hitbox()

        data = HITBOX_DATA[2][3]
        px, py = data["offset"]
        sh = data["size"][1]
        full_w = data["size"][0]

        frm = self.frame_S3
        if frm < 6 or frm > 16:
            return None

        ratio = (frm - 5) / 11.0  # frame 6 → 1/11 ≈ 9%, frame 16 → 100%
        sw = int(full_w * ratio)
        if sw <= 0:
            return None

        px = int(px * CHARACTER_SCALE)
        py = int(py * CHARACTER_SCALE)
        sw = int(sw * CHARACTER_SCALE)
        sh = int(sh * CHARACTER_SCALE)
        x, y = self.position
        if self.direction == "left":
            px = SCALED_FRAME_SIZE - px - sw

        return pyg.Rect(x + px, y + py, sw, sh)

    def _apply_status_on_hit(self, target, skill):
        super()._apply_status_on_hit(target, skill)

        if skill == 3:
            target.is_hidden = True
            target.bubble_source_char = self.char_num
            effect_data = BUBBLE_EFFECT_DATA.get(self.char_num)
            if effect_data:
                target.bubble_effect = SubProjectile(
                    target.position[0], target.position[1], effect_data
                )

        elif skill == 1:
            effect_data = {
                "path": "assets/sprites/Character-2/effect-2-S1-Sheet.png",
                "frames": 2,
                "frame_duration": 150,
                "width": 80,
                "height": 48,
            }
            self.projectiles.append(
                SubProjectile(
                    target.position[0],
                    target.position[1],
                    effect_data,
                    direction=self.direction,
                )
            )


CHAR3_S1_PHASE3_HITBOX = {"offset": (15, 3), "size": (90, 45)}
CHAR3_S1_DAMAGE_NORMAL = 25
CHAR3_S1_DAMAGE_PARRY = 55


class Character3(Character):
    def __init__(self):
        self.s1_phase = 1
        self.s1_parried = False
        self._last_hit_by_pos = None
        self._parried_attacker = None
        self.frame_S1_2 = 0
        self.timer_S1_2 = 0
        self.frame_S1_3 = 0
        self.timer_S1_3 = 0
        self.frames_S1_1 = []
        self.frames_S1_2_anim = []
        self.frames_S1_3 = []
        self.frames_S1_1_left = []
        self.frames_S1_2_anim_left = []
        self.frames_S1_3_left = []
        super().__init__(3)

    def notify_incoming_hit(self, attacker_pos, attacker=None):
        self._last_hit_by_pos = attacker_pos
        self._parried_attacker = attacker

    def _load_animations(self):
        super()._load_animations()

        s1_1w, s1_1h = self._dims("S1_1", "S1")
        s1_2w, s1_2h = self._dims("S1_2", "S1")
        s1_3w, s1_3h = self._dims("S1_3", "S1")

        s1_1 = self._load_sheet("S1-1-Sheet.png", s1_1w, s1_1h) or self._blank(
            w=s1_1w, h=s1_1h
        )
        s1_2 = self._load_sheet("S1-2-Sheet.png", s1_2w, s1_2h) or self._blank(
            w=s1_2w, h=s1_2h
        )
        s1_3 = self._load_sheet("S1-3-Sheet.png", s1_3w, s1_3h) or self._blank(
            w=s1_3w, h=s1_3h
        )

        self.frames_S1_1 = s1_1
        self.frames_S1_2_anim = s1_2
        self.frames_S1_3 = s1_3
        self.frames_S1_1_left = self._flip(s1_1)
        self.frames_S1_2_anim_left = self._flip(s1_2)
        self.frames_S1_3_left = self._flip(s1_3)

        self.frames_S1 = s1_1
        self.frames_S1_left = self.frames_S1_1_left

    def use_skill(self, skill_num):
        if skill_num == 1 and not self.is_attacking_s1:
            # Son
            snd = getattr(self, "_sounds", {}).get("s1")
            if snd:
                snd.play()
            self.is_attacking_s1 = True
            self.s1_phase = 1
            self.s1_parried = False
            self._parried_attacker = None
            self.frame_S1 = 0
            self.timer_S1 = 0
            self.frame_S1_2 = 0
            self.timer_S1_2 = 0
            self.frame_S1_3 = 0
            self.timer_S1_3 = 0
            self._hit_this_swing = set()
            return True
        return super().use_skill(skill_num)

    def take_damage(self, amount, trigger_hurt=True, parriable=True):
        if parriable and self.is_attacking_s1 and self.s1_phase == 1:
            self.s1_parried = True
            return False
        return super().take_damage(
            amount, trigger_hurt=trigger_hurt, parriable=parriable
        )

    def _handle_s1_update(self, dt):
        if self.s1_phase == 1:
            if self.s1_parried:
                self.s1_phase = 2
                self.frame_S1_2 = 0
                self.timer_S1_2 = 0
                if self._last_hit_by_pos is not None:
                    ax, ay = self._last_hit_by_pos
                    cx, cy = self.position
                    if ax >= cx:
                        self.position = (int(ax) + SCALED_FRAME_SIZE // 2, cy)
                        self.direction = "left"
                    else:
                        self.position = (int(ax) - SCALED_FRAME_SIZE // 2, cy)
                        self.direction = "right"
                    self._last_hit_by_pos = None
                self._hit_this_swing = set()
                return

            self.timer_S1 += dt
            if self.timer_S1 >= SKILL_SPEED:
                self.timer_S1 = 0
                self.frame_S1 += 1
                if self.frame_S1 >= len(self.frames_S1_1):
                    self.s1_phase = 3
                    self.frame_S1_3 = 0
                    self.timer_S1_3 = 0

        elif self.s1_phase == 2:
            self.timer_S1_2 += dt
            if self.timer_S1_2 >= SKILL_SPEED:
                self.timer_S1_2 = 0
                self.frame_S1_2 += 1
                if self.frame_S1_2 >= len(self.frames_S1_2_anim):
                    self.is_attacking_s1 = False
                    self.s1_phase = 1
                    self.s1_parried = False
                    self._parried_attacker = None
                    self._hit_this_swing = set()

        elif self.s1_phase == 3:
            self.timer_S1_3 += dt
            if self.timer_S1_3 >= SKILL_SPEED:
                self.timer_S1_3 = 0
                self.frame_S1_3 += 1
                if self.frame_S1_3 >= len(self.frames_S1_3):
                    self.is_attacking_s1 = False
                    self.s1_phase = 1
                    self.s1_parried = False
                    self._parried_attacker = None
                    self._hit_this_swing = set()

    def get_current_sprite(self):
        if self.is_hidden:
            return None

        if self.is_attacking_s1:
            left = self.direction == "left"
            if self.s1_phase == 1:
                frames = self.frames_S1_1_left if left else self.frames_S1_1
                idx = self.frame_S1
            elif self.s1_phase == 2:
                frames = self.frames_S1_2_anim_left if left else self.frames_S1_2_anim
                idx = self.frame_S1_2
            else:
                frames = self.frames_S1_3_left if left else self.frames_S1_3
                idx = self.frame_S1_3
            if frames:
                return frames[min(idx, len(frames) - 1)]
            return None

        return super().get_current_sprite()

    def get_anim_state(self):
        if self.is_attacking_s1:
            return f"s1_{self.s1_phase}"
        return super().get_anim_state()

    def get_network_state(self):
        return {"s1_phase": self.s1_phase}

    def apply_extra_network_state(self, extra):
        if "s1_phase" in extra:
            self.s1_phase = int(extra["s1_phase"])

    def get_attack_hitbox(self):
        if self.is_attacking_s1 and self.s1_phase in (1, 2):
            return None
        return super().get_attack_hitbox()

    def check_hits(self, targets):
        if self.is_attacking_s1:
            # Phase 1 : fenêtre de parade — pas de hitbox
            if self.s1_phase == 1:
                return

            # Phase 3 : animation ratée (pas de parade) — pas de dégâts
            if self.s1_phase == 3:
                return

            attacker = self._parried_attacker
            if attacker is None or attacker.is_dead:
                for t in targets:
                    if t is not self and not t.is_dead:
                        attacker = t
                        break
            if attacker is not None and not attacker.is_dead:
                tid = id(attacker)
                if tid not in self._hit_this_swing:
                    attacker.take_damage(
                        _calc_damage(CHAR3_S1_DAMAGE_PARRY, attacker, 1)
                    )
                    self._hit_this_swing.add(tid)

        elif self.is_attacking_s3:
            hitbox = self.get_attack_hitbox()
            if hitbox is None:
                return
            dmg = HITBOX_DATA.get(self.char_num, {}).get(3, _DEFAULT_HITBOX)["damage"]
            for target in targets:
                if target is self or target.is_dead:
                    continue
                tid = id(target)
                if tid in self._hit_this_swing:
                    continue
                if hitbox.colliderect(target.get_body_rect()):
                    target.take_damage(_calc_damage(dmg, target, 3))
                    self._apply_status_on_hit(target, 3)
                    self._hit_this_swing.add(tid)

        else:
            super().check_hits(targets)


def make_character(char_num):
    _registry = {
        1: Furnace,
        2: Water,
        3: Character3,
        4: Character4,
        5: Character5,
    }
    cls = _registry.get(char_num)
    return cls() if cls else Character(char_num)


# petit helper pour les classes qui suivent
def _resolve_path(relative_path):
    parts = relative_path.replace("assets/", "").split("/")
    return get_asset_path(*parts)


class Projectile:
    def __init__(self, char_num, skill_num, origin_pos, direction, data):
        self.x, self.y = float(origin_pos[0]), float(origin_pos[1])
        self.direction = direction
        self.speed = data["speed"]
        self.stops = data["stops"]
        raw_w = data["width"]
        raw_h = data["height"]
        self.width = int(raw_w * CHARACTER_SCALE)
        self.height = int(raw_h * CHARACTER_SCALE)
        self.total_frames = data["frames"] * data["loops"]
        self.frames_per_loop = data["frames"]
        self.current_frame = 0
        self.timer = 0
        self.is_dead = False
        self._hit_targets = set()
        self.sub_data = data.get("sub", None)
        self.sub_projectiles = []
        self.skill_num = skill_num

        self.damage = HITBOX_DATA.get(char_num, {}).get(skill_num, _DEFAULT_HITBOX)[
            "damage"
        ]

        sheet = pyg.image.load(_resolve_path(data["path"])).convert_alpha()
        n = max(1, sheet.get_width() // raw_w)
        raw_frames = [sheet.subsurface((i * raw_w, 0, raw_w, raw_h)) for i in range(n)]
        if CHARACTER_SCALE != 1.0:
            raw_frames = [
                pyg.transform.scale(f, (self.width, self.height)) for f in raw_frames
            ]
        self.frames_right = raw_frames
        self.frames_left = [pyg.transform.flip(f, True, False) for f in raw_frames]
        self.double_hit = data.get("double_hit", False)
        self._hit_counts = {}

        self.effect_data = data.get("effect", None)
        self.effect_sprites = []

        self.captured_target = None

        if self.effect_data:
            sheet = pyg.image.load(self.effect_data["path"]).convert_alpha()
            ew, eh = self.effect_data["width"], self.effect_data["height"]
            n = max(1, sheet.get_width() // ew)
            eff_frames = [sheet.subsurface((i * ew, 0, ew, eh)) for i in range(n)]
            if CHARACTER_SCALE != 1.0:
                sew, seh = int(ew * CHARACTER_SCALE), int(eh * CHARACTER_SCALE)
                eff_frames = [pyg.transform.scale(f, (sew, seh)) for f in eff_frames]
            self._effect_frames = eff_frames
        else:
            self._effect_frames = []

    def update(self, dt, targets):

        if self.current_frame >= self.total_frames:
            if self.stops and self.sub_data and not self._hit_targets:
                self._spawn_sub(self.x, self.y)
            self.is_dead = True

        if self.is_dead:
            for sub in self.sub_projectiles:
                sub.update(dt)
                if (
                    sub.is_dead
                    and hasattr(sub, "release_target")
                    and sub.release_target
                ):
                    t = sub.release_target
                    t.is_hidden = False
                    offset = (
                        SCALED_FRAME_SIZE
                        if self.direction == "right"
                        else -SCALED_FRAME_SIZE
                    )
                    x, y = (
                        self.position if hasattr(self, "position") else (sub.x, sub.y)
                    )
                    t.position = (int(sub.x + offset), int(sub.y))
                    t.status.effects.pop("disabled", None)
                    sub.release_target = None
            self.sub_projectiles = [s for s in self.sub_projectiles if not s.is_dead]
            for e in self.effect_sprites:
                e.update(dt)
            self.effect_sprites = [e for e in self.effect_sprites if not e.is_dead]
            return

        if self.direction == "right":
            self.x += self.speed
        else:
            self.x -= self.speed

        rect = self.get_rect()
        for target in targets:
            if target.is_dead:
                continue
            tid = id(target)

            if self.double_hit:
                count = self._hit_counts.get(tid, 0)
                if count >= 2:
                    continue
                if rect.colliderect(target.get_body_rect()):
                    target.take_damage(
                        _calc_damage(self.damage, target, self.skill_num)
                    )
                    self._hit_counts[tid] = count + 1
                    if self._effect_frames:
                        self.effect_sprites.append(
                            SubProjectile(
                                target.position[0],
                                target.position[1],
                                {
                                    "width": self.effect_data["width"],
                                    "height": self.effect_data["height"],
                                    "frame_duration": self.effect_data[
                                        "frame_duration"
                                    ],
                                    "frames": self.effect_data["frames"],
                                    "path": self.effect_data["path"],
                                },
                            )
                        )
            else:
                if tid in self._hit_targets:
                    continue
                if rect.colliderect(target.get_body_rect()):
                    target.take_damage(
                        _calc_damage(self.damage, target, self.skill_num)
                    )
                    self._hit_targets.add(tid)
                    if self.stops:
                        if self.skill_num == 3:
                            sub = SubProjectile(self.x, self.y, self.sub_data)
                            sub.release_target = target
                            self.captured_target = target
                            self.sub_projectiles.append(sub)
                        else:
                            self._spawn_sub(self.x, self.y)
                        self.is_dead = True
                        return

        self.timer += dt
        if self.timer >= SKILL_SPEED:
            self.timer = 0
            self.current_frame += 1
            if self.current_frame >= self.total_frames:
                self.is_dead = True

        for sub in self.sub_projectiles:
            sub.update(dt)
        self.sub_projectiles = [s for s in self.sub_projectiles if not s.is_dead]
        for e in self.effect_sprites:
            e.update(dt)
        self.effect_sprites = [e for e in self.effect_sprites if not e.is_dead]

    def draw(self, surface):
        for sub in self.sub_projectiles:
            sub.draw(surface)
        for e in self.effect_sprites:
            e.draw(surface)

        if self.is_dead:
            return

        frames = self.frames_left if self.direction == "left" else self.frames_right
        frame_index = min(self.current_frame % self.frames_per_loop, len(frames) - 1)
        surface.blit(frames[frame_index], (int(self.x), int(self.y)))

        if TMP__GET_SURFACE_HITBOX_ATTACKS_:
            pyg.draw.rect(surface, (255, 165, 0), self.get_rect(), 2)

    def get_rect(self):
        return pyg.Rect(int(self.x), int(self.y), self.width, self.height)

    def _spawn_sub(self, impact_x, impact_y):
        if self.stops and self.sub_data is not None:
            self.sub_projectiles.append(
                SubProjectile(impact_x, impact_y, self.sub_data)
            )


class SubProjectile:
    def __init__(self, x, y, data, direction="right"):
        self.x = x
        self.y = y
        self.direction = direction
        raw_w = data["width"]
        raw_h = data["height"]
        self.width = int(raw_w * CHARACTER_SCALE)
        self.height = int(raw_h * CHARACTER_SCALE)
        self.frame_duration = data["frame_duration"]
        self.loop = data.get("loop", False)

        sheet = pyg.image.load(_resolve_path(data["path"])).convert_alpha()
        n = max(1, sheet.get_width() // raw_w)
        raw_frames = [sheet.subsurface((i * raw_w, 0, raw_w, raw_h)) for i in range(n)]
        if CHARACTER_SCALE != 1.0:
            raw_frames = [
                pyg.transform.scale(f, (self.width, self.height)) for f in raw_frames
            ]
        self.frames_right = raw_frames
        self.frames_left = [pyg.transform.flip(f, True, False) for f in raw_frames]
        # backward-compat alias
        self.frames = raw_frames
        self.total_frames = data["frames"]
        self.current_frame = 0
        self.timer = 0
        self.is_dead = False
        self.release_target = None

    def get_rect(self):
        return pyg.Rect(round(self.x), round(self.y), self.width, self.height)

    def draw(self, surface):
        if self.is_dead:
            return
        frames = self.frames_left if self.direction == "left" else self.frames_right
        frame_index = min(self.current_frame, len(frames) - 1)
        surface.blit(frames[frame_index], (round(self.x), round(self.y)))

        if TMP__GET_SURFACE_HITBOX_ATTACKS_:
            pyg.draw.rect(surface, (255, 255, 0), self.get_rect(), 2)

    def update(self, dt, target=None):
        if self.is_dead:
            return

        self.timer += dt
        if self.timer >= self.frame_duration:
            self.timer = 0
            self.current_frame += 1
            if self.current_frame >= self.total_frames:
                if self.loop:
                    self.current_frame = 0
                else:
                    self.is_dead = True


class Character4(Character):
    MAX_CHRGS = 4
    CHRG_INTRVL = 15000

    def __init__(self):
        self.chrgs = 0
        self.chrg_tmr = 0
        self.s1_phse = 1
        self.s1_htd = False
        self.grbd_tgt = None
        self.s2_vrt = 1
        self._s3_chrgs_spnt = 0

        self.frm_S1_1 = 0
        self.frm_S1_2 = 0
        self.frm_S1_3 = 0
        self.timr_S1_1 = 0
        self.timr_S1_2 = 0
        self.timr_S1_3 = 0

        self.frms_S1_1 = []
        self.frms_S1_1_left = []
        self.frms_S1_2 = []
        self.frms_S1_2_left = []
        self.frms_S1_3 = []
        self.frms_S1_3_left = []
        self.frms_S2_1 = []
        self.frms_S2_1_left = []
        self.frms_S2_2 = []
        self.frms_S2_2_left = []

        super().__init__(4)

    def _load_animations(self):
        super()._load_animations()

        s11w, s11h = self._dims("S1_1", "S1")
        s12w, s12h = self._dims("S1_2", "S1")
        s13w, s13h = self._dims("S1_3", "S1")
        s21w, s21h = self._dims("S2_1", "S2")
        s22w, s22h = self._dims("S2_2", "S2")

        s1_1 = self._load_sheet("S1-1-Sheet.png", s11w, s11h) or self._blank(
            w=s11w, h=s11h
        )
        s1_2 = self._load_sheet("S1-2-Sheet.png", s12w, s12h) or self._blank(
            w=s12w, h=s12h
        )
        s1_3 = self._load_sheet("S1-3-Sheet.png", s13w, s13h) or self._blank(
            w=s13w, h=s13h
        )
        s2_1 = self._load_sheet("S2-1-Sheet.png", s21w, s21h) or self._blank(
            w=s21w, h=s21h
        )
        s2_2 = self._load_sheet("S2-2-Sheet.png", s22w, s22h) or self._blank(
            w=s22w, h=s22h
        )

        self.frms_S1_1 = s1_1
        self.frms_S1_2 = s1_2
        self.frms_S1_3 = s1_3
        self.frms_S2_1 = s2_1
        self.frms_S2_2 = s2_2

        self.frms_S1_1_left = self._flip(s1_1)
        self.frms_S1_2_left = self._flip(s1_2)
        self.frms_S1_3_left = self._flip(s1_3)
        self.frms_S2_1_left = self._flip(s2_1)
        self.frms_S2_2_left = self._flip(s2_2)

        self.frames_S1 = s1_1
        self.frames_S1_left = self.frms_S1_1_left

    def use_skill(self, skill_num):
        if skill_num == 1 and not self.is_attacking_s1:
            snd = getattr(self, "_sounds", {}).get("s1")
            if snd:
                snd.play()
            self.is_attacking_s1 = True
            self.s1_phse = 1
            self.s1_htd = False
            self.grbd_tgt = None
            self.frm_S1_1 = 0
            self.frm_S1_2 = 0
            self.frm_S1_3 = 0
            self.timr_S1_1 = 0
            self.timr_S1_2 = 0
            self.timr_S1_3 = 0
            self._hit_this_swing = set()
            return True

        if skill_num == 2 and not self.is_attacking_s2 and not self.is_attacking_s1:
            snd = getattr(self, "_sounds", {}).get("s2")
            if snd:
                snd.play()
            self.s2_vrt = 1 if self.chrgs < 3 else 2
            if self.s2_vrt == 1:
                self.chrgs = min(self.MAX_CHRGS, self.chrgs + 1)
                self.frames_S2 = self.frms_S2_1
                self.frames_S2_left = self.frms_S2_1_left
            else:
                self.chrgs = max(0, self.chrgs - 2)
                self.frames_S2 = self.frms_S2_2
                self.frames_S2_left = self.frms_S2_2_left
            self.is_attacking_s2 = True
            self.frame_S2 = 0
            self.timer_S2 = 0
            self._hit_this_swing = set()
            return True

        if skill_num == 3 and not self.is_attacking_s3:
            snd = getattr(self, "_sounds", {}).get("s3")
            if snd:
                snd.play()
            self._s3_chrgs_spnt = self.chrgs
            self.chrgs = 0
            self.is_attacking_s3 = True
            self.frame_S3 = 0
            self.timer_S3 = 0
            self._hit_this_swing = set()
            return True

        return False

    def _handle_s1_update(self, dt):
        if self.s1_phse == 1:
            self.timr_S1_1 += dt
            if self.timr_S1_1 >= SKILL_SPEED:
                self.timr_S1_1 = 0
                self.frm_S1_1 += 1
                self.frame_S1 = self.frm_S1_1  # keep base frame_S1 in sync for hitbox
                if self.frm_S1_1 >= len(self.frms_S1_1):
                    if self.s1_htd:
                        self.s1_phse = 2
                        self.frm_S1_2 = 0
                        self.timr_S1_2 = 0
                    else:
                        self.s1_phse = 3
                        self.frm_S1_3 = 0
                        self.timr_S1_3 = 0

        elif self.s1_phse == 2:
            self.timr_S1_2 += dt
            if self.timr_S1_2 >= SKILL_SPEED:
                self.timr_S1_2 = 0
                self.frm_S1_2 += 1
                if self.frm_S1_2 >= len(self.frms_S1_2):
                    if self.grbd_tgt:
                        self.grbd_tgt.status.effects.pop("grabbed", None)
                        self.grbd_tgt = None
                    self.s1_phse = 3
                    self.frm_S1_3 = 0
                    self.timr_S1_3 = 0

        elif self.s1_phse == 3:
            self.timr_S1_3 += dt
            if self.timr_S1_3 >= SKILL_SPEED:
                self.timr_S1_3 = 0
                self.frm_S1_3 += 1
                if self.frm_S1_3 >= len(self.frms_S1_3):
                    self.is_attacking_s1 = False
                    self.s1_phse = 1
                    self._hit_this_swing = set()

    def update_animation(self, dt, is_moving):
        self.chrg_tmr += dt
        if self.chrg_tmr >= self.CHRG_INTRVL:
            self.chrg_tmr = 0
            self.chrgs = min(self.MAX_CHRGS, self.chrgs + 1)
        if self.status.is_stunned:
            is_moving = False
        super().update_animation(dt, is_moving)

    def check_hits(self, targets):
        if self.is_attacking_s1:
            if self.s1_phse == 1:
                hbx = self.get_attack_hitbox()
                if hbx is not None:
                    dmg = HITBOX_DATA.get(self.char_num, {}).get(1, _DEFAULT_HITBOX)[
                        "damage"
                    ]
                    for tgt in targets:
                        if tgt is self or tgt.is_dead:
                            continue
                        if id(tgt) in self._hit_this_swing:
                            continue
                        if hbx.colliderect(tgt.get_body_rect()):
                            if hasattr(tgt, "notify_incoming_hit"):
                                tgt.notify_incoming_hit(self.position, self)
                            tgt.take_damage(_calc_damage(dmg, tgt, 1))
                            self._hit_this_swing.add(id(tgt))
                            self.s1_htd = True
                            self.chrgs = min(self.MAX_CHRGS, self.chrgs + 2)
                            tgt.status.apply_grabbed(self)
                            self.grbd_tgt = tgt
                    return
            return

        if self.is_attacking_s2:
            hbx = self.get_attack_hitbox()
            if hbx is None:
                return
            base_dmg = HITBOX_DATA.get(self.char_num, {}).get(2, _DEFAULT_HITBOX)[
                "damage"
            ]
            dmg = base_dmg if self.s2_vrt == 2 else max(1, base_dmg // 2)
            for tgt in targets:
                if tgt is self or tgt.is_dead:
                    continue
                if id(tgt) in self._hit_this_swing:
                    continue
                if hbx.colliderect(tgt.get_body_rect()):
                    tgt.take_damage(_calc_damage(dmg, tgt, 2))
                    if self.s2_vrt == 2:
                        tgt.status.apply_stun(2000)
                    self._hit_this_swing.add(id(tgt))
            return

        if self.is_attacking_s3:
            hbx = self.get_attack_hitbox()
            if hbx is None:
                return
            dmg = HITBOX_DATA.get(self.char_num, {}).get(3, _DEFAULT_HITBOX)["damage"]
            stun_dur = max(1000, self._s3_chrgs_spnt * 2000)
            for tgt in targets:
                if tgt is self or tgt.is_dead:
                    continue
                if id(tgt) in self._hit_this_swing:
                    continue
                if hbx.colliderect(tgt.get_body_rect()):
                    tgt.take_damage(_calc_damage(dmg, tgt, 3))
                    tgt.status.apply_burn()
                    tgt.status.apply_stun(stun_dur)
                    self._hit_this_swing.add(id(tgt))

    def get_attack_hitbox(self):
        if self.is_attacking_s1:
            if self.s1_phse in (2, 3):
                return None
        return super().get_attack_hitbox()

    def get_current_sprite(self):
        if self.is_hidden:
            return None

        lft = self.direction == "left"

        if self.is_dead:
            return self.frames_DEAD[-1] if self.frames_DEAD else None

        if self.is_hurt:
            frms = self.frames_HURT_left if lft else self.frames_HURT
            if frms:
                return frms[min(self.frame_HURT, len(frms) - 1)]

        if self.is_attacking_s1:
            if self.s1_phse == 1:
                frms = self.frms_S1_1_left if lft else self.frms_S1_1
                idx = self.frm_S1_1
            elif self.s1_phse == 2:
                frms = self.frms_S1_2_left if lft else self.frms_S1_2
                idx = self.frm_S1_2
            else:
                frms = self.frms_S1_3_left if lft else self.frms_S1_3
                idx = self.frm_S1_3
            if frms:
                return frms[min(idx, len(frms) - 1)]
            return None

        if self.is_attacking_s2:
            frms = (
                (self.frms_S2_2_left if lft else self.frms_S2_2)
                if self.s2_vrt == 2
                else (self.frms_S2_1_left if lft else self.frms_S2_1)
            )
            if frms:
                return frms[min(self.frame_S2, len(frms) - 1)]
            return None

        if self.is_attacking_s3:
            frms = self.frames_S3_left if lft else self.frames_S3
            if frms:
                return frms[min(self.frame_S3, len(frms) - 1)]
            return None

        if self.is_moving:
            frms = self.frames_MOVE_left if lft else self.frames_MOVE
            if frms:
                return frms[self.frame_MOVE % len(frms)]

        frms = self.frames_IDLE_left if lft else self.frames_IDLE
        if frms:
            return frms[self.frame_IDLE % len(frms)]
        return None

    def _current_skill_frame(self):
        if self.is_attacking_s1:
            if self.s1_phse == 1:
                return self.frm_S1_1
            if self.s1_phse == 2:
                return self.frm_S1_2
            return self.frm_S1_3
        return super()._current_skill_frame()

    def get_network_state(self):
        return {
            "s1_phse": self.s1_phse,
            "frm_s1_1": self.frm_S1_1,
            "frm_s1_2": self.frm_S1_2,
            "frm_s1_3": self.frm_S1_3,
        }

    def apply_extra_network_state(self, extra):
        if "s1_phse" in extra:
            self.s1_phse = int(extra["s1_phse"])
        if "frm_s1_1" in extra:
            self.frm_S1_1 = int(extra["frm_s1_1"])
        if "frm_s1_2" in extra:
            self.frm_S1_2 = int(extra["frm_s1_2"])
        if "frm_s1_3" in extra:
            self.frm_S1_3 = int(extra["frm_s1_3"])

    def get_anim_state(self):
        if self.is_attacking_s1:
            return f"s1_{self.s1_phse}"
        if self.is_attacking_s2:
            return f"s2_{self.s2_vrt}"
        return super().get_anim_state()


class Character5(Character):
    MAX_CNS = 4

    def __init__(self):
        self.wtr_cns = 4
        self.sda_cns = 4
        self._cns_ctx = "water"
        self._pending_s2_on_s1 = None

        super().__init__(5)

    def use_skill(self, skill_num):
        if skill_num == 1:
            if self.is_attacking_s1 or self.is_attacking_s2:
                return False
            snd = getattr(self, "_sounds", {}).get("s1")
            if snd:
                snd.play()
            if self.wtr_cns > 0:
                self._cns_ctx = "water"
                self.is_attacking_s1 = True
                self.frame_S1 = 0
                self.timer_S1 = 0
                self._hit_this_swing = set()
                proj_data = PROJECTILES_INFOS.get(self.char_num, {}).get("s1")
                if proj_data:
                    if proj_data.get("spawn_frame", 0) == 0:
                        p = Projectile(
                            self.char_num, 1, self.position, self.direction, proj_data
                        )
                        self.projectiles.append(p)
                        self._just_spawned_projectiles.append((1, p))
                    else:
                        self._pending_projectiles[1] = proj_data
                self.wtr_cns -= 1
            else:
                self._cns_ctx = "fallback"
                self.is_attacking_s2 = True
                self.frame_S2 = 0
                self.timer_S2 = 0
                self._hit_this_swing = set()
            return True

        if skill_num == 2:
            if self.is_attacking_s1 or self.is_attacking_s2:
                return False
            snd = getattr(self, "_sounds", {}).get("s2")
            if snd:
                snd.play()
            if self.sda_cns > 0:
                self._cns_ctx = "soda"
                self.is_attacking_s1 = True
                self.frame_S1 = 0
                self.timer_S1 = 0
                self._hit_this_swing = set()
                proj_data = PROJECTILES_INFOS.get(self.char_num, {}).get("s2")
                if proj_data:
                    self._pending_s2_on_s1 = proj_data
                    if proj_data.get("spawn_frame", 0) == 0:
                        p = Projectile(
                            self.char_num, 2, self.position, self.direction, proj_data
                        )
                        self.projectiles.append(p)
                        self._just_spawned_projectiles.append((2, p))
                    else:
                        self._pending_projectiles[2] = proj_data
                self.sda_cns -= 1
            else:
                self._cns_ctx = "fallback"
                self.is_attacking_s2 = True
                self.frame_S2 = 0
                self.timer_S2 = 0
                self._hit_this_swing = set()
            return True

        if skill_num == 3 and not self.is_attacking_s3:
            snd = getattr(self, "_sounds", {}).get("s3")
            if snd:
                snd.play()
            self.is_attacking_s3 = True
            self.frame_S3 = 0
            self.timer_S3 = 0
            self.wtr_cns = self.MAX_CNS
            self.sda_cns = self.MAX_CNS
            return True

        return False

    def check_hits(self, targets):
        if self.is_attacking_s3:
            return
        if self.is_attacking_s2 and self._cns_ctx == "fallback":
            if self.frame_S2 <= 9 or self.frame_S2 > 14:
                return
            data = HITBOX_DATA[5][2]
            px, py = data["offset"]
            sw, sh = data["size"]
            px = int(px * CHARACTER_SCALE)
            py = int(py * CHARACTER_SCALE)
            sw = int(sw * CHARACTER_SCALE)
            sh = int(sh * CHARACTER_SCALE)
            x, y = self.position
            if self.direction == "left":
                px = SCALED_FRAME_SIZE - px - sw
            hbx = pyg.Rect(x + px, y + py, sw, sh)
            dmg = data["damage"]
            dmg_hited = False
            for tgt in targets:
                if tgt is self or tgt.is_dead:
                    continue
                if id(tgt) in self._hit_this_swing:
                    continue
                if hbx.colliderect(tgt.get_body_rect()) and not dmg_hited:
                    tgt.take_damage(_calc_damage(dmg, tgt, 2))
                    dmg_hited = True
                    self._hit_this_swing.add(id(tgt))
            return
        if self.is_attacking_s2 and self._cns_ctx == "soda":
            return
        Character.check_hits(self, targets)

    def _apply_status_on_hit(self, target, skill):
        if skill == 1:
            if self._cns_ctx == "water":
                target.status.apply_wet()
            elif self._cns_ctx == "soda":
                target.status.apply_oiled()
        elif skill == 2:
            target.status.apply_pushed(self.direction)

    def _handle_s1_update(self, dt):
        self.timer_S1 += dt
        if self.timer_S1 >= SKILL_SPEED:
            self.timer_S1 = 0
            self.frame_S1 += 1
            if hasattr(self, "_pending_s2_on_s1") and self._pending_s2_on_s1:
                proj_data = self._pending_s2_on_s1
                if self.frame_S1 >= proj_data.get("spawn_frame", 0):
                    p = Projectile(
                        self.char_num, 2, self.position, self.direction, proj_data
                    )
                    self.projectiles.append(p)
                    self._just_spawned_projectiles.append((2, p))
                    self._pending_s2_on_s1 = None
            else:
                self._maybe_spawn_projectile(1)
            if self.frame_S1 >= len(self.frames_S1):
                self.frame_S1 = 0
                self.is_attacking_s1 = False
                self._hit_this_swing = set()
                self._pending_projectiles.pop(1, None)
                if hasattr(self, "_pending_s2_on_s1"):
                    self._pending_s2_on_s1 = None
