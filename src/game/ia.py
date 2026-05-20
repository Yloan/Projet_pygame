import random as r
from math import inf, sqrt

from game.characters import make_character
from ui.console import (
    print_debug,
    print_error,
    print_info,
)

RANGE_ATTACK = {"close": 80, "medium": 180, "far": 350}

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

    def _distance_to(self, position: tuple) -> float:
        dx = position[0] - self.current_position[0]
        dy = position[1] - self.current_position[1]
        return sqrt(dx * dx + dy * dy)

    def verify_range(self, skill: str, position_targeted: tuple) -> bool:
        """
        Retourne True si la cible est à portée du skill donné.
        """
        skill_range_key = INFOS_SKILL_RANGE.get(self.char_num, {}).get(skill)
        if skill_range_key is None:
            return False
        max_range = RANGE_ATTACK[skill_range_key]
        return self._distance_to(position_targeted) <= max_range

    def _update_direction(self, target_position: tuple):
        """
        Met à jour la direction du char (left/right) selon la cible.
        """
        if target_position[0] >= self.current_position[0]:
            self.char.direction = "right"
        else:
            self.char.direction = "left"

    def reflexion(self) -> str:
        health_in_pourcent = int(self.char.health / self.max_health * 100)
        _, closest_pos = self.get_closest_player()
        distance = self._distance_to(closest_pos)

        # En dessous de 20% de vie → fuite prioritaire
        if health_in_pourcent <= 20:
            action = r.choice(["flee", "flee", "flee", "flee", "follow"])

        elif health_in_pourcent <= 60:
            if distance <= RANGE_ATTACK["close"] * 1.5:
                # À portée : attaque souvent
                action = r.choice(
                    [
                        "attack",
                        "attack",
                        "attack",
                        "attack",
                        "attack",
                        "follow",
                        "follow",
                        "rest",
                    ]
                )
            else:
                # Trop loin : se rapproche
                action = r.choice(
                    [
                        "follow",
                        "follow",
                        "follow",
                        "attack",
                        "rest",
                    ]
                )

        # Au-dessus de 60% → mobile, cherche à engager
        else:
            if distance <= RANGE_ATTACK["close"] * 2:
                action = r.choice(
                    [
                        "follow",
                        "follow",
                        "attack",
                        "attack",
                        "top",
                        "bottom",
                        "left",
                        "right",
                        "rest",
                        "rest",
                    ]
                )
            else:
                action = r.choice(
                    [
                        "follow",
                        "follow",
                        "follow",
                        "follow",
                        "attack",
                        "top",
                        "bottom",
                        "rest",
                    ]
                )

        return action

    def pick_action(self) -> str:
        self.duration_action = r.randint(8, 20)
        action = self.reflexion()
        self.previous_action = self.current_action
        return action

    def update_player_position(self, player_id: int, position: tuple):
        self.position_players[player_id] = position

    def get_closest_player(self):
        """
        Return a tuple: (player_id, closest_position)
        """
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

    # ALL ACTIONS

    def go_top(self):
        x = r.randint(-1, 1)
        self.current_position = (
            self.current_position[0] + x,
            self.current_position[1] - self.speed,
        )

    def go_bottom(self):
        x = r.randint(-1, 1)
        self.current_position = (
            self.current_position[0] + x,
            self.current_position[1] + self.speed,
        )

    def go_right(self):
        y = r.randint(-1, 1)
        self.current_position = (
            self.current_position[0] + self.speed,
            self.current_position[1] + y,
        )

    def go_left(self):
        y = r.randint(-1, 1)
        self.current_position = (
            self.current_position[0] - self.speed,
            self.current_position[1] + y,
        )

    def do_nothing(self):
        pass

    def follow_closest_player(self):
        _, closest_position = self.get_closest_player()
        self._update_direction(closest_position)

        dx = closest_position[0] - self.current_position[0]
        dy = closest_position[1] - self.current_position[1]

        # Normalisation pour que la vitesse soit constante en diagonale
        distance = sqrt(dx * dx + dy * dy)
        if distance == 0:
            return

        nx = dx / distance
        ny = dy / distance

        self.current_position = (
            self.current_position[0] + nx * self.speed,
            self.current_position[1] + ny * self.speed,
        )

    def pick_attack(self):
        """
        Choisit un skill en fonction de la portée et du cooldown.
        N'attaque que si la cible est à portée du skill choisi.
        """
        if self._attack_cooldown > 0:
            # Pas encore prêt, se rapproche en attendant
            self.follow_closest_player()
            return

        _, closest_pos = self.get_closest_player()
        self._update_direction(closest_pos)

        # Construire la liste des skills disponibles à portée
        skill_infos = INFOS_SKILL_RANGE.get(self.char_num, {})
        available_skills = [
            int(s[1])  # "s1" → 1
            for s in skill_infos
            if self.verify_range(s, closest_pos)
        ]

        if not available_skills:
            # Hors portée : se rapprocher
            self.follow_closest_player()
            return

        skill = r.choice(available_skills)

        if skill == 1:
            self.char.is_attacking_s1 = True
        elif skill == 2:
            self.char.is_attacking_s2 = True
        else:
            self.char.is_attacking_s3 = True

        self._attack_cooldown = ATTACK_COOLDOWN_FRAMES

    def flee(self):
        """
        Fuite : direction opposée au joueur le plus proche
        """
        _, closest_position = self.get_closest_player()
        self._update_direction(closest_position)

        dx = closest_position[0] - self.current_position[0]
        dy = closest_position[1] - self.current_position[1]

        distance = sqrt(dx * dx + dy * dy)
        if distance == 0:
            return

        nx = dx / distance
        ny = dy / distance

        # On part dans la direction opposée
        self.current_position = (
            self.current_position[0] - nx * self.speed,
            self.current_position[1] - ny * self.speed,
        )

    def update(self, dt):
        # Décrémenter le cooldown d'attaque
        if self._attack_cooldown > 0:
            self._attack_cooldown -= 1

        self.char.is_moving = self.current_action not in ("rest", None)
        self.char.update_animation(dt, self.char.is_moving)

        if self.duration_action <= 0:
            self.current_action = self.pick_action()

        # Exécuter l'action courante
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
