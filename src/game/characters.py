# import pygame as pyg

# from utils.paths import get_asset_path

# FRAME_SIZE = 40
# IDLE_SPEED = 100
# MOVE_SPEED = 150
# HURT_SPEED = 80
# SKILL_SPEED = 100

# CHAR_STATS = {
#     1: {"speed": 3, "health": 100, "color": (220, 80, 20)},
#     2: {"speed": 2, "health": 100, "color": (20, 120, 220)},
#     3: {"speed": 2, "health": 100, "color": (200, 200, 50)},
#     4: {"speed": 4, "health": 80, "color": (255, 230, 0)},
#     5: {"speed": 2, "health": 100, "color": (100, 200, 100)},
#     6: {"speed": 2, "health": 100, "color": (200, 130, 50)},
#     7: {"speed": 2, "health": 100, "color": (150, 150, 150)},
#     8: {"speed": 3, "health": 80, "color": (180, 100, 255)},
#     9: {"speed": 2, "health": 100, "color": (100, 200, 50)},
# }
# DEFAULT_STATS = {"speed": 2, "health": 100, "color": (128, 128, 128)}

# SPECIAL_DIMS = {
#     3: {
#         "MOVE": (60, 60),
#         "S1": (120, 60),
#         "S2": (80, 60),
#         "S3": (120, 60),
#     },
#     4: {
#         "MOVE": (64, 40),
#         "S1": (75, 40),
#         "S2": (160, 91),
#         "S3": (176, 80),
#     },
#     5: {
#         "S2": (122, 84),
#     },
# }


# class Character:
#     def __init__(self, char_num):
#         stats = CHAR_STATS.get(char_num, DEFAULT_STATS)
#         self.char_num = char_num
#         self.health = stats["health"]
#         self.max_health = stats["health"]
#         self.speed = stats["speed"]
#         self.color = stats["color"]

#         self.position = (400, 400)
#         self.direction = "right"

#         self._load_animations()

#         self.frame_IDLE = 0
#         self.frame_MOVE = 0
#         self.frame_HURT = 0
#         self.frame_S1 = 0
#         self.frame_S2 = 0
#         self.frame_S3 = 0

#         self.timer_IDLE = 0
#         self.timer_MOVE = 0
#         self.timer_HURT = 0
#         self.timer_S1 = 0
#         self.timer_S2 = 0
#         self.timer_S3 = 0

#         self.is_moving = False
#         self.is_attacking_s1 = False
#         self.is_attacking_s2 = False
#         self.is_attacking_s3 = False
#         self.is_hurt = False
#         self.is_dead = False

#     def _dims(self, anim):
#         # return a tuple for the dimensions which is not 40 * 40, if there isn't "special dimension"
#         # then this return (40, 40)
#         return SPECIAL_DIMS.get(self.char_num, {}).get(anim, (FRAME_SIZE, FRAME_SIZE))

#     def _blank(self, color=None, w=None, h=None):
#         w = w or FRAME_SIZE
#         h = h or FRAME_SIZE
#         surf = pyg.Surface((w, h))
#         surf.fill(color if color else self.color)
#         return [surf]

#     def _load_sheet(self, filename, w=FRAME_SIZE, h=FRAME_SIZE):
#         try:
#             path = get_asset_path("sprites", f"Character-{self.char_num}", filename)
#             sheet = pyg.image.load(path).convert_alpha()
#             n = max(1, sheet.get_width() // w)
#             return [sheet.subsurface((i * w, 0, w, h)) for i in range(n)]
#         except (FileNotFoundError, pyg.error):
#             return None

#     @staticmethod
#     def _flip(frames):
#         return [pyg.transform.flip(f, True, False) for f in frames]

#     def _load_animations(self):
#         mw, mh = self._dims("MOVE")
#         s1w, s1h = self._dims("S1")
#         s2w, s2h = self._dims("S2")
#         s3w, s3h = self._dims("S3")

#         raw_idle = self._load_sheet("IDLE-Sheet.png")
#         self.has_sprites = raw_idle is not None

#         idle = raw_idle or self._blank()
#         move = self._load_sheet("MOVE-Sheet.png", mw, mh) or self._blank(w=mw, h=mh)
#         hurt = self._load_sheet("HURT-Sheet.png") or idle
#         dead = self._load_sheet("DEAD-Sheet.png") or self._blank((80, 0, 0))
#         s1 = self._load_sheet("S1-Sheet.png", s1w, s1h) or self._blank(w=s1w, h=s1h)
#         s2 = self._load_sheet("S2-Sheet.png", s2w, s2h) or self._blank(w=s2w, h=s2h)
#         s3 = self._load_sheet("S3-1-Sheet.png", s3w, s3h) or self._blank(w=s3w, h=s3h)

#         self.frames_IDLE = idle
#         self.frames_MOVE = move
#         self.frames_HURT = hurt
#         self.frames_DEAD = dead
#         self.frames_S1 = s1
#         self.frames_S2 = s2
#         self.frames_S3 = s3

#         self.frames_IDLE_left = self._flip(idle)
#         self.frames_MOVE_left = self._flip(move)
#         self.frames_HURT_left = self._flip(hurt)
#         self.frames_S1_left = self._flip(s1)
#         self.frames_S2_left = self._flip(s2)
#         self.frames_S3_left = self._flip(s3)

#     def move(self, direction):
#         x, y = self.position
#         if direction == "up":
#             self.position = (x, y - self.speed)
#         elif direction == "down":
#             self.position = (x, y + self.speed)
#         elif direction == "left":
#             self.position = (x - self.speed, y)
#             self.direction = "left"
#         elif direction == "right":
#             self.position = (x + self.speed, y)
#             self.direction = "right"

#     def take_damage(self, amount):
#         self.health = max(0, self.health - amount)
#         if self.health == 0:
#             self.is_dead = True
#         else:
#             self.is_hurt = True
#             self.frame_HURT = 0
#             self.timer_HURT = 0

#     def heal(self, amount):
#         self.health = min(self.max_health, self.health + amount)

#     def get_status(self):
#         return {
#             "char_num": self.char_num,
#             "health": self.health,
#             "position": self.position,
#         }

#     def use_skill(self, skill_num):
#         if skill_num == 1 and not self.is_attacking_s1:
#             self.is_attacking_s1 = True
#             self.frame_S1 = 0
#             self.timer_S1 = 0
#             return True
#         if skill_num == 2 and not self.is_attacking_s2:
#             self.is_attacking_s2 = True
#             self.frame_S2 = 0
#             self.timer_S2 = 0
#             return True
#         if skill_num == 3 and not self.is_attacking_s3:
#             self.is_attacking_s3 = True
#             self.frame_S3 = 0
#             self.timer_S3 = 0
#             return True
#         return False

#     def update_animation(self, dt, is_moving):
#         self.is_moving = is_moving

#         if self.is_attacking_s1:
#             self.timer_S1 += dt
#             if self.timer_S1 >= SKILL_SPEED:
#                 self.timer_S1 = 0
#                 self.frame_S1 += 1
#                 if self.frame_S1 >= len(self.frames_S1):
#                     self.frame_S1 = 0
#                     self.is_attacking_s1 = False

#         if self.is_attacking_s2:
#             self.timer_S2 += dt
#             if self.timer_S2 >= SKILL_SPEED:
#                 self.timer_S2 = 0
#                 self.frame_S2 += 1
#                 if self.frame_S2 >= len(self.frames_S2):
#                     self.frame_S2 = 0
#                     self.is_attacking_s2 = False

#         if self.is_attacking_s3:
#             self.timer_S3 += dt
#             if self.timer_S3 >= SKILL_SPEED:
#                 self.timer_S3 = 0
#                 self.frame_S3 += 1
#                 if self.frame_S3 >= len(self.frames_S3):
#                     self.frame_S3 = 0
#                     self.is_attacking_s3 = False

#         if self.is_hurt:
#             self.timer_HURT += dt
#             if self.timer_HURT >= HURT_SPEED:
#                 self.timer_HURT = 0
#                 self.frame_HURT += 1
#                 if self.frame_HURT >= len(self.frames_HURT):
#                     self.frame_HURT = 0
#                     self.is_hurt = False

#         if is_moving:
#             self.timer_MOVE += dt
#             if self.timer_MOVE >= MOVE_SPEED:
#                 self.timer_MOVE = 0
#                 self.frame_MOVE = (self.frame_MOVE + 1) % len(self.frames_MOVE)
#         else:
#             self.timer_IDLE += dt
#             if self.timer_IDLE >= IDLE_SPEED:
#                 self.timer_IDLE = 0
#                 self.frame_IDLE = (self.frame_IDLE + 1) % len(self.frames_IDLE)

#     def get_current_sprite(self):
#         left = self.direction == "left"

#         if self.is_dead:
#             return self.frames_DEAD[-1]

#         if self.is_hurt:
#             frames = self.frames_HURT_left if left else self.frames_HURT
#             return frames[min(self.frame_HURT, len(frames) - 1)]

#         if self.is_attacking_s1:
#             frames = self.frames_S1_left if left else self.frames_S1
#             return frames[min(self.frame_S1, len(frames) - 1)]

#         if self.is_attacking_s2:
#             frames = self.frames_S2_left if left else self.frames_S2
#             return frames[min(self.frame_S2, len(frames) - 1)]

#         if self.is_attacking_s3:
#             frames = self.frames_S3_left if left else self.frames_S3
#             return frames[min(self.frame_S3, len(frames) - 1)]

#         if self.is_moving:
#             frames = self.frames_MOVE_left if left else self.frames_MOVE
#             return frames[self.frame_MOVE]

#         frames = self.frames_IDLE_left if left else self.frames_IDLE
#         return frames[self.frame_IDLE]

#     def apply_network_state(self, state):
#         if "pos" in state:
#             self.position = tuple(state["pos"])
#         if "direction" in state:
#             self.direction = state["direction"]
#         if "health" in state:
#             self.health = int(state["health"])
#             self.is_dead = self.health <= 0
#         if "is_moving" in state:
#             self.is_moving = bool(state["is_moving"])
#         if "is_hurt" in state:
#             self.is_hurt = bool(state["is_hurt"])

#         atk = state.get("is_attacking", {})
#         self.is_attacking_s1 = bool(atk.get("1", False))
#         self.is_attacking_s2 = bool(atk.get("2", False))
#         self.is_attacking_s3 = bool(atk.get("3", False))

#         idx = state.get("anim_indices", {})
#         self.frame_IDLE = int(idx.get("idle", self.frame_IDLE))
#         self.frame_MOVE = int(idx.get("move", self.frame_MOVE))
#         self.frame_HURT = int(idx.get("hurt", self.frame_HURT))
#         self.frame_S1 = int(idx.get("skill1", self.frame_S1))
#         self.frame_S2 = int(idx.get("skill2", self.frame_S2))
#         self.frame_S3 = int(idx.get("skill3", self.frame_S3))

#     def get_effect_sprite(self):
#         return None

#     def update(self):
#         pass


# class Furnace(Character):
#     def __init__(self):
#         super().__init__(1)


# class Water(Character):
#     def __init__(self):
#         super().__init__(2)


import pygame as pyg

from utils.paths import get_asset_path

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

DIMENS = {
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
# "offset" : (x, y) par rapport a la position du perso (quand il regarde a droite)
# Le x est automatiquement inverse quand le perso regarde a gauche
# "size"   : (largeur, hauteur) de la hitbox
# "damage" : degats infliges au contact
HITBOX_DATA = {
    1: {
        1: {"offset": (38, -5), "size": (44, 32), "damage": 15},
        2: {"offset": (25, -22), "size": (58, 58), "damage": 25},
        3: {"offset": (48, -12), "size": (75, 42), "damage": 40},
    },
    2: {
        1: {"offset": (36, -8), "size": (40, 36), "damage": 12},
        2: {"offset": (20, -25), "size": (65, 65), "damage": 22},
        3: {"offset": (45, -10), "size": (80, 48), "damage": 35},
    },
    3: {
        1: {"offset": (50, -8), "size": (55, 40), "damage": 18},
        2: {"offset": (30, -30), "size": (60, 60), "damage": 28},
        3: {"offset": (55, -15), "size": (90, 50), "damage": 45},
    },
    4: {
        1: {"offset": (40, -5), "size": (42, 30), "damage": 10},
        2: {"offset": (20, -30), "size": (80, 70), "damage": 30},
        3: {"offset": (50, -20), "size": (100, 60), "damage": 50},
    },
    5: {
        1: {"offset": (35, -10), "size": (40, 35), "damage": 12},
        2: {"offset": (22, -28), "size": (70, 65), "damage": 24},
        3: {"offset": (46, -14), "size": (78, 44), "damage": 38},
    },
    6: {
        1: {"offset": (36, -8), "size": (38, 34), "damage": 14},
        2: {"offset": (24, -22), "size": (55, 55), "damage": 22},
        3: {"offset": (44, -12), "size": (72, 44), "damage": 36},
    },
}
_DEFAULT_HITBOX = {"offset": (36, -8), "size": (40, 36), "damage": 10}

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
        self.frame_S1 = 0
        self.frame_S2 = 0
        self.frame_S3 = 0

        self.timer_IDLE = 0
        self.timer_MOVE = 0
        self.timer_HURT = 0
        self.timer_S1 = 0
        self.timer_S2 = 0
        self.timer_S3 = 0

        self.is_moving = False
        self.is_attacking_s1 = False
        self.is_attacking_s2 = False
        self.is_attacking_s3 = False
        self.is_hurt = False
        self.is_dead = False

        self._hit_this_swing = set()

    def _dims(self, anim):
        return DIMENS.get(self.char_num, {}).get(anim, (FRAME_SIZE, FRAME_SIZE))

    def _blank(self, color=None, w=None, h=None):
        w = w or FRAME_SIZE
        h = h or FRAME_SIZE
        surf = pyg.Surface((w, h))
        surf.fill(color if color else self.color)
        return [surf]

    def _load_sheet(self, filename, w=FRAME_SIZE, h=FRAME_SIZE):
        try:
            path = get_asset_path("sprites", f"Character-{self.char_num}", filename)
            sheet = pyg.image.load(path).convert_alpha()
            n = max(1, sheet.get_width() // w)
            return [sheet.subsurface((i * w, 0, w, h)) for i in range(n)]
        except (FileNotFoundError, pyg.error):
            return None

    @staticmethod
    def _flip(frames):
        return [pyg.transform.flip(f, True, False) for f in frames]

    def _load_animations(self):
        mw, mh = self._dims("MOVE")
        s1w, s1h = self._dims("S1")
        s2w, s2h = self._dims("S2")
        s3w, s3h = self._dims("S3")

        raw_idle = self._load_sheet("IDLE-Sheet.png")
        self.has_sprites = raw_idle is not None

        idle = raw_idle or self._blank()
        move = self._load_sheet("MOVE-Sheet.png", mw, mh) or self._blank(w=mw, h=mh)
        hurt = self._load_sheet("HURT-Sheet.png") or idle
        dead = self._load_sheet("DEAD-Sheet.png") or self._blank((80, 0, 0))
        s1 = self._load_sheet("S1-Sheet.png", s1w, s1h) or self._blank(w=s1w, h=s1h)
        s2 = self._load_sheet("S2-Sheet.png", s2w, s2h) or self._blank(w=s2w, h=s2h)
        s3 = self._load_sheet("S3-1-Sheet.png", s3w, s3h) or self._blank(w=s3w, h=s3h)

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
        if skill_num == 1 and not self.is_attacking_s1:
            self.is_attacking_s1 = True
            self.frame_S1 = 0
            self.timer_S1 = 0
            self._hit_this_swing = set()
            return True
        if skill_num == 2 and not self.is_attacking_s2:
            self.is_attacking_s2 = True
            self.frame_S2 = 0
            self.timer_S2 = 0
            self._hit_this_swing = set()
            return True
        if skill_num == 3 and not self.is_attacking_s3:
            self.is_attacking_s3 = True
            self.frame_S3 = 0
            self.timer_S3 = 0
            self._hit_this_swing = set()
            return True
        return False

    def update_animation(self, dt, is_moving):
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
            frames = self.frames_S3_left if left else self.frames_S3
            return frames[min(self.frame_S3, len(frames) - 1)]

        if self.is_moving:
            frames = self.frames_MOVE_left if left else self.frames_MOVE
            return frames[self.frame_MOVE]

        frames = self.frames_IDLE_left if left else self.frames_IDLE
        return frames[self.frame_IDLE]

    def get_body_rect(self):
        x, y = self.position
        return pyg.Rect(x, y, FRAME_SIZE, FRAME_SIZE)

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
        ox, oy = data["offset"]
        sw, sh = data["size"]
        x, y = self.position

        if self.direction == "left":
            ox = -(ox + sw)

        return pyg.Rect(x + ox, y + oy, sw, sh)

    def check_hits(self, targets):
        skill = self._active_skill()
        if skill is None:
            return

        hitbox = self.get_attack_hitbox()
        dmg = HITBOX_DATA.get(self.char_num, {}).get(skill, _DEFAULT_HITBOX)["damage"]

        for target in targets:
            if target is self or target.is_dead:
                continue
            tid = id(target)
            if tid in self._hit_this_swing:
                continue
            if hitbox.colliderect(target.get_body_rect()):
                target.take_damage(dmg)
                self._hit_this_swing.add(tid)

    def draw_hitbox(self, surface):
        body = self.get_body_rect()
        atk = self.get_attack_hitbox()

        overlay = pyg.Surface(surface.get_size(), pyg.SRCALPHA)

        pyg.draw.rect(overlay, COLOR_BODY, body, 2)
        if atk:
            pyg.draw.rect(overlay, COLOR_ATTACK, atk, 2)

        surface.blit(overlay, (0, 0))

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

    def update(self):
        pass


class Furnace(Character):
    def __init__(self):
        super().__init__(1)


class Water(Character):
    def __init__(self):
        super().__init__(2)
