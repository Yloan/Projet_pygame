from sysconfig import get_path

import pygame as pyg

import utils.paths as __paths__
from ui.console import (
    print_debug,
    print_error,
    print_info,
    print_network,
    print_success,
    print_warning,
)

# Global variables

SPEC_HUD_POSITIONS = {
    1: (304, 13),
    2: (900, 13),
    3: (304, 685),
    4: (900, 685),
}

CHRG_SHEET_W = 100
CHRG_SHEET_H = 26
CHRG_FRAMES = 5

WTR_SHEET_W = 130
WTR_SHEET_H = 15
WTR_FRAMES = 5

SDA_SHEET_W = 130
SDA_SHEET_H = 15
SDA_FRAMES = 5

SDA_ROW_GAP = 19

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

PORTRAIT_OFFSETS = {
    1: (16, 10),
    2: (230, 10),
    3: (16, 142),
    4: (230, 142),
}
PORTRAIT_SIZE = 40

OFFSET_HEALTH = (4, 2)
OFFSET_RESIST = (10, 80)
OFFSET_ASS = (29, 83)
OFFSET_COOLDOWN = {
    "S1": (57, 74),
    "S2": (70, 74),
    "S3": (83, 74),
}


# The dict for the position of alll the fucking position ( yes all positions are different 🫪)

OFFSETS_PAR_PLAYER = {
    1: {
        "health": (int(OFFSET_HEALTH[0] * 2) + 56, int(OFFSET_HEALTH[1] * 2) + 7),
        "resist": (int(OFFSET_RESIST[0] * 2) + 21, int(OFFSET_RESIST[1] * 2) - 59),
        "ass": (int(OFFSET_ASS[0] * 2) + 2, int(OFFSET_ASS[1] * 2) - 14),
        "ass2_dx": -48,
        "cooldown": {
            "S1": (
                int(OFFSET_COOLDOWN["S1"][0] * 2),
                int(OFFSET_COOLDOWN["S1"][1] * 2),
            ),
            "S2": (
                int(OFFSET_COOLDOWN["S2"][0] * 2),
                int(OFFSET_COOLDOWN["S2"][1] * 2),
            ),
            "S3": (
                int(OFFSET_COOLDOWN["S3"][0] * 2),
                int(OFFSET_COOLDOWN["S3"][1] * 2),
            ),
        },
        "health_step_dir": 1,
    },
    2: {
        "health": (int(OFFSET_HEALTH[0] * 2) + 40, int(OFFSET_HEALTH[1] * 2) + 7),
        "resist": (int(OFFSET_RESIST[0] * 2) + 112, int(OFFSET_RESIST[1] * 2) - 59),
        "ass": (int(OFFSET_ASS[0] * 2) + 172, int(OFFSET_ASS[1] * 2) - 14),
        "ass2_dx": -48,
        "cooldown": {
            "S1": (
                int(OFFSET_COOLDOWN["S1"][0] * 2) - 15,
                int(OFFSET_COOLDOWN["S1"][1] * 2),
            ),
            "S2": (
                int(OFFSET_COOLDOWN["S2"][0] * 2) - 15,
                int(OFFSET_COOLDOWN["S2"][1] * 2),
            ),
            "S3": (
                int(OFFSET_COOLDOWN["S3"][0] * 2) - 15,
                int(OFFSET_COOLDOWN["S3"][1] * 2),
            ),
        },
        "health_step_dir": 1,
    },
    3: {
        "health": (int(OFFSET_HEALTH[0] * 2) + 56, int(OFFSET_HEALTH[1] * 2) + 7 + 135),
        "resist": (int(OFFSET_RESIST[0] * 2) + 21, int(OFFSET_RESIST[1] * 2) - 46),
        "ass": (int(OFFSET_ASS[0] * 2) + 2, int(OFFSET_ASS[1] * 2) - 14 - 146),
        "ass2_dx": -48,
        "cooldown": {
            "S1": (
                int(OFFSET_COOLDOWN["S1"][0] * 2),
                int(OFFSET_COOLDOWN["S1"][1] * 2) - 127,
            ),
            "S2": (
                int(OFFSET_COOLDOWN["S2"][0] * 2),
                int(OFFSET_COOLDOWN["S2"][1] * 2) - 127,
            ),
            "S3": (
                int(OFFSET_COOLDOWN["S3"][0] * 2),
                int(OFFSET_COOLDOWN["S3"][1] * 2) - 127,
            ),
        },
        "health_step_dir": 1,
    },
    4: {
        "health": (int(OFFSET_HEALTH[0] * 2) + 40, int(OFFSET_HEALTH[1] * 2) + 7 + 135),
        "resist": (int(OFFSET_RESIST[0] * 2) + 112, int(OFFSET_RESIST[1] * 2) - 46),
        "ass": (int(OFFSET_ASS[0] * 2) + 172 - 48, int(OFFSET_ASS[1] * 2) - 14 - 146),
        "ass2_dx": +48,
        "cooldown": {
            "S1": (
                int(OFFSET_COOLDOWN["S1"][0] * 2) - 15,
                int(OFFSET_COOLDOWN["S1"][1] * 2) - 127,
            ),
            "S2": (
                int(OFFSET_COOLDOWN["S2"][0] * 2) - 15,
                int(OFFSET_COOLDOWN["S2"][1] * 2) - 127,
            ),
            "S3": (
                int(OFFSET_COOLDOWN["S3"][0] * 2) - 15,
                int(OFFSET_COOLDOWN["S3"][1] * 2) - 127,
            ),
            # AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA finallyy
        },
        "health_step_dir": 1,
    },
}


class HUD:
    def __init__(self, id_player):
        SCALE = 2

        def _subFunctionREALLYusefull(s):
            # function reaaally usefull (avoid repetition)
            w, h = s.get_size()
            return pyg.transform.scale(s, (int(w * SCALE), int(h * SCALE)))

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

        self.interface = _subFunctionREALLYusefull(
            self.all_picture["HUD-PLAYER-INTERFACE-Sheet"].subsurface(
                (id_player - 1) * 144, 0, 144, 96
            )
        )

        self.cooldown = {"S1": [], "S2": [], "S3": []}
        self.cooldownOKK = {"S1": [], "S2": [], "S3": []}
        self.health = []

        self.sub_health1_red = _subFunctionREALLYusefull(
            self.all_picture["HUD-HP-CORE-Sheet"].subsurface(
                1 * 16, 0, SIZE_FRAMES_HP_CORE, 18
            )
        )
        self.sub_health2_red = _subFunctionREALLYusefull(
            self.all_picture["HUD-HP-CORE-Sheet"].subsurface(
                2 * 16, 0, SIZE_FRAMES_HP_CORE, 18
            )
        )
        self.sub_health1_blue = _subFunctionREALLYusefull(
            self.all_picture["HUD-HP-CORE-Sheet"].subsurface(
                4 * 16, 0, SIZE_FRAMES_HP_CORE, 18
            )
        )
        self.sub_health2_blue = _subFunctionREALLYusefull(
            self.all_picture["HUD-HP-CORE-Sheet"].subsurface(
                5 * 16, 0, SIZE_FRAMES_HP_CORE, 18
            )
        )
        self.sub_health1_green = _subFunctionREALLYusefull(
            self.all_picture["HUD-HP-CORE-Sheet"].subsurface(
                7 * 16, 0, SIZE_FRAMES_HP_CORE, 18
            )
        )

        self.sub_health2_green = _subFunctionREALLYusefull(
            self.all_picture["HUD-HP-CORE-Sheet"].subsurface(
                8 * 16, 0, SIZE_FRAMES_HP_CORE, 18
            )
        )
        self.sub_health3_green = _subFunctionREALLYusefull(
            self.all_picture["HUD-HP-CORE-Sheet"].subsurface(
                9 * 16, 0, SIZE_FRAMES_HP_CORE, 18
            )
        )

        self.ass = {"OK": [], "WAIT": []}
        self.resist = []

        self.id_player = id_player
        self.scaled_w = int(144 * SCALE)
        self.scaled_h = int(96 * SCALE)

        for k in [6, 3, 0]:
            for j in range(6):
                chunk = _subFunctionREALLYusefull(
                    self.all_picture["HUD-HP-CORE-Sheet"].subsurface(
                        k * SIZE_FRAMES_HP_CORE, 0, SIZE_FRAMES_HP_CORE, 18
                    )
                )
                self.health.append(chunk)

        for i in range(TOTAL_CHUNK_ASS_WAIT):
            chunk = _subFunctionREALLYusefull(
                self.all_picture["HUD-ASS-WAIT-Sheet"].subsurface(
                    i * SIZE_FRAMES_ASS_WAIT, 0, SIZE_FRAMES_ASS_WAIT, 7
                )
            )
            # nice ass
            self.ass["WAIT"].append(chunk)

        for i in range(TOTAL_CHUNK_ASS_OK):
            chunk = _subFunctionREALLYusefull(
                self.all_picture["HUD-ASS-OK-Sheet"].subsurface(
                    i * SIZE_FRAMES_ASS_OK, 0, SIZE_FRAMES_ASS_OK, 7
                )
            )
            self.ass["OK"].append(chunk)

        for j in range(1, 4):
            for i in range(TOTAL_CHUNK_COOLDOWN_WAIT):
                chunk = _subFunctionREALLYusefull(
                    self.all_picture[f"HUD-S{j}-WAIT-Sheet"].subsurface(
                        i * SIZE_CHUNK_COOLDOWN, 0, SIZE_CHUNK_COOLDOWN, 12
                    )
                )
                self.cooldown[f"S{j}"].append(chunk)

        for j in range(1, 4):
            for i in range(TOTAL_CHUNK_COOLDOWN_OK):
                chunk = _subFunctionREALLYusefull(
                    self.all_picture[f"HUD-S{j}-OK-Sheet"].subsurface(
                        i * SIZE_CHUNK_COOLDOWN, 0, SIZE_CHUNK_COOLDOWN, 12
                    )
                )
                self.cooldownOKK[f"S{j}"].append(chunk)

        for i in range(TOTAL_CHUNK_RESIST):
            chunk = _subFunctionREALLYusefull(
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
        self.skillCooldownDuration = {"S1": 0, "S2": 0, "S3": 0}
        self.skillCooldownRemaining = {"S1": 0, "S2": 0, "S3": 0}
        self.skillAnimFrame = {"S1": 0, "S2": 0, "S3": 0}
        self.skillAnimTimer = {"S1": 0, "S2": 0, "S3": 0}

        self.assState = "OK"
        self.assFrame = 0
        self.assAnimTimer = 0
        self.assCooldownRemaining = 0
        self.assCooldownDuration = 0

        self.scale = SCALE
        self.currentResist = 0

        self._portrait = None

    def set_portrait(self, char_num):
        try:
            sheet = pyg.image.load(
                f"assets/sprites/Character-{char_num}/IDLE-Sheet.png"
            ).convert_alpha()
            frame = sheet.subsurface(0, 0, 40, 40)
            self._portrait = pyg.transform.scale(frame, (PORTRAIT_SIZE, PORTRAIT_SIZE))
        except Exception as e:
            print_warning(f"Portrait char {char_num} introuvable: {e}")
            self._portrait = None

    def update(self, dt):
        for skill in ["S1", "S2", "S3"]:
            if self.skillState[skill] == "WAIT":
                self.skillCooldownRemaining[skill] -= dt
                if self.skillCooldownRemaining[skill] <= 0:
                    self.skillCooldownRemaining[skill] = 0
                    self.skillState[skill] = "OK"
                    self.skillAnimFrame[skill] = 0
                    self.skillAnimTimer[skill] = 0
                else:
                    progress = 1 - (
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
                    self.skillAnimTimer[skill] = 0
                    self.skillAnimFrame[skill] = (
                        self.skillAnimFrame[skill] + 1
                    ) % TOTAL_CHUNK_COOLDOWN_OK

        if self.assState == "WAIT":
            self.assCooldownRemaining -= dt
            if self.assCooldownRemaining <= 0:
                self.assCooldownRemaining = 0
                self.assState = "OK"
                self.assFrame = 0
                self.assAnimTimer = 0
            else:
                progress = 1 - (self.assCooldownRemaining / self.assCooldownDuration)
                self.assFrame = min(
                    int(progress * TOTAL_CHUNK_ASS_WAIT),
                    TOTAL_CHUNK_ASS_WAIT - 1,
                )
        else:
            self.assAnimTimer += dt
            if self.assAnimTimer >= ANIM_SPEED_ASS:
                self.assAnimTimer = 0
                self.assFrame = (self.assFrame + 1) % TOTAL_CHUNK_ASS_OK

        self.deltaTimeS1 = self.skillCooldownRemaining["S1"]
        self.deltaTimeS2 = self.skillCooldownRemaining["S2"]
        self.deltaTimeS3 = self.skillCooldownRemaining["S3"]

    def setResist(self, value):
        self.currentResist = max(0, min(value, TOTAL_CHUNK_RESIST - 1))

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

    def draw(self, surface, x, y):
        # Dreaw the hud with all teh subfunctions made for it
        surface.blit(self.interface, (x, y))
        self._drawPortrait(surface, x, y)
        self._drawHealth(surface, x, y)
        self._drawCooldowns(surface, x, y)
        self._drawAss(surface, x, y)
        self._drawResist(surface, x, y)

    def _drawPortrait(self, surface, x, y):
        if self._portrait is None:
            return
        ox, oy = PORTRAIT_OFFSETS[self.id_player]
        surface.blit(self._portrait, (x + ox, y + oy))

    def _drawHealth(self, surface, x, y):

        tx, ty = OFFSETS_PAR_PLAYER[self.id_player]["health"]

        step = self.health[0].get_width() - round(self.scale)
        barStart = self.currentHealth - (self.currentHealth % 6)
        chunksInBar = (self.currentHealth % 6) + 1
        for i in range(chunksInBar):
            if i == chunksInBar - 1 and self.healthPartial > 0:
                continue  # chunk partiel → rien (image pleine ou rien)
            j = barStart + i
            surface.blit(self.health[j], (x + tx + i * step, y + ty))

    def _drawCooldowns(self, surface, x, y):

        for skill in ["S1", "S2", "S3"]:
            tx, ty = OFFSETS_PAR_PLAYER[self.id_player]["cooldown"][skill]
            frame = (
                self.cooldown[skill][self.skillAnimFrame[skill]]
                if self.skillState[skill] == "WAIT"
                else self.cooldownOKK[skill][self.skillAnimFrame[skill]]
            )
            surface.blit(frame, (x + tx, y + ty))

    def _drawAss(self, surface, x, y):
        c = OFFSETS_PAR_PLAYER[self.id_player]
        tx, ty = c["ass"]
        d2 = c["ass2_dx"]
        frame = (
            self.ass["WAIT"][self.assFrame]
            if self.assState == "WAIT"
            else self.ass["OK"][self.assFrame]
        )
        surface.blit(frame, (x + tx, y + ty))
        surface.blit(frame, (x + tx + d2, y + ty))

    def _drawResist(self, surface, x, y):

        tx, ty = OFFSETS_PAR_PLAYER[self.id_player]["resist"]
        gap = 0
        for frame in self.resist:
            surface.blit(frame, (x + tx + gap, y + ty))
            gap += 56

    def startCooldown(self, skill, duration):
        self.skillState[skill] = "WAIT"

        self.skillCooldownDuration[skill] = duration
        self.skillCooldownRemaining[skill] = duration

        self.skillAnimFrame[skill] = 0
        self.skillAnimTimer[skill] = 0

    def isSkillReady(self, skill):
        return self.skillState[skill] == "OK"

    def startAssCooldown(self, duration):

        self.assState = "WAIT"
        self.assCooldownDuration = duration
        self.assCooldownRemaining = duration
        self.assFrame = 0
        self.assAnimTimer = 0

    def isAssReady(self):
        return self.assState == "OK"

    def setHealth(self, value):
        self.currentHealth = max(0, min(value, TOTAL_CHUNK_HEALTH - 1))
        self.healthPartial = 0
        self.verifyColorBar()

    def heal(self, amount):
        if self.healthPartial > 0:
            recover = min(amount, self.healthPartial)
            self.healthPartial -= recover
            amount -= recover

        fu = amount // 3
        remainder = amount % 3

        self.currentHealth = min(self.currentHealth + fu, TOTAL_CHUNK_HEALTH - 1)

        if remainder > 0:
            self.healthPartial = max(0, self.healthPartial - remainder)

        self.verifyColorBar()

    def DealsDamage(self, damage=1):
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

    def verifyColorBar(self):
        # Verify the color of the bar for the display
        red = 12
        blue = 6
        green = 0

        if self.currentHealth >= red:
            self.currentBarColor = "red"
        elif self.currentHealth >= blue:
            self.currentBarColor = "blue"
        elif self.currentHealth >= green:
            self.currentBarColor = "green"

    def isDead(self):
        # 1 if death, 0 otherwise
        return self.currentHealth <= 0 and self.healthPartial >= 3

    def getHealthPercent(self):
        totalPoints = (self.currentHealth + 1) * 3 - self.healthPartial
        return totalPoints / (TOTAL_CHUNK_HEALTH * 3)

    def updateFromServer(self, data):
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
                        self.skillAnimFrame[skill] = 0
                        self.skillAnimTimer[skill] = 0
        if "assist" in data:
            if data["assist"] == "WAIT":
                assDuration = data.get("assistDuration", self.assCooldownDuration)
                assRemaining = data.get("assistRemaining", self.assCooldownRemaining)
                if self.assState == "OK":
                    self.startAssCooldown(assDuration)
                self.assCooldownRemaining = assRemaining
            else:
                self.assState = "OK"
                self.assCooldownRemaining = 0
                self.assFrame = 0
                self.assAnimTimer = 0

        self.verifyColorBar()

    def toNetworkData(self):

        # return a dict for the server
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
        # Reset the variables and stats of the hud
        self.currentHealth = TOTAL_CHUNK_HEALTH - 1
        self.healthPartial = 0
        self.currentBarColor = "red"

        self.assState = "OK"
        self.assFrame = 0
        self.assAnimTimer = 0
        self.assCooldownRemaining = 0

        for skill in ["S1", "S2", "S3"]:
            self.skillState[skill] = "OK"
            self.skillCooldownDuration[skill] = 0
            self.skillCooldownRemaining[skill] = 0
            self.skillAnimFrame[skill] = 0
            self.skillAnimTimer[skill] = 0

        self.deltaTimeS1 = 0
        self.deltaTimeS2 = 0
        self.deltaTimeS3 = 0


def _load_spec_hud_sheets(self):
    try:
        import pygame as pyg

        sht_chrg = pyg.image.load(
            "assets/sprites/Character-4/HUD-SPEC-4-CHARGE-Sheet.png"
        ).convert_alpha()
        fw = CHRG_SHEET_W // CHRG_FRAMES
        self._chrg_frms = [
            sht_chrg.subsurface((i * fw, 0, fw, CHRG_SHEET_H))
            for i in range(CHRG_FRAMES)
        ]

        sht_wtr = pyg.image.load(
            "assets/sprites/Character-5/HUD-SPEC-6-WTR-Sheet.png"
        ).convert_alpha()
        fw2 = WTR_SHEET_W // WTR_FRAMES
        self._wtr_frms = [
            sht_wtr.subsurface((i * fw2, 0, fw2, WTR_SHEET_H))
            for i in range(WTR_FRAMES)
        ]

        sht_sda = pyg.image.load(
            "assets/sprites/Character-5/HUD-SPEC-6-SODA-Sheet.png"
        ).convert_alpha()
        fw3 = SDA_SHEET_W // SDA_FRAMES
        self._sda_frms = [
            sht_sda.subsurface((i * fw3, 0, fw3, SDA_SHEET_H))
            for i in range(SDA_FRAMES)
        ]

        self._spec_hud_loaded = True
    except Exception as e:
        from ui.console import print_error

        print_error(f"Erreur chargement spec HUD: {e}")
        self._spec_hud_loaded = False


def _draw_char4_hud(self, surface, player_id):
    if not self._spec_hud_loaded or not self._chrg_frms:
        return
    pos = SPEC_HUD_POSITIONS.get(player_id)
    if not pos:
        return
    x, y = pos
    chrgs = getattr(self.active_char, "chrgs", 0)
    frm_idx = max(0, min(CHRG_FRAMES - 1, chrgs))
    surface.blit(self._chrg_frms[frm_idx], (x, y))


def _draw_char5_hud(self, surface, player_id):
    if not self._spec_hud_loaded or not self._wtr_frms or not self._sda_frms:
        return
    pos = SPEC_HUD_POSITIONS.get(player_id)
    if not pos:
        return
    x, y = pos
    wtr = getattr(self.active_char, "wtr_cns", 4)
    sda = getattr(self.active_char, "sda_cns", 4)

    wtr_idx = max(0, min(WTR_FRAMES - 1, WTR_FRAMES - 1 - wtr))
    sda_idx = max(0, min(SDA_FRAMES - 1, SDA_FRAMES - 1 - sda))

    surface.blit(self._wtr_frms[wtr_idx], (x, y))
    gap = -SDA_ROW_GAP if player_id in (3, 4) else SDA_ROW_GAP
    surface.blit(self._sda_frms[sda_idx], (x, y + gap))
