import random as r
from math import inf, sqrt

from src.game.characters import make_character
from ui.console import (
    print_debug,
    print_error,
    print_info,
)


class Bot:
    def __init__(self, char_num: int, nb_players: int, position: tuple, speed: int = 0):

        self.speed = 4 if speed == 0 else speed

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
            self.actions_possible[2]: self.attack,
            self.actions_possible[3]: self.flee,
        }
        self.current_position = position

        self.duration_action = 0
        self.position_players = {}
        for i in range(1, nb_players + 1):
            self.position_players[i] = (0, 0)

        self.char = make_character(char_num)

        self.previous_action = None

        self.current_action = None

    def pick_action(self):
        # Pick a random action and return it
        self.duration_action = r.randint(1, 10)
        action = r.choice(self.actions_possible)
        if action == "random":
            action = r.choice(self.random_action_possible)
        return action  # One of the element of self.actions_possible picked randomly

    def update_player_position(self, player_id: int, position: tuple):
        self.position_players[player_id] = position

    def get_closest_player(self):
        """
        Return a tuple: (player followed, tuple closest position)
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
        """
        Go to top (for smoothness we will pick a random x to substract to the position too)
        """
        x = r.randint(-3, 3)

        self.current_position = (
            self.current_position[0] - x,
            self.current_position[1] - self.speed,
        )

    def go_bottom(self):
        """
        Go to bottom (for smoothness we will pick a random x to substract to the position too)
        """
        x = r.randint(-3, 3)

        self.current_position = (
            self.current_position[0] - x,
            self.current_position[1] + self.speed,
        )

    def go_right(self):
        """
        Go to right (for smoothness we will pick a random y to substract to the position too)
        """
        y = r.randint(-3, 3)

        self.current_position = (
            self.current_position[0] + self.speed,
            self.current_position[1] - y,
        )

    def go_left(self):
        """
        Go to left (for smoothness we will pick a random y to substract to the position too)
        """
        y = r.randint(-3, 3)

        self.current_position = (
            self.current_position[0] - self.speed,
            self.current_position[1] - y,
        )

    def do_nothing(self):
        pass

    def follow_closest_player(self):
        _, closest_position = self.get_closest_player()

        if (
            closest_position[0] > self.current_position[0]
            and closest_position[1] > self.current_position[1]
        ):
            self.current_position = (
                self.current_position[0] + self.speed,
                self.current_position[1] + self.speed,
            )
        elif (
            closest_position[0] < self.current_position[0]
            and closest_position[1] > self.current_position[1]
        ):
            self.current_position = (
                self.current_position[0] - self.speed,
                self.current_position[1] + self.speed,
            )
        elif (
            closest_position[0] > self.current_position[0]
            and closest_position[1] < self.current_position[1]
        ):
            self.current_position = (
                self.current_position[0] + self.speed,
                self.current_position[1] - self.speed,
            )
        elif (
            closest_position[0] < self.current_position[0]
            and closest_position[1] < self.current_position[1]
        ):
            self.current_position = (
                self.current_position[0] - self.speed,
                self.current_position[1] - self.speed,
            )

    def attack(self):
        """
        pick a random attack and do it
        """
        skill = r.randint(1, 3)

        if skill == 1:
            self.char.is_attacking_s1 = True
        elif skill == 2:
            self.char.is_attacking_s2 = True
        else:  # Should be 3
            self.char.is_attacking_s3 = True

    def flee(self):
        """
        Just do the inverse of the followed of the closest player
        """
        self.speed = -self.speed
        self.follow_closest_player()
        self.speed = -self.speed

    def update(self, dt):

        if self.current_action != "rest":
            self.char.is_moving = True
        else:
            self.char.is_moving = False

        self.char.update_animation(dt, self.char.is_moving)
        if self.duration_action <= 0:
            self.current_action = self.pick_action()

        if self.current_action is not None:
            if (
                self.current_action == "top"
                or self.current_action == "bottom"
                or self.current_action == "right"
                or self.current_action == "left"
            ):
                self.actions["random"][self.current_action]()
            else:
                self.actions[self.current_action]()
        else:
            print_error("Can't pick action")

        self.duration_action -= 1

        self.char.position = self.current_position
