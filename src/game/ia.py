import random as r
from math import inf, sqrt

import pygame as pyg

from game.characters import FRAME_SIZE, HITBOX_DATA, make_character
from game.map_laoder import MAP1_COLLISIONS
from ui.console import (
    print_debug,
    print_error,
    print_info,
)

RANGE_ATTACK = {"close": 90, "medium": 160, "far": 320}

_COLLISION_THICKNESS = 10

INFOS_SKILL_RANGE = {
    1: {
        "s1": "close",
        "s2": "close",
        "s3": "medium",
    },
    2: {
        "s1": "far",
        "s2": "close",
        "s3": "far",
    },
    3: {
        "s1": "close",
        "s2": "close",
        "s3": "medium",
    },
    4: {
        "s1": "close",
        "s2": "medium",
        "s3": "medium",
    },
    5: {
        "s1": "far",
        "s2": "close",
        "s3": "far",
    },
}

ATTACK_COOLDOWN_FRAMES = 60

COLLISION_THICKNESS = 10

BOT_MODE_OFFENSIVE = "offensive"
BOT_MODE_DEFENSIVE = "defensive"

MODE_DURATION_MIN = 180
MODE_DURATION_MAX = 360

RAGE_DAMAGE_THRESHOLD = 30
RAGE_WINDOW_FRAMES = 90
RAGE_FORCED_OFFENSIVE_DURATION = 240

Y_ALIGNMENT_TOLERANCE = 12

_OPPOSITE = {
    "top": "bottom",
    "bottom": "top",
    "left": "right",
    "right": "left",
}


def _compute_skill_positioning():
    result = {}
    for char_num, skills_hitbox in HITBOX_DATA.items():
        if char_num not in INFOS_SKILL_RANGE:
            continue
        result[char_num] = {}
        for skill_num, hdata in skills_hitbox.items():
            skill_key = f"s{skill_num}"
            range_key = INFOS_SKILL_RANGE.get(char_num, {}).get(skill_key)
            if range_key is None:
                continue
            offset_y = hdata["offset"][1]
            size_h = hdata["size"][1]
            y_alignment_offset = offset_y + size_h / 2 - FRAME_SIZE / 2
            result[char_num][skill_num] = {
                "ideal_distance": RANGE_ATTACK[range_key],
                "range_key": range_key,
                "y_alignment_offset": y_alignment_offset,
            }
    return result


SKILL_POSITIONING = _compute_skill_positioning()


class Bot:
    def __init__(self, char_num: int, nb_players: int, position: tuple, speed: int = 0):

        self.speed = 2 if speed == 0 else speed

        self.actions_possible = ["follow", "random", "attack", "flee"]
        self.random_action_possible = ["top", "left", "right", "bottom", "rest"]
        self.actions = {
            self.actions_possible[0]: self.follow_closest_player,
            self.actions_possible[1]: {
                self.random_action_possible[0]: self.go_top,
                self.random_action_possible[1]: self.go_left,
                self.random_action_possible[2]: self.go_right,
                self.random_action_possible[3]: self.go_bottom,
                self.random_action_possible[4]: self.do_nothing,
            },
            self.actions_possible[2]: self.pick_attack,
            self.actions_possible[3]: self.flee,
        }
        self.current_position = position

        self.duration_action = 0
        self.position_players = {}
        for i in range(1, nb_players + 1):
            self.position_players[i] = (0, 0)

        self.char = make_character(char_num)
        self.max_health = self.char.max_health
        self.char_num = char_num

        self.previous_action = None
        self.current_action = None

        self._attack_cooldown = 0

        self._post_hit_freeze = 0
        self._hit_set_size_last = 0
        self._post_hit_flee_frames = 0
        self._overlap_frames = 0

        self._blocked_directions: set = set()

        self.current_mode = r.choice([BOT_MODE_OFFENSIVE, BOT_MODE_DEFENSIVE])
        self.mode_duration_remaining = r.randint(MODE_DURATION_MIN, MODE_DURATION_MAX)

        self._rage_damage_accumulated_in_window = 0
        self._rage_window_frames_remaining = 0
        self._rage_forced_offensive_frames_remaining = 0

        self._health_last_frame = self.char.max_health

        self._targeted_skill_for_positioning = None

    # Helpers

    def _distance_to(self, position: tuple) -> float:
        dx = position[0] - self.current_position[0]
        dy = position[1] - self.current_position[1]
        return sqrt(dx * dx + dy * dy)

    def verify_range(self, skill: str, position_targeted: tuple) -> bool:
        skill_range_key = INFOS_SKILL_RANGE.get(self.char_num, {}).get(skill)
        if skill_range_key is None:
            return False
        max_range = RANGE_ATTACK[skill_range_key]
        return self._distance_to(position_targeted) <= max_range

    def _update_direction(self, target_position: tuple):
        if target_position[0] >= self.current_position[0]:
            self.char.direction = "right"
        else:
            self.char.direction = "left"
        self.char.position = self.current_position

    def _bot_rect(self, position=None) -> pyg.Rect:
        x, y = position if position is not None else self.current_position
        return pyg.Rect(int(x), int(y), 40, 40)

    def _check_collision(self, new_position: tuple) -> bool:
        rect = self._bot_rect(new_position)
        return any(rect.colliderect(wall) for wall in MAP1_COLLISIONS)

    def _move_with_collision(self, new_position: tuple, direction: str) -> bool:
        if self._check_collision(new_position):
            self._blocked_directions.add(direction)
            self.duration_action = 0
            self.current_action = None
            return True
        self.current_position = new_position
        return False

    # Mode management

    def _update_mode(self):
        if self._rage_forced_offensive_frames_remaining > 0:
            self._rage_forced_offensive_frames_remaining -= 1
            self.current_mode = BOT_MODE_OFFENSIVE
            return

        self.mode_duration_remaining -= 1
        if self.mode_duration_remaining <= 0:
            self.current_mode = r.choice([BOT_MODE_OFFENSIVE, BOT_MODE_DEFENSIVE])
            self.mode_duration_remaining = r.randint(
                MODE_DURATION_MIN, MODE_DURATION_MAX
            )

    def _update_rage_tracker(self):
        current_health = self.char.health
        damage_taken_this_frame = self._health_last_frame - current_health

        if damage_taken_this_frame > 0:
            if self._rage_window_frames_remaining <= 0:
                self._rage_damage_accumulated_in_window = 0
                self._rage_window_frames_remaining = RAGE_WINDOW_FRAMES

            self._rage_damage_accumulated_in_window += damage_taken_this_frame

            if self._rage_damage_accumulated_in_window >= RAGE_DAMAGE_THRESHOLD:
                self._rage_forced_offensive_frames_remaining = (
                    RAGE_FORCED_OFFENSIVE_DURATION
                )
                self._rage_damage_accumulated_in_window = 0
                self._rage_window_frames_remaining = 0

        if self._rage_window_frames_remaining > 0:
            self._rage_window_frames_remaining -= 1

        self._health_last_frame = current_health

    # Réflexion

    def _pick_first_skill_in_range(self, closest_pos: tuple):
        skill_infos = INFOS_SKILL_RANGE.get(self.char_num, {})
        for skill_key in ("s1", "s2", "s3"):
            if skill_key not in skill_infos:
                continue
            if self.verify_range(skill_key, closest_pos):
                return int(skill_key[1])
        return None

    def _select_skill_for_approach(self, closest_pos: tuple):
        skill_infos = INFOS_SKILL_RANGE.get(self.char_num, {})
        distance = self._distance_to(closest_pos)
        for skill_key in ("s1", "s2", "s3"):
            if skill_key not in skill_infos:
                continue
            range_key = skill_infos[skill_key]
            if distance <= RANGE_ATTACK[range_key] * 2:
                return int(skill_key[1])
        return 1

    def reflexion_offensive(
        self, health_in_pourcent: int, distance: float, can_attack: bool
    ):
        random_dirs = [
            d
            for d in ("top", "bottom", "left", "right", "rest")
            if d not in self._blocked_directions
        ]
        if not random_dirs:
            random_dirs = ["rest"]

        if health_in_pourcent <= 20:
            action = r.choice(["flee", "flee", "follow", "follow", "attack"])

        elif health_in_pourcent <= 60:
            if can_attack and distance <= RANGE_ATTACK["close"] * 1.2:
                action = r.choice(["attack", "attack", "follow", "follow"])
            else:
                pool = ["follow", "follow", "follow", "attack", "attack"]
                action = r.choice(pool)

        else:
            if can_attack and distance <= RANGE_ATTACK["close"] * 2:
                action = r.choice(
                    ["attack", "attack", "follow", "follow"] + random_dirs
                )
            else:
                action = r.choice(
                    ["follow", "follow", "follow", "follow"] + random_dirs
                )

        return action

    def reflexion_defensive(
        self, health_in_pourcent: int, distance: float, can_attack: bool
    ):
        random_dirs = [
            d
            for d in ("top", "bottom", "left", "right", "rest")
            if d not in self._blocked_directions
        ]
        if not random_dirs:
            random_dirs = ["rest"]

        if health_in_pourcent <= 20:
            action = r.choice(["flee", "flee", "flee", "flee", "flee", "follow"])

        elif health_in_pourcent <= 60:
            if can_attack and distance <= RANGE_ATTACK["far"]:
                action = r.choice(
                    ["attack", "follow", "follow", "flee", "flee", "rest"]
                )
            else:
                action = r.choice(
                    ["flee", "flee", "follow", "follow", "rest"] + random_dirs
                )

        else:
            if can_attack and distance <= RANGE_ATTACK["medium"]:
                action = r.choice(
                    ["attack", "flee", "flee", "follow", "rest"] + random_dirs
                )
            else:
                action = r.choice(
                    ["flee", "flee", "flee", "follow", "rest"] + random_dirs
                )

        return action

    def reflexion(self):
        health_in_pourcent = int(self.char.health / self.max_health * 100)
        _, closest_pos = self.get_closest_player()
        distance = self._distance_to(closest_pos)

        skill_infos = INFOS_SKILL_RANGE.get(self.char_num, {})
        can_attack = any(
            distance <= RANGE_ATTACK[range_key] for range_key in skill_infos.values()
        )

        if self.current_mode == BOT_MODE_OFFENSIVE:
            return self.reflexion_offensive(health_in_pourcent, distance, can_attack)
        else:
            return self.reflexion_defensive(health_in_pourcent, distance, can_attack)

    def pick_action(self):
        self.duration_action = r.randint(25, 55)
        self._blocked_directions.clear()
        self._targeted_skill_for_positioning = None
        action = self.reflexion()
        self.previous_action = self.current_action
        return action

    def update_player_position(self, player_id: int, position: tuple):
        self.position_players[player_id] = position

    def get_closest_player(self):
        closest_position = (0, 0)
        min_distance = inf
        player_followed = None

        for key, value in self.position_players.items():
            x, y = value
            dx = x - self.current_position[0]
            dy = y - self.current_position[1]
            distance = sqrt((dx * dx) + (dy * dy))

            if min_distance > distance:
                min_distance = distance
                player_followed = key
                closest_position = (x, y)

        return (player_followed, closest_position)

    # Actions de mouvement

    def go_top(self):
        ox = r.randint(-1, 1)
        new_pos = (self.current_position[0] + ox, self.current_position[1] - self.speed)
        self._move_with_collision(new_pos, "top")
        self.char.position = self.current_position

    def go_bottom(self):
        ox = r.randint(-1, 1)
        new_pos = (self.current_position[0] + ox, self.current_position[1] + self.speed)
        self._move_with_collision(new_pos, "bottom")
        self.char.position = self.current_position

    def go_right(self):
        oy = r.randint(-1, 1)
        new_pos = (self.current_position[0] + self.speed, self.current_position[1] + oy)
        self._move_with_collision(new_pos, "right")
        self.char.direction = "right"
        self.char.position = self.current_position

    def go_left(self):
        oy = r.randint(-1, 1)
        new_pos = (self.current_position[0] - self.speed, self.current_position[1] + oy)
        self._move_with_collision(new_pos, "left")
        self.char.direction = "left"
        self.char.position = self.current_position

    def do_nothing(self):
        pass

    def follow_closest_player(self):
        _, closest_position = self.get_closest_player()
        self._update_direction(closest_position)

        dx = closest_position[0] - self.current_position[0]
        dy = closest_position[1] - self.current_position[1]

        distance = sqrt(dx * dx + dy * dy)
        if distance == 0:
            return

        nx = dx / distance
        ny = dy / distance

        new_pos = (
            self.current_position[0] + nx * self.speed,
            self.current_position[1] + ny * self.speed,
        )

        if abs(nx) >= abs(ny):
            direction = "right" if nx > 0 else "left"
        else:
            direction = "bottom" if ny > 0 else "top"

        self._move_with_collision(new_pos, direction)

    def follow_with_skill_positioning(self, skill_num: int):
        _, closest_position = self.get_closest_player()
        self._update_direction(closest_position)

        positioning_data = SKILL_POSITIONING.get(self.char_num, {}).get(skill_num)
        if positioning_data is None:
            self.follow_closest_player()
            return

        ideal_distance = positioning_data["ideal_distance"]
        y_alignment_offset = positioning_data["y_alignment_offset"]

        target_y = closest_position[1] - y_alignment_offset

        dx = closest_position[0] - self.current_position[0]
        dy = target_y - self.current_position[1]
        current_distance_x = abs(dx)

        y_is_aligned = abs(self.current_position[1] - target_y) <= Y_ALIGNMENT_TOLERANCE

        if not y_is_aligned:
            move_y = self.speed if dy > 0 else -self.speed
            new_pos = (self.current_position[0], self.current_position[1] + move_y)
            direction = "bottom" if dy > 0 else "top"
            self._move_with_collision(new_pos, direction)
            return

        if current_distance_x > ideal_distance:
            move_x = self.speed if dx > 0 else -self.speed
            new_pos = (self.current_position[0] + move_x, self.current_position[1])
            direction = "right" if dx > 0 else "left"
            self._move_with_collision(new_pos, direction)

    def _pick_attack_char4(self, closest_pos: tuple):
        distance = self._distance_to(closest_pos)
        self._update_direction(closest_pos)

        charges_actuelles = self.char.chrgs

        if charges_actuelles == self.char.MAX_CHRGS:
            positioning_data_s3 = SKILL_POSITIONING.get(4, {}).get(3)
            if positioning_data_s3 is not None:
                target_y = closest_pos[1] - positioning_data_s3["y_alignment_offset"]
                y_is_aligned = (
                    abs(self.current_position[1] - target_y) <= Y_ALIGNMENT_TOLERANCE
                )
                if not y_is_aligned:
                    self.follow_with_skill_positioning(3)
                    return
            success = self.char.use_skill(3)
            if success:
                self._attack_cooldown = ATTACK_COOLDOWN_FRAMES
            return

        if distance <= RANGE_ATTACK["close"]:
            positioning_data_s1 = SKILL_POSITIONING.get(4, {}).get(1)
            if positioning_data_s1 is not None:
                target_y = closest_pos[1] - positioning_data_s1["y_alignment_offset"]
                y_is_aligned = (
                    abs(self.current_position[1] - target_y) <= Y_ALIGNMENT_TOLERANCE
                )
                if not y_is_aligned:
                    self.follow_with_skill_positioning(1)
                    return
            success = self.char.use_skill(1)
            if success:
                self._attack_cooldown = ATTACK_COOLDOWN_FRAMES
            return

        if distance <= RANGE_ATTACK["medium"]:
            self.follow_with_skill_positioning(1)
            return

        self.follow_closest_player()

    def _pick_attack_char5(self, closest_pos: tuple):
        distance = self._distance_to(closest_pos)
        self._update_direction(closest_pos)

        wtr_cns_vide = self.char.wtr_cns == 0
        sda_cns_vide = self.char.sda_cns == 0
        toutes_cannettes_vides = wtr_cns_vide and sda_cns_vide

        if toutes_cannettes_vides:
            success = self.char.use_skill(3)
            if success:
                self._attack_cooldown = ATTACK_COOLDOWN_FRAMES
            return

        une_cannette_vide = wtr_cns_vide or sda_cns_vide

        if une_cannette_vide:
            skill_num_close = 1 if wtr_cns_vide else 2
            if distance <= RANGE_ATTACK["close"]:
                positioning_data = SKILL_POSITIONING.get(5, {}).get(skill_num_close)
                if positioning_data is not None:
                    target_y = closest_pos[1] - positioning_data["y_alignment_offset"]
                    y_is_aligned = (
                        abs(self.current_position[1] - target_y)
                        <= Y_ALIGNMENT_TOLERANCE
                    )
                    if not y_is_aligned:
                        self.follow_with_skill_positioning(skill_num_close)
                        return
                success = self.char.use_skill(skill_num_close)
                if success:
                    self._attack_cooldown = ATTACK_COOLDOWN_FRAMES
            else:
                self.follow_closest_player()
            return

        if distance >= RANGE_ATTACK["far"]:
            skill_num_in_range = self._pick_first_skill_in_range(closest_pos)
            if skill_num_in_range is not None:
                positioning_data = SKILL_POSITIONING.get(5, {}).get(skill_num_in_range)
                if positioning_data is not None:
                    target_y = closest_pos[1] - positioning_data["y_alignment_offset"]
                    y_is_aligned = (
                        abs(self.current_position[1] - target_y)
                        <= Y_ALIGNMENT_TOLERANCE
                    )
                    if not y_is_aligned:
                        self.follow_with_skill_positioning(skill_num_in_range)
                        return
                success = self.char.use_skill(skill_num_in_range)
                if success:
                    self._attack_cooldown = ATTACK_COOLDOWN_FRAMES
                return

        distance_ideale_far = RANGE_ATTACK["far"]
        dx = closest_pos[0] - self.current_position[0]
        dy = closest_pos[1] - self.current_position[1]
        dist = sqrt(dx * dx + dy * dy)
        if dist == 0:
            return

        nx = dx / dist
        ny = dy / dist

        if distance < distance_ideale_far:
            new_pos = (
                self.current_position[0] - nx * self.speed,
                self.current_position[1] - ny * self.speed,
            )
            direction = "left" if nx > 0 else "right"
        else:
            new_pos = (
                self.current_position[0] + nx * self.speed,
                self.current_position[1] + ny * self.speed,
            )
            direction = "right" if nx > 0 else "left"

        self._move_with_collision(new_pos, direction)

    def pick_attack(self):
        if self._attack_cooldown > 0:
            _, closest_pos = self.get_closest_player()
            skill_num_to_approach = self._select_skill_for_approach(closest_pos)
            self.follow_with_skill_positioning(skill_num_to_approach)
            return

        _, closest_pos = self.get_closest_player()
        self._update_direction(closest_pos)

        if self.char_num == 4:
            self._pick_attack_char4(closest_pos)
            return

        if self.char_num == 5:
            self._pick_attack_char5(closest_pos)
            return

        skill_num_in_range = self._pick_first_skill_in_range(closest_pos)

        if skill_num_in_range is None:
            skill_num_to_approach = self._select_skill_for_approach(closest_pos)
            self._targeted_skill_for_positioning = skill_num_to_approach
            self.follow_with_skill_positioning(skill_num_to_approach)
            return

        positioning_data = SKILL_POSITIONING.get(self.char_num, {}).get(
            skill_num_in_range
        )
        if positioning_data is not None:
            target_y = closest_pos[1] - positioning_data["y_alignment_offset"]
            y_is_aligned = (
                abs(self.current_position[1] - target_y) <= Y_ALIGNMENT_TOLERANCE
            )
            if not y_is_aligned:
                self.follow_with_skill_positioning(skill_num_in_range)
                return

        success = self.char.use_skill(skill_num_in_range)
        if success:
            self._attack_cooldown = ATTACK_COOLDOWN_FRAMES

    def flee(self):
        _, closest_position = self.get_closest_player()
        self._update_direction(closest_position)

        dx = closest_position[0] - self.current_position[0]
        dy = closest_position[1] - self.current_position[1]

        distance = sqrt(dx * dx + dy * dy)
        if distance == 0:
            return

        nx = dx / distance
        ny = dy / distance

        new_pos = (
            self.current_position[0] - nx * self.speed,
            self.current_position[1] - ny * self.speed,
        )

        if abs(nx) >= abs(ny):
            direction = "left" if nx > 0 else "right"
        else:
            direction = "top" if ny > 0 else "bottom"

        self._move_with_collision(new_pos, direction)

    def update(self, dt):
        if self.char.is_dead or self.char.is_hurt:
            self.char.position = self.current_position
            self.char.update_animation(dt, False)
            self.current_position = self.char.position
            return

        self._update_rage_tracker()
        self._update_mode()

        if self._attack_cooldown > 0:
            self._attack_cooldown -= 1

        current_hit_set_size = len(self.char._hit_this_swing)
        if current_hit_set_size > self._hit_set_size_last:
            self._post_hit_freeze = 45
            self._post_hit_flee_frames = 90
            self.duration_action = 0
        self._hit_set_size_last = current_hit_set_size

        if self.char.status.is_disabled:
            self.char.is_moving = False
            self.char.position = self.current_position
            self.char.update_animation(dt, False)
            self.current_position = self.char.position
            self.duration_action = 0
            self.current_action = None
            return

        if self._post_hit_freeze > 0:
            self._post_hit_freeze -= 1
            self.char.is_moving = False
            self.char.position = self.current_position
            self.char.update_animation(dt, False)
            self.current_position = self.char.position
            return

        if self._post_hit_flee_frames > 0:
            self._post_hit_flee_frames -= 1
            self.flee()
            self.char.is_moving = True
            self.char.position = self.current_position
            self.char.update_animation(dt, True)
            self.current_position = self.char.position
            return

        _, closest_pos = self.get_closest_player()
        dist_to_closest = self._distance_to(closest_pos)
        if dist_to_closest < 20:
            self._overlap_frames += 1
            if self._overlap_frames > 120:
                self.flee()
                self.char.is_moving = True
                self.char.position = self.current_position
                self.char.update_animation(dt, True)
                self.current_position = self.char.position
                return
        else:
            self._overlap_frames = 0

        self.char.position = self.current_position
        self.char.is_moving = self.current_action not in ("rest", None)
        self.char.update_animation(dt, self.char.is_moving)
        self.current_position = self.char.position

        status = self.char.status
        ia_can_move = not (status.is_pushed or status.is_grabbed or status.is_stunned)

        if ia_can_move:
            if self.duration_action <= 0:
                self.current_action = self.pick_action()

            if self.current_action is not None:
                if self.current_action in ("top", "bottom", "right", "left", "rest"):
                    self.actions["random"][self.current_action]()
                elif self.current_action in self.actions:
                    self.actions[self.current_action]()
                else:
                    print_error(f"Action inconnue: {self.current_action}")
            else:
                print_error("Can't pick action")
        else:
            self.duration_action = 0

        self.duration_action -= 1
