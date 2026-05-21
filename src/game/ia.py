import random as r
from math import inf, sqrt

import pygame as pyg

from game.characters import make_character
from game.map_laoder import MAP1_COLLISIONS
from ui.console import (
    print_debug,
    print_error,
    print_info,
)

RANGE_ATTACK = {"close": 80, "medium": 180, "far": 350}

_COLLISION_THICKNESS = 10

INFOS_SKILL_RANGE = {
    1: {
        "s1": "close",
        "s2": "close",
        "s3": "close",
    },
    2: {"s1": "far", "s2": "far", "s3": "far"},
    3: {
        "s1": "close",
        "s2": "close",
        "s3": "medium",
    },
    4: {
        "s1": "close",
        "s2": "close",
        "s3": "medium",
    },
    5: {
        "s1": "far",
        "s2": "far",
        "s3": "close",
    },
    6: {
        "s1": "close",
        "s2": "close",
        "s3": "close",
    },
}

ATTACK_COOLDOWN_FRAMES = 60

COLLISION_THICKNESS = 10


_OPPOSITE = {
    "top": "bottom",
    "bottom": "top",
    "left": "right",
    "right": "left",
}


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

        # Cooldown anti-spam attaque
        self._attack_cooldown = 0

        self._post_hit_freeze = 0
        self._hit_set_size_last = 0

        self._blocked_directions: set = set()

    # Helpers

    def _distance_to(self, position: tuple) -> float:
        dx = position[0] - self.current_position[0]
        dy = position[1] - self.current_position[1]
        return sqrt(dx * dx + dy * dy)

    def verify_range(self, skill: str, position_targeted: tuple) -> bool:
        """Retourne True si la cible est à portée du skill donné"""
        skill_range_key = INFOS_SKILL_RANGE.get(self.char_num, {}).get(skill)
        if skill_range_key is None:
            return False
        max_range = RANGE_ATTACK[skill_range_key]
        return self._distance_to(position_targeted) <= max_range

    def _update_direction(self, target_position: tuple):
        """Met à jour la direction du char (left/right) selon la cible"""
        if target_position[0] >= self.current_position[0]:
            self.char.direction = "right"
        else:
            self.char.direction = "left"

    def _bot_rect(self, position=None) -> pyg.Rect:
        """Retourne le rect du bot à une position donnée (ou position actuelle)"""
        x, y = position if position is not None else self.current_position
        return pyg.Rect(int(x), int(y), 40, 40)  # FRAME_SIZE = 40

    def _check_collision(self, new_position: tuple) -> bool:
        """Retourne True si new_position provoque une collision avec MAP1"""
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

    # Réflexion

    def reflexion(self):
        health_in_pourcent = int(self.char.health / self.max_health * 100)
        _, closest_pos = self.get_closest_player()
        distance = self._distance_to(closest_pos)

        # Vérifie si au moins un skill est utilisable à cette distance
        skill_infos = INFOS_SKILL_RANGE.get(self.char_num, {})
        can_attack = any(
            distance <= RANGE_ATTACK[range_key] for range_key in skill_infos.values()
        )

        random_dirs = [
            d
            for d in ("top", "bottom", "left", "right", "rest")
            if d not in self._blocked_directions
        ]
        if not random_dirs:
            random_dirs = ["rest"]

        # En dessous de 20% de vie → fuite prioritaire
        if health_in_pourcent <= 20:
            action = r.choice(["flee", "flee", "flee", "flee", "follow"])

        elif health_in_pourcent <= 60:
            if can_attack and distance <= RANGE_ATTACK["close"] * 1.5:
                action = r.choice(
                    ["attack", "follow", "follow", "follow", "rest", "rest"]
                )
            else:
                pool = ["follow", "follow", "follow", "follow", "rest"]
                if can_attack:
                    pool.append("attack")
                action = r.choice(pool)

        else:
            if can_attack and distance <= RANGE_ATTACK["close"] * 2:
                pool = ["follow", "follow", "follow", "attack"] + random_dirs
                action = r.choice(pool)
            else:
                pool = ["follow", "follow", "follow", "follow", "follow"] + random_dirs
                action = r.choice(pool)

        return action

    def pick_action(self):
        self.duration_action = r.randint(25, 55)
        self._blocked_directions.clear()
        action = self.reflexion()
        self.previous_action = self.current_action
        return action

    def update_player_position(self, player_id: int, position: tuple):
        self.position_players[player_id] = position

    def get_closest_player(self):
        """Return a tuple: (player_id, closest_position)"""
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

    def go_bottom(self):
        ox = r.randint(-1, 1)
        new_pos = (self.current_position[0] + ox, self.current_position[1] + self.speed)
        self._move_with_collision(new_pos, "bottom")

    def go_right(self):
        oy = r.randint(-1, 1)
        new_pos = (self.current_position[0] + self.speed, self.current_position[1] + oy)
        self._move_with_collision(new_pos, "right")

    def go_left(self):
        oy = r.randint(-1, 1)
        new_pos = (self.current_position[0] - self.speed, self.current_position[1] + oy)
        self._move_with_collision(new_pos, "left")

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

    def pick_attack(self):
        """Choisit un skill en fonction de la portée et du cooldown"""
        if self._attack_cooldown > 0:
            self.follow_closest_player()
            return

        _, closest_pos = self.get_closest_player()
        self._update_direction(closest_pos)

        skill_infos = INFOS_SKILL_RANGE.get(self.char_num, {})
        available_skills = [
            int(s[1]) for s in skill_infos if self.verify_range(s, closest_pos)
        ]

        if not available_skills:
            self.follow_closest_player()
            return

        skill = r.choice(available_skills)
        success = self.char.use_skill(skill)
        if success:
            self._attack_cooldown = ATTACK_COOLDOWN_FRAMES

    def flee(self):
        """Fuite --> direction opposée au joueur le plus proche"""
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

    # Update method a appelé dans la bocuel principale pour updates les bots present dzns lz session

    def update(self, dt):
        if self.char.is_dead or self.char.is_hurt:
            self.char.update_animation(dt, False)
            self.char.position = self.current_position
            return

        if self._attack_cooldown > 0:
            self._attack_cooldown -= 1

        current_hit_set_size = len(self.char._hit_this_swing)
        if current_hit_set_size > self._hit_set_size_last:
            self._post_hit_freeze = 45
            self.duration_action = 0
        self._hit_set_size_last = current_hit_set_size

        if self._post_hit_freeze > 0:
            self._post_hit_freeze -= 1
            self.char.is_moving = False
            self.char.update_animation(dt, False)
            self.char.position = self.current_position
            return

        self.char.is_moving = self.current_action not in ("rest", None)
        self.char.update_animation(dt, self.char.is_moving)

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

        self.duration_action -= 1
        self.char.position = self.current_position
