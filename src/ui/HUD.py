from sysconfig import get_path

import pygame as pyg

import src.utils.paths as __paths__
from ui.console import (
    print_error,
    print_info,
    print_network,
    print_success,
    print_warning,
)

TOTAL_CHUNK_HEALTH = 18  # 6 chunk per HealthBar * 3 HelathBar
SIZE_FRAMES_HP_CORE = 16  # Size in x

TOTAL_CHUNK_ASS_WAIT = 6
SIZE_FRAMES_ASS_WAIT = 24  # Size in x

TOTAL_CHUNK_ASS_OK = 2
SIZE_FRAMES_ASS_OK = 24  # Size in x

# Cooldown
TOTAL_CHUNK_COOLDOWN_WAIT = 6
SIZE_CHUNK_COOLDOWN = 13  # Size in x


class HUD:
    def __init__(self, id_player):

        # Defined all sprites sheet
        self.all_picture = {
            "HUD-PLAYER-INTERFACE-Sheet": pyg.image.load(
                "assets/HUD/HUD-PLAYER-INTERFACE-Sheet.png"
            ),
            "HUD-ASS-OK-Sheet": pyg.image.load("assets/HUD/HUD-ASS-OK-Sheet.png"),
            "HUD-ASS-WAIT-Sheet": pyg.image.load("assets/HUD/HUD-ASS-WAIT-Sheet.png"),
            "HUD-HP-CORE-Sheet": pyg.image.load("assets/HUD/HUD-HP-CORE-Sheet.png"),
            "HUD-RESIST-Sheet": pyg.image.load("assets/HUD/HUD-RESIST-Sheet.png"),
            "HUD-S1-OK-Sheet": pyg.image.load("assets/HUD/HUD-S1-OK-Sheet.png"),
            "HUD-S1-WAIT-Sheet": pyg.image.load("assets/HUD/HUD-S1-WAIT-Sheet.png"),
            "HUD-S2-OK-Sheet": pyg.image.load("assets/HUD/HUD-S2-OK-Sheet.png"),
            "HUD-S2-WAIT-Sheet": pyg.image.load("assets/HUD/HUD-S2-WAIT-Sheet.png"),
            "HUD-S3-OK-Sheet": pyg.image.load("assets/HUD/HUD-S3-OK-Sheet.png"),
            "HUD-S3-WAIT-Sheet": pyg.image.load("assets/HUD/HUD-S3-WAIT-Sheet.png"),
        }

        # Put all the image into variables
        self.interface = self.all_picture["HUD-PLAYER-INTERFACE-Sheet"].subsurface(
            (id_player - 1) * 144, 0, 144, 96
        )

        self.cooldown = {
            "S1": [],
            "S2": [],
            "S3": [],
        }  # form of : {S1: [pyg.image.load("...").subsurface(first cooldown chunk of the first skill cooldown), ...], S2: ...}
        self.health = []
        self.sub_health1_red = self.all_picture["HUD-HP-CORE-Sheet"].subsurface(
            1 * 16, 0, SIZE_FRAMES_HP_CORE, 18
        )
        self.sub_health2_red = self.all_picture["HUD-HP-CORE-Sheet"].subsurface(
            2 * 16, 0, SIZE_FRAMES_HP_CORE, 18
        )
        self.sub_health1_blue = self.all_picture["HUD-HP-CORE-Sheet"].subsurface(
            4 * 16, 0, SIZE_FRAMES_HP_CORE, 18
        )
        self.sub_health2_blue = self.all_picture["HUD-HP-CORE-Sheet"].subsurface(
            5 * 16, 0, SIZE_FRAMES_HP_CORE, 18
        )
        self.sub_health1_green = self.all_picture["HUD-HP-CORE-Sheet"].subsurface(
            7 * 16, 0, SIZE_FRAMES_HP_CORE, 18
        )
        self.sub_health2_green = self.all_picture["HUD-HP-CORE-Sheet"].subsurface(
            8 * 16, 0, SIZE_FRAMES_HP_CORE, 18
        )
        self.sub_health3_green = self.all_picture["HUD-HP-CORE-Sheet"].subsurface(
            9 * 16, 0, SIZE_FRAMES_HP_CORE, 18
        )
        self.ass = {"OK": [], "WAIT": []}

        # Fill all the variables

        # Let's beggin with the health
        for i in range(6, -1, -3):
            for j in range(TOTAL_CHUNK_HEALTH // 3):
                chunk = self.all_picture["HUD-HP-CORE-Sheet"].subsurface(
                    i * SIZE_FRAMES_HP_CORE, 0, SIZE_FRAMES_HP_CORE, 18
                )
                self.health.append(chunk)

        # Ass
        for i in range(TOTAL_CHUNK_ASS_WAIT):
            chunk = self.all_picture["HUD-ASS-WAIT-Sheet"].subsurface(
                i * SIZE_FRAMES_ASS_WAIT, 0, SIZE_FRAMES_ASS_WAIT, 7
            )
            self.ass["WAIT"].append(chunk)

        for i in range(TOTAL_CHUNK_ASS_OK):
            chunk = self.all_picture["HUD-ASS-OK-Sheet"].subsurface(
                i * SIZE_FRAMES_ASS_OK, 0, SIZE_FRAMES_ASS_OK, 7
            )
            self.ass["OK"].append(chunk)

        # Cooldown
        for j in range(1, 4):
            for i in range(TOTAL_CHUNK_COOLDOWN_WAIT):
                chunk = self.all_picture[f"HUD-S{j}-WAIT-Sheet"].subsurface(
                    i * SIZE_CHUNK_COOLDOWN, 0, SIZE_CHUNK_COOLDOWN, 12
                )
                self.cooldown[f"S{j}"].append(chunk)

        # Variables for the health
        self.currentHealth = (
            len(self.health) - 1
        )  # Will chang this will be the index until we can go for display the health images, represents the health of the player
        self.currentBarColor = "red"

        # Variables for cooldown
        self.deltaTimeS1 = 0
        self.deltaTimeS2 = 0
        self.deltaTimeS3 = 0

    def DealsDamage(self, damage=1):
        """Remove a complete chunk if damage = 3"""
        try:
            toRemove = damage - (damage % 3) / 3
            toReplace = damage % 3

            self.currentHealth -= toRemove
            repl = None
            if self.currentBarColor == "green":
                repl = (
                    self.sub_health1_green if toReplace == 1 else self.sub_health2_green
                )
            if self.currentBarColor == "blue":
                repl = (
                    self.sub_health1_blue if toReplace == 1 else self.sub_health2_blue
                )
            if self.currentBarColor == "red":
                repl = self.sub_health1_red if toReplace == 1 else self.sub_health2_red

            self.health[toReplace] = repl

            self.verifyColorBar()

            return 0

        except Exception as e:
            print_error(f"Error while deals damage {e}")
            return 1

    def verifyColorBar(self):
        try:
            red = 12
            blue = 6
            green = 0

            if self.currentHealth >= red:
                self.currentBarColor = "red"

            elif self.currentHealth >= blue:
                self.currentBarColor = "blue"

            elif self.currentHealth >= green:
                self.currentBarColor = "green"

            return 0
        except Exception as e:
            print_error(f"Error while veirify color bar {e}")
            return 1
