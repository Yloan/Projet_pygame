import pygame as pyg

from ui.console import print_debug
from utils.paths import get_asset_path
from utils.status import StatusManager

FRAME_SIZE = 40
IDLE_SPEED = 100
MOVE_SPEED = 150
HURT_SPEED = 80
SKILL_SPEED = 100

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

TMP__GET_SURFACE_HITBOX_ATTACKS_ = False
DIMENS = {
    2: {
        "MOVE": (FRAME_SIZE, FRAME_SIZE),
        "S1": (168, 40),
        "S2": (112, 96),
        "S3": (200, 40),
        "S3_2": (176, 64),
    },
    3: {
        "MOVE": (60, 60),
        "S1": (120, 60),
        "S2": (80, 60),
        "S3": (120, 60),
    },
    4: {
        "MOVE": (64, 40),
        "S1": (75, 40),
        "S2": (160, 91),
        "S3": (176, 80),
    },
    5: {
        "S2": (122, 84),
    },
}

# Hitbox d'attaque par personnage et par skill
# "offset" : (x, y) par rapport a la position du perso (direction droite, c adapte quand c a gauche)
# "size"   : (largeur, hauteur) de la hitbox
# "damage" : degats infliges au contact
HITBOX_DATA = {
    1: {
        1: {"offset": (38, -5), "size": (44, 32), "damage": 15},
        2: {"offset": (25, -22), "size": (58, 58), "damage": 25},
        3: {"offset": (48, -12), "size": (75, 42), "damage": 40},
    },
    2: {
        1: {"offset": (0, 0), "size": (0, 0), "damage": 12},
        2: {"offset": (0, 0), "size": (0, 0), "damage": 22},
        3: {"offset": (0, 0), "size": (0, 0), "damage": 35},
    },
    3: {
        1: {"offset": (85, 25), "size": (30, 20), "damage": 18},
        2: {"offset": (45, 20), "size": (20, 40), "damage": 28},
        3: {"offset": (20, 8), "size": (90, 45), "damage": 45},
    },
    4: {
        1: {"offset": (40, -5), "size": (42, 30), "damage": 10},
        2: {"offset": (20, -30), "size": (80, 70), "damage": 30},
        3: {"offset": (50, -20), "size": (100, 60), "damage": 50},
    },
    5: {
        1: {"offset": (0, 0), "size": (0, 0), "damage": 12},
        2: {"offset": (18, 37), "size": (80, 45), "damage": 24},
        3: {"offset": (0, 0), "size": (0, 0), "damage": 0},
    },
    6: {
        1: {"offset": (36, -8), "size": (38, 34), "damage": 14},
        2: {"offset": (24, -22), "size": (55, 55), "damage": 22},
        3: {"offset": (44, -12), "size": (72, 44), "damage": 36},
    },
}
_DEFAULT_HITBOX = {"offset": (36, -8), "size": (40, 36), "damage": 10}


# All the finfos ab the character's projectiles if there had some
PROJECTILES_INFOS = {
    5: {
        "s1": {
            "path": "assets/sprites/Character-5/6-PROJECTILE-1-1-Sheet.png",
            "frames": 4,
            "loops": 3,
            "stops": True,
            "speed": 5,
            "width": 20,
            "height": 20,
            "sub": {
                "path": "assets/sprites/Character-5/6-PROJECTILE-1-2-Sheet.png",
                "frames": 1,
                "frame_duration": 150,
                "width": 20,
                "height": 20,
            },
        },
        "s2": {
            "path": "assets/sprites/Character-5/6-PROJECTILE-2-1-Sheet.png",
            "frames": 4,
            "loops": 2,
            "stops": True,
            "speed": 5,
            "width": 20,
            "height": 20,
            "sub": {
                "path": "assets/sprites/Character-5/6-PROJECTILE-2-2-Sheet.png",
                "frames": 1,
                "frame_duration": 150,
                "width": 20,
                "height": 20,
            },
        },
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
        self.frames_S3_2 = []
        self.frames_S3_2_left = []

    def _dims(self, anim):
        char_dimensi = DIMENS.get(self.char_num, {})
        if anim in char_dimensi:
            return char_dimensi[anim]
        return (FRAME_SIZE, FRAME_SIZE)

    def _blank(self, color=None, w=None, h=None):
        w = w or FRAME_SIZE
        h = h or FRAME_SIZE
        surf = pyg.Surface((w, h))
        surf.fill(color if color else self.color)
        return [surf]

    def _load_sheet(self, filename, w=FRAME_SIZE, h=FRAME_SIZE):
        try:
            path = get_asset_path("sprites", f"Character-{self.char_num}", filename)
            # import os  # tmp

            # print_debug(f"Chargement : {path} | existe : {os.path.exists(path)}")
            # sheet = pyg.image.load(path).convert_alpha()
            # print(f"[DEBUG] sheet size: {sheet.get_size()} | frame size: {w}x{h}")
            sheet = pyg.image.load(path).convert_alpha()
            n = max(1, sheet.get_width() // w)
            frames = []
            for i in range(n):
                if (i + 1) * w <= sheet.get_width() and h <= sheet.get_height():
                    frames.append(sheet.subsurface((i * w, 0, w, h)))
            return frames if frames else None
        except (FileNotFoundError, pyg.error):
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
            self._load_sheet("S3-1-Sheet.png", s3w, s3h)
            or self._load_sheet("S3-Sheet.png", s3w, s3h)
            or self._blank(w=s3w, h=s3h)
        )

        raw_idle = self._load_sheet("IDLE-Sheet.png")
        self.has_sprites = raw_idle is not None

        idle = raw_idle or self._blank()
        move = self._load_sheet("MOVE-Sheet.png", mw, mh) or self._blank(w=mw, h=mh)
        hurt = self._load_sheet("HURT-Sheet.png") or idle
        dead = self._load_sheet("DEAD-Sheet.png") or self._blank((80, 0, 0))
        s1 = self._load_sheet("S1-Sheet.png", s1w, s1h) or self._blank(w=s1w, h=s1h)
        s2 = self._load_sheet("S2-Sheet.png", s2w, s2h) or self._blank(w=s2w, h=s2h)

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

    def move(self, direction):
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

    def take_damage(self, amount):
        if self.status.is_disabled:
            return

        self.health = max(0, self.health - amount)
        if self.health == 0:
            self.is_dead = True
        else:
            self.is_hurt = True
            self.frame_HURT = 0
            self.timer_HURT = 0

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

        if skill_num == 1 and not self.is_attacking_s1:
            self.is_attacking_s1 = True
            self.frame_S1 = 0
            self.timer_S1 = 0
            self._hit_this_swing = set()
            proj_data = PROJECTILES_INFOS.get(self.char_num, {}).get(skill_key)
            if proj_data:
                self.projectiles.append(
                    Projectile(
                        self.char_num,
                        skill_num,
                        self.position,
                        self.direction,
                        proj_data,
                    )
                )
            return True

        if skill_num == 2 and not self.is_attacking_s2:
            self.is_attacking_s2 = True
            self.frame_S2 = 0
            self.timer_S2 = 0
            self._hit_this_swing = set()
            proj_data = PROJECTILES_INFOS.get(self.char_num, {}).get(skill_key)
            if proj_data:
                self.projectiles.append(
                    Projectile(
                        self.char_num,
                        skill_num,
                        self.position,
                        self.direction,
                        proj_data,
                    )
                )
            return True

        if skill_num == 3 and not self.is_attacking_s3:
            self.is_attacking_s3 = True
            self.frame_S3 = 0
            self.timer_S3 = 0
            self._hit_this_swing = set()
            proj_data = PROJECTILES_INFOS.get(self.char_num, {}).get(skill_key)
            if proj_data:
                self.projectiles.append(
                    Projectile(
                        self.char_num,
                        skill_num,
                        self.position,
                        self.direction,
                        proj_data,
                    )
                )
            return True

        return False

    def update_projectiles(self, dt, targets):
        for p in self.projectiles:
            p.update(dt, targets)
        self.projectiles = [p for p in self.projectiles if not p.is_dead]

    def draw_projectiles(self, surface):
        for p in self.projectiles:
            p.draw(surface)

    def update_animation(self, dt, is_moving):

        if hasattr(self, "bubble_effect") and self.bubble_effect:
            self.bubble_effect.update(dt)
            if not self.status.is_disabled:
                self.bubble_effect = None

        self.status.update(dt)
        if self.status.is_disabled:
            is_moving = False
        push_delta = self.status.get_push_delta(dt)
        if push_delta != 0:
            x, y = self.position
            self.position = (x + push_delta, y)

        self.is_moving = is_moving

        if self.is_attacking_s1:
            self.timer_S1 += dt
            if self.timer_S1 >= SKILL_SPEED:
                self.timer_S1 = 0
                self.frame_S1 += 1
                if self.frame_S1 >= len(self.frames_S1):
                    self.frame_S1 = 0
                    self.is_attacking_s1 = False
                    self._hit_this_swing = set()

        if self.is_attacking_s2:
            self.timer_S2 += dt
            if self.timer_S2 >= SKILL_SPEED:
                self.timer_S2 = 0
                self.frame_S2 += 1
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
                    if self.frame_S3_2 >= len(self.frames_S3_2):
                        self.frame_S3_2 = 0
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
            return None  # in the buubble
        left = self.direction == "left"

        if self.is_dead:
            return self.frames_DEAD[-1]

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
            if self.s3_hit:
                frames = self.frames_S3_2_left if left else self.frames_S3_2
                return frames[min(self.frame_S3_2, len(frames) - 1)]
            frames = self.frames_S3_left if left else self.frames_S3
            return frames[min(self.frame_S3, len(frames) - 1)]

        if self.is_moving:
            frames = self.frames_MOVE_left if left else self.frames_MOVE
            return frames[self.frame_MOVE]

        frames = self.frames_IDLE_left if left else self.frames_IDLE
        return frames[self.frame_IDLE]

    def get_body_rect(self):
        x, y = self.position
        offset_x = int(self.status.bubble_offset)
        return pyg.Rect(x + offset_x, y, FRAME_SIZE, FRAME_SIZE)

    def _active_skill(self):
        if self.is_attacking_s1:
            return 1  # skill 1
        if self.is_attacking_s2:
            return 2  # 2
        if self.is_attacking_s3:
            return 3  # and 3
        return None  # No skill activated

    def get_attack_hitbox(self):
        skill = self._active_skill()
        if skill is None:
            return None

        data = HITBOX_DATA.get(self.char_num, {}).get(skill, _DEFAULT_HITBOX)
        px, py = data["offset"]
        sw, sh = data["size"]
        x, y = self.position

        if self.direction == "left":
            width_frame = self.get_current_sprite().get_width()
            px = -(px + sw) + width_frame

        return pyg.Rect(x + px, y + py, sw, sh)

    def check_hits(self, targets):
        skill = self._active_skill()
        if skill is None:
            return

        hitbox = self.get_attack_hitbox()
        dmg = HITBOX_DATA.get(self.char_num, {}).get(skill, _DEFAULT_HITBOX)["damage"]

        for target in targets:
            if target is self or target.is_dead:
                continue

            if skill == 3 and not self.s3_hit:
                if hitbox.colliderect(target.get_body_rect()):
                    target.take_damage(dmg)
                    self._hit_this_swing.add(id(target))
                    self.s3_hit = True
                    self.frame_S3_2 = 0
                    self.timer_S3_2 = 0
                    self._apply_status_on_hit(target, skill)
                    return

            tid = id(target)
            if tid in self._hit_this_swing:
                continue
            if hitbox.colliderect(target.get_body_rect()):
                target.take_damage(dmg)
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

    def apply_network_state(self, state):
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
        self.frame_IDLE = int(idx.get("idle", self.frame_IDLE))
        self.frame_MOVE = int(idx.get("move", self.frame_MOVE))
        self.frame_HURT = int(idx.get("hurt", self.frame_HURT))
        self.frame_S1 = int(idx.get("skill1", self.frame_S1))
        self.frame_S2 = int(idx.get("skill2", self.frame_S2))
        self.frame_S3 = int(idx.get("skill3", self.frame_S3))

    def get_effect_sprite(self):
        return None

    def _apply_status_on_hit(self, target, skill):
        if self.char_num == 2:
            if skill == 1:
                target.status.apply_wet()
                effect_data = {
                    "path": "assets/sprites/Character-2/effect-2-S1-Sheet.png",
                    "frames": 2,
                    "frame_duration": 150,
                    "width": 160,
                    "height": 48,
                }
                self.projectiles.append(
                    SubProjectile(target.position[0], target.position[1], effect_data)
                )
            elif skill == 2:
                target.status.apply_pushed(self.direction)
            elif skill == 3:
                target.status.apply_wet()
                target.status.apply_disabled(self.direction)
                target.is_hidden = True
                effect_data = {
                    "path": "assets/sprites/Character-2/effect-2-S3-Sheet.png",
                    "frames": 4,
                    "frame_duration": DISABLED_DURATION // 4,
                    "width": 128,
                    "height": 32,
                }
                target.bubble_effect = SubProjectile(
                    target.position[0], target.position[1], effect_data
                )


class Furnace(Character):
    def __init__(self):
        super().__init__(1)


class Water(Character):
    def __init__(self):
        super().__init__(2)


class Projectile:
    def __init__(self, char_num, skill_num, origin_pos, direction, data):
        self.x, self.y = float(origin_pos[0]), float(origin_pos[1])
        self.direction = direction
        self.speed = data["speed"]
        self.stops = data["stops"]
        self.width = data["width"]
        self.height = data["height"]
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

        sheet = pyg.image.load(data["path"]).convert_alpha()
        n = max(1, sheet.get_width() // self.width)
        raw_frames = [
            sheet.subsurface((i * self.width, 0, self.width, self.height))
            for i in range(n - 1, -1, -1)
            # for i in range(n)
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
            w, h = self.effect_data["width"], self.effect_data["height"]
            n = max(1, sheet.get_width() // w)
            self._effect_frames = [sheet.subsurface((i * w, 0, w, h)) for i in range(n)]
        else:
            self._effect_frames = []

    def update(self, dt, targets):
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
                    offset = 40 if self.direction == "right" else -40
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
                    target.take_damage(self.damage)
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
                    target.take_damage(self.damage)
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
    def __init__(self, x, y, data):
        self.x = x
        self.y = y
        self.width = data["width"]
        self.height = data["height"]
        self.frame_duration = data["frame_duration"]

        sheet = pyg.image.load(data["path"]).convert_alpha()
        n = max(1, sheet.get_width() // self.width)
        self.frames = [
            sheet.subsurface((i * self.width, 0, self.width, self.height))
            for i in range(n)
        ]
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
        frame_index = min(self.current_frame, len(self.frames) - 1)
        surface.blit(self.frames[frame_index], (round(self.x), round(self.y)))

        if TMP__GET_SURFACE_HITBOX_ATTACKS_:
            pyg.draw.rect(surface, (255, 255, 0), self.get_rect(), 2)

    def update(self, dt):
        if self.is_dead:
            return

        self.timer += dt
        if self.timer >= self.frame_duration:
            self.timer = 0
            self.current_frame += 1
            if self.current_frame >= self.total_frames:
                self.is_dead = True
