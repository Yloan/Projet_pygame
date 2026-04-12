from sysconfig import get_path

import pygame as pyg

import utils.paths as __paths__
from ui.console import (
    print_error,
    print_info,
    print_network,
    print_success,
    print_warning,
)

TOTAL_CHUNK_HEALTH = 18
SIZE_FRAMES_HP_CORE = 16

TOTAL_CHUNK_ASS_WAIT = 6
SIZE_FRAMES_ASS_WAIT = 24

TOTAL_CHUNK_ASS_OK = 2
SIZE_FRAMES_ASS_OK = 24

TOTAL_CHUNK_COOLDOWN_WAIT = 6
TOTAL_CHUNK_COOLDOWN_OK = 2
SIZE_CHUNK_COOLDOWN = 13

TOTAL_CHUNK_RESIST = 3
SIZE_FRAMES_RESIST = 13
HEIGHT_RESIST = 10

ANIM_SPEED_OK = 0.3
ANIM_SPEED_ASS = 0.25

OFFSET_HEALTH = (4, 2)
OFFSET_RESIST = (10, 80)
OFFSET_ASS = (29, 83)
OFFSET_COOLDOWN = {
    "S1": (57, 74),
    "S2": (70, 74),
    "S3": (83, 74),
}


class HUD:
    def __init__(self, id_player):
        SCALE = 2

        def _s(surf):
            w, h = surf.get_size()
            return pyg.transform.scale(surf, (int(w * SCALE), int(h * SCALE)))

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

        self.interface = _s(
            self.all_picture["HUD-PLAYER-INTERFACE-Sheet"].subsurface(
                (id_player - 1) * 144, 0, 144, 96
            )
        )

        self.cooldown = {"S1": [], "S2": [], "S3": []}
        self.cooldownOK = {"S1": [], "S2": [], "S3": []}
        self.health = []

        self.sub_health1_red = _s(
            self.all_picture["HUD-HP-CORE-Sheet"].subsurface(
                1 * 16, 0, SIZE_FRAMES_HP_CORE, 18
            )
        )
        self.sub_health2_red = _s(
            self.all_picture["HUD-HP-CORE-Sheet"].subsurface(
                2 * 16, 0, SIZE_FRAMES_HP_CORE, 18
            )
        )
        self.sub_health1_blue = _s(
            self.all_picture["HUD-HP-CORE-Sheet"].subsurface(
                4 * 16, 0, SIZE_FRAMES_HP_CORE, 18
            )
        )
        self.sub_health2_blue = _s(
            self.all_picture["HUD-HP-CORE-Sheet"].subsurface(
                5 * 16, 0, SIZE_FRAMES_HP_CORE, 18
            )
        )
        self.sub_health1_green = _s(
            self.all_picture["HUD-HP-CORE-Sheet"].subsurface(
                7 * 16, 0, SIZE_FRAMES_HP_CORE, 18
            )
        )
        self.sub_health2_green = _s(
            self.all_picture["HUD-HP-CORE-Sheet"].subsurface(
                8 * 16, 0, SIZE_FRAMES_HP_CORE, 18
            )
        )
        self.sub_health3_green = _s(
            self.all_picture["HUD-HP-CORE-Sheet"].subsurface(
                9 * 16, 0, SIZE_FRAMES_HP_CORE, 18
            )
        )

        self.ass = {"OK": [], "WAIT": []}
        self.resist = []

        self.id_player = id_player
        self.scaled_w = int(144 * SCALE)
        self.scaled_h = int(96 * SCALE)

        for frame_idx in [6, 3, 0]:
            for j in range(6):
                chunk = _s(
                    self.all_picture["HUD-HP-CORE-Sheet"].subsurface(
                        frame_idx * SIZE_FRAMES_HP_CORE, 0, SIZE_FRAMES_HP_CORE, 18
                    )
                )
                self.health.append(chunk)

        for i in range(TOTAL_CHUNK_ASS_WAIT):
            chunk = _s(
                self.all_picture["HUD-ASS-WAIT-Sheet"].subsurface(
                    i * SIZE_FRAMES_ASS_WAIT, 0, SIZE_FRAMES_ASS_WAIT, 7
                )
            )
            self.ass["WAIT"].append(chunk)

        for i in range(TOTAL_CHUNK_ASS_OK):
            chunk = _s(
                self.all_picture["HUD-ASS-OK-Sheet"].subsurface(
                    i * SIZE_FRAMES_ASS_OK, 0, SIZE_FRAMES_ASS_OK, 7
                )
            )
            self.ass["OK"].append(chunk)

        for j in range(1, 4):
            for i in range(TOTAL_CHUNK_COOLDOWN_WAIT):
                chunk = _s(
                    self.all_picture[f"HUD-S{j}-WAIT-Sheet"].subsurface(
                        i * SIZE_CHUNK_COOLDOWN, 0, SIZE_CHUNK_COOLDOWN, 12
                    )
                )
                self.cooldown[f"S{j}"].append(chunk)

        for j in range(1, 4):
            for i in range(TOTAL_CHUNK_COOLDOWN_OK):
                chunk = _s(
                    self.all_picture[f"HUD-S{j}-OK-Sheet"].subsurface(
                        i * SIZE_CHUNK_COOLDOWN, 0, SIZE_CHUNK_COOLDOWN, 12
                    )
                )
                self.cooldownOK[f"S{j}"].append(chunk)

        for i in range(TOTAL_CHUNK_RESIST):
            chunk = _s(
                self.all_picture["HUD-RESIST-Sheet"].subsurface(
                    i * SIZE_FRAMES_RESIST, 0, SIZE_FRAMES_RESIST, HEIGHT_RESIST
                )
            )
            self.resist.append(chunk)

        self.currentHealth = TOTAL_CHUNK_HEALTH - 1
        self.currentBarColor = "red"
        self.healthPartial = 0

        self.deltaTimeS1 = 0
        self.deltaTimeS2 = 0
        self.deltaTimeS3 = 0

        self.skillState = {"S1": "OK", "S2": "OK", "S3": "OK"}
        self.skillCooldownDuration = {"S1": 0.0, "S2": 0.0, "S3": 0.0}
        self.skillCooldownRemaining = {"S1": 0.0, "S2": 0.0, "S3": 0.0}
        self.skillAnimFrame = {"S1": 0, "S2": 0, "S3": 0}
        self.skillAnimTimer = {"S1": 0.0, "S2": 0.0, "S3": 0.0}

        self.assState = "OK"
        self.assFrame = 0
        self.assAnimTimer = 0.0
        self.assCooldownRemaining = 0.0
        self.assCooldownDuration = 0.0

        self.scale = SCALE

    def update(self, dt):
        try:
            for skill in ["S1", "S2", "S3"]:
                if self.skillState[skill] == "WAIT":
                    self.skillCooldownRemaining[skill] -= dt
                    if self.skillCooldownRemaining[skill] <= 0:
                        self.skillCooldownRemaining[skill] = 0
                        self.skillState[skill] = "OK"
                        self.skillAnimFrame[skill] = 0
                        self.skillAnimTimer[skill] = 0.0
                    else:
                        progress = 1.0 - (
                            self.skillCooldownRemaining[skill]
                            / self.skillCooldownDuration[skill]
                        )
                        self.skillAnimFrame[skill] = min(
                            int(progress * TOTAL_CHUNK_COOLDOWN_WAIT),
                            TOTAL_CHUNK_COOLDOWN_WAIT - 1,
                        )
                else:
                    self.skillAnimTimer[skill] += dt
                    if self.skillAnimTimer[skill] >= ANIM_SPEED_OK:
                        self.skillAnimTimer[skill] = 0.0
                        self.skillAnimFrame[skill] = (
                            self.skillAnimFrame[skill] + 1
                        ) % TOTAL_CHUNK_COOLDOWN_OK

            if self.assState == "WAIT":
                self.assCooldownRemaining -= dt
                if self.assCooldownRemaining <= 0:
                    self.assCooldownRemaining = 0
                    self.assState = "OK"
                    self.assFrame = 0
                    self.assAnimTimer = 0.0
                else:
                    progress = 1.0 - (
                        self.assCooldownRemaining / self.assCooldownDuration
                    )
                    self.assFrame = min(
                        int(progress * TOTAL_CHUNK_ASS_WAIT),
                        TOTAL_CHUNK_ASS_WAIT - 1,
                    )
            else:
                self.assAnimTimer += dt
                if self.assAnimTimer >= ANIM_SPEED_ASS:
                    self.assAnimTimer = 0.0
                    self.assFrame = (self.assFrame + 1) % TOTAL_CHUNK_ASS_OK

            self.deltaTimeS1 = self.skillCooldownRemaining["S1"]
            self.deltaTimeS2 = self.skillCooldownRemaining["S2"]
            self.deltaTimeS3 = self.skillCooldownRemaining["S3"]

            return 0
        except Exception as e:
            print_error(f"Error while update HUD {e}")
            return 1

    def draw(self, surface, x, y):
        try:
            temp = pyg.Surface((self.scaled_w, self.scaled_h), pyg.SRCALPHA)

            temp.blit(self.interface, (0, 0))
            self._drawHealth(temp, 0, 0)
            self._drawCooldowns(temp, 0, 0)
            self._drawAss(temp, 0, 0)
            self._drawResist(temp, 0, 0)

            flip_x = self.id_player in (2, 4)
            flip_y = self.id_player in (3, 4)
            final = pyg.transform.flip(temp, flip_x, flip_y)
            surface.blit(final, (x, y))
            return 0
        except Exception as e:
            print_error(f"Error while draw HUD {e}")
            return 1

    def _getPartialHealthSprite(self):
        if self.currentBarColor == "red":
            return (
                self.sub_health1_red
                if self.healthPartial == 1
                else self.sub_health2_red
            )
        elif self.currentBarColor == "blue":
            return (
                self.sub_health1_blue
                if self.healthPartial == 1
                else self.sub_health2_blue
            )
        elif self.currentBarColor == "green":
            return (
                self.sub_health1_green
                if self.healthPartial == 1
                else self.sub_health2_green
            )
        return None

    def _drawHealth(self, surface, x, y):
        barStart = self.currentHealth - (self.currentHealth % 6)
        chunksInBar = (self.currentHealth % 6) + 1
        ox = int(OFFSET_HEALTH[0] * self.scale) + 56
        oy = int(OFFSET_HEALTH[1] * self.scale) + 7
        step = int(SIZE_FRAMES_HP_CORE * self.scale) - round(self.scale)

        for i in range(chunksInBar):
            idx = barStart + i
            if i == chunksInBar - 1 and self.healthPartial > 0:
                partialSprite = self._getPartialHealthSprite()
                if partialSprite:
                    surface.blit(partialSprite, (x + ox + i * step, y + oy))
                    continue
            surface.blit(self.health[idx], (x + ox + i * step, y + oy))

    def _drawCooldowns(self, surface, x, y):
        for skill in ["S1", "S2", "S3"]:
            ox = int(OFFSET_COOLDOWN[skill][0] * self.scale)
            oy = int(OFFSET_COOLDOWN[skill][1] * self.scale)
            if self.skillState[skill] == "WAIT":
                frame = self.cooldown[skill][self.skillAnimFrame[skill]]
            else:
                frame = self.cooldownOK[skill][self.skillAnimFrame[skill]]
            surface.blit(frame, (x + ox, y + oy))

    def _drawAss(self, surface, x, y):
        if self.assState == "WAIT":
            frame = self.ass["WAIT"][self.assFrame]
        else:
            frame = self.ass["OK"][self.assFrame]
        ox = int(OFFSET_ASS[0] * self.scale) + 2
        oy = int(OFFSET_ASS[1] * self.scale) - 14
        surface.blit(frame, (x + ox, y + oy))
        surface.blit(frame, (x + ox - 48, y + oy))

    def _drawResist(self, surface, x, y):
        gap = 0
        for frame in self.resist:
            ox = int(OFFSET_RESIST[0] * self.scale) + 21
            oy = int(OFFSET_RESIST[1] * self.scale) - 59
            surface.blit(frame, (x + ox + gap, y + oy))
            gap += 56

    def startCooldown(self, skill, duration):
        try:
            self.skillState[skill] = "WAIT"
            self.skillCooldownDuration[skill] = duration
            self.skillCooldownRemaining[skill] = duration
            self.skillAnimFrame[skill] = 0
            self.skillAnimTimer[skill] = 0
            return 0
        except Exception as e:
            print_error(f"Error while start cooldown {e}")
            return 1

    def isSkillReady(self, skill):
        return self.skillState[skill] == "OK"

    def startAssCooldown(self, duration):
        try:
            self.assState = "WAIT"
            self.assCooldownDuration = duration
            self.assCooldownRemaining = duration
            self.assFrame = 0
            self.assAnimTimer = 0
            return 0
        except Exception as e:
            print_error(f"Error while start ass cooldown {e}")
            return 1

    def isAssReady(self):
        return self.assState == "OK"

    def setHealth(self, value):
        try:
            self.currentHealth = max(0, min(value, TOTAL_CHUNK_HEALTH - 1))
            self.healthPartial = 0
            self.verifyColorBar()
            return 0
        except Exception as e:
            print_error(f"Error while set health {e}")
            return 1

    def heal(self, amount):
        try:
            if self.healthPartial > 0:
                recover = min(amount, self.healthPartial)
                self.healthPartial -= recover
                amount -= recover

            fullChunks = amount // 3
            remainder = amount % 3

            self.currentHealth = min(
                self.currentHealth + fullChunks, TOTAL_CHUNK_HEALTH - 1
            )

            if remainder > 0 and self.healthPartial == 0:
                self.healthPartial = max(0, self.healthPartial - remainder)

            self.verifyColorBar()
            return 0
        except Exception as e:
            print_error(f"Error while heal {e}")
            return 1

    def DealsDamage(self, damage=1):
        try:
            fullChunks = damage // 3
            remainder = damage % 3

            self.currentHealth -= fullChunks

            if remainder > 0:
                self.healthPartial += remainder
                if self.healthPartial >= 3:
                    self.healthPartial -= 3
                    self.currentHealth -= 1

            self.currentHealth = max(0, self.currentHealth)
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
            print_error(f"Error while verify color bar {e}")
            return 1

    def isDead(self):
        return self.currentHealth <= 0 and self.healthPartial >= 3

    def getHealthPercent(self):
        totalPoints = (self.currentHealth + 1) * 3 - self.healthPartial
        return totalPoints / (TOTAL_CHUNK_HEALTH * 3)

    def updateFromServer(self, data):
        try:
            if "health" in data:
                self.setHealth(data["health"])

            if "healthPartial" in data:
                self.healthPartial = data["healthPartial"]

            if "resist" in data:
                self.setResist(data["resist"])

            if "cooldowns" in data:
                for skill in ["S1", "S2", "S3"]:
                    if skill in data["cooldowns"]:
                        remaining = data["cooldowns"][skill]
                        if remaining > 0:
                            if self.skillState[skill] == "OK":
                                duration = data.get("cooldownDurations", {}).get(
                                    skill, remaining
                                )
                                self.startCooldown(skill, duration)
                            self.skillCooldownRemaining[skill] = remaining
                        else:
                            self.skillState[skill] = "OK"
                            self.skillCooldownRemaining[skill] = 0

            if "assist" in data:
                if data["assist"] == "WAIT":
                    assDuration = data.get("assistDuration", self.assCooldownDuration)
                    assRemaining = data.get(
                        "assistRemaining", self.assCooldownRemaining
                    )
                    if self.assState == "OK":
                        self.startAssCooldown(assDuration)
                    self.assCooldownRemaining = assRemaining
                else:
                    self.assState = "OK"
                    self.assCooldownRemaining = 0

            self.verifyColorBar()
            return 0
        except Exception as e:
            print_error(f"Error while update from server {e}")
            return 1

    def toNetworkData(self):
        return {
            "health": self.currentHealth,
            "healthPartial": self.healthPartial,
            "cooldowns": {
                "S1": self.skillCooldownRemaining["S1"],
                "S2": self.skillCooldownRemaining["S2"],
                "S3": self.skillCooldownRemaining["S3"],
            },
            "cooldownDurations": {
                "S1": self.skillCooldownDuration["S1"],
                "S2": self.skillCooldownDuration["S2"],
                "S3": self.skillCooldownDuration["S3"],
            },
            "assist": self.assState,
            "assistDuration": self.assCooldownDuration,
            "assistRemaining": self.assCooldownRemaining,
        }

    def resetAll(self):
        self.currentHealth = TOTAL_CHUNK_HEALTH - 1
        self.healthPartial = 0
        self.currentBarColor = "red"
        self.assState = "OK"
        self.assFrame = 0
        self.assAnimTimer = 0.0
        self.assCooldownRemaining = 0.0
        for skill in ["S1", "S2", "S3"]:
            self.skillState[skill] = "OK"
            self.skillCooldownDuration[skill] = 0.0
            self.skillCooldownRemaining[skill] = 0.0
            self.skillAnimFrame[skill] = 0
            self.skillAnimTimer[skill] = 0.0
        self.deltaTimeS1 = 0
        self.deltaTimeS2 = 0
        self.deltaTimeS3 = 0
