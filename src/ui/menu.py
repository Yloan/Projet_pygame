import json
import math
import os
import sys
from email import message

import pygame as pyg

import game.characters as player_module
from ui import Buttons as ObjButton
from ui.console import (
    print_debug,
    print_error,
    print_warning,
    # Le reste on s'en fout, ca sera probablement pas utilisé (au pire on import tout)
)
from utils.paths import get_asset_path

from . import animated_button, button

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
BUTTON_SCALE = 2

TMP_NUBER_OF_ASSETS_VARIABLES_HERE = 5

MAPS_NOT_IMPLEMENTED_YET = set()


class Menu:
    def __init__(self, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, fullscreen=False):
        # WINDOW CONFIGURATION
        self.width = width
        self.height = height
        self.fullscreen = fullscreen
        # PLAYER INITIALIZATION
        self.player = player_module.Furnace()
        # MENU STATE VARIABLES
        self.etat = "menu"
        self.game_started = False
        self.menu_state = "main"
        self.number_players = 0
        self.number_bot = 0
        self.character_1 = 0
        self.character_2 = 0
        self.character_3 = 0

        # PYGAME INITIALIZATION
        pyg.init()

        # Display setup
        flags = pyg.FULLSCREEN if self.fullscreen else 0
        self.screen = pyg.display.set_mode((self.width, self.height), flags)
        pyg.display.set_caption("Jeu Multijoueur")
        self.c = pyg.time.Clock()

        # FONT AND COLOR SETUP
        self.font = pyg.font.SysFont("arialblack", 40)
        self.middle_font = pyg.font.SysFont("arialblack", 20)
        self.mini_font = pyg.font.SysFont("arialblack", 10)

        self.TEXT_COL = (255, 255, 255)
        self.TEXT_COL2 = (255, 0, 0)

        # LOAD MENU BACKGROUNDS
        self.wallpaper = pyg.image.load(
            "assets/buttons/21-MENUS/MAIN MENU-Sheet.png"
        ).convert_alpha()
        self.wallpaper = pyg.transform.scale(self.wallpaper, (self.width, self.height))
        self.choice_chracters = pyg.image.load(
            "assets/wallpapers/menewer-Sheet.png"
        ).convert_alpha()
        self.choice_chracters = pyg.transform.scale(
            self.choice_chracters, (self.width, self.height)
        )

        # PLAY BUTTON FRAMES
        play_button = ObjButton.PlayButton()
        self.play_button_frames = play_button.play_button_frames
        self.play_button_frames_pressed = play_button.play_button_frames_pressed
        self.play_button_frames_unpressed = play_button.play_button_frames_unpressed

        # SETTINGS BUTTON FRAMES
        settings_button = ObjButton.OptionsButton()
        self.settings_button_frames = settings_button.settings_button_frames
        self.settings_button_frames_pressed = (
            settings_button.settings_button_frames_pressed
        )
        self.settings_button_frames_unpressed = (
            settings_button.settings_button_frames_unpressed
        )

        # EXIT BUTTON FRAMES
        exit_button = ObjButton.ExitButton()
        self.exit_button_frames = exit_button.exit_button_frames
        self.exit_button_frames_pressed = exit_button.exit_button_frames_pressed
        self.exit_button_frames_unpressed = (
            exit_button.exit_button_frames_unpressed
        )  # empty list

        # Settings submenu buttons
        video_img = pyg.image.load("assets/buttons/button_video.png").convert_alpha()
        audio_img = pyg.image.load("assets/buttons/button_audio.png").convert_alpha()
        keys_img = pyg.image.load("assets/buttons/button_keys.png").convert_alpha()

        # Player count selection buttons
        zero_player_img = pyg.image.load(
            "assets/buttons/button_zero_player.png"
        ).convert_alpha()
        one_player_img = pyg.image.load(
            "assets/buttons/button_one_player.png"
        ).convert_alpha()
        two_players_img = pyg.image.load(
            "assets/buttons/button_two_players.png"
        ).convert_alpha()
        three_players_img = pyg.image.load(
            "assets/buttons/button_trhee_players.png"
        ).convert_alpha()
        four_players_img = pyg.image.load(
            "assets/buttons/button_four_players.png"
        ).convert_alpha()
        back_char_img = pyg.transform.scale(
            pyg.image.load(
                "assets/buttons/Back_selection_character.png"
            ).convert_alpha(),
            (63, 57),
        )
        # IMAGES FOR SESSION INTERFACE
        self.bg_session = pyg.image.load(
            "assets/Menus_assets/sessions_section/Browse_Sessions.png"
        ).convert_alpha()
        # self.bar_session = pyg.image.load("assets/Menus_assets/sessions_section/BAR.png").convert_alpha()
        # self.bot_session = pyg.image.load("assets/Menus_assets/sessions_section/BOT.png").convert_alpha()
        self.button_session = pyg.image.load(
            "assets/Menus_assets/sessions_section/Button.png"
        ).convert_alpha()
        # self.player_session = pyg.image.load("assets/Menus_assets/sessions_section/player.png").convert_alpha()
        # self.splash_session = pyg.image.load("assets/Menus_assets/sessions_section/splash.png").convert_alpha()
        # self.star_bar_session = pyg.image.load("assets/Menus_assets/sessions_section/Star_Bar.png").convert_alpha()

        # LOAD CHARACTER SELECTION IMAGES
        image_ch = []
        for i in range(5):
            # 24 * 22 px
            path = get_asset_path("Menus_assets")
            Img = pyg.image.load(path + "/SELECT-ICONES-Sheet.png")
            Img = Img.subsurface(i * 24, 0, 24, 22)
            Img = pyg.transform.scale(Img, (143, 107))
            image_ch.append(Img)

        # Add the character 3, 4 & 5 which is not at a good index in the file
        _icones_sheet = pyg.image.load(
            get_asset_path("Menus_assets") + "/SELECT-ICONES-Sheet.png"
        ).convert_alpha()
        _icones_h = _icones_sheet.get_height()

        # Character 3 — frame 6 of SELECT-ICONES-Sheet
        Img = _icones_sheet.subsurface(6 * 24, 0, 24, _icones_h)
        Img = pyg.transform.scale(Img, (143, 107))
        image_ch.insert(2, Img)

        # Character 4
        i = 4
        Img = pyg.image.load(
            get_asset_path("characters_selection", f"Character_{i}.png")
        ).convert_alpha()
        Img = pyg.transform.scale(Img, (143, 107))
        image_ch.insert(3, Img)

        # Character 5 — frame 7 of SELECT-ICONES-Sheet
        Img = _icones_sheet.subsurface(7 * 24, 0, 24, _icones_h)
        Img = pyg.transform.scale(Img, (143, 107))
        image_ch.insert(4, Img)

        self.image_ch = image_ch
        self.char_p_scale = 9.5
        # self.char_p_scale = 1

        ___size_frame_idle_ = 40
        self._idle_preview_frames = {}
        self._idle_anim_i = {}
        self._idle_anim_accum = {}
        self._idle_anim_last_tick = pyg.time.get_ticks()

        for __i___ in range(1, TMP_NUBER_OF_ASSETS_VARIABLES_HERE + 1):
            _path = get_asset_path("sprites", f"Character-{__i___}", "IDLE-Sheet.png")
            _sheet = pyg.image.load(_path)
            _count = _sheet.get_width() // ___size_frame_idle_
            _frames = [
                _sheet.subsurface(
                    (
                        _j * ___size_frame_idle_,
                        0,
                        ___size_frame_idle_,
                        ___size_frame_idle_,
                    )
                )
                for _j in range(_count)
            ]
            self._idle_preview_frames[__i___] = _frames
            self._idle_anim_i[__i___] = 0
            self._idle_anim_accum[__i___] = 0

        # CREATE BUTTON INSTANCES
        self.play_button = animated_button.AnimatedButton(
            self.center_x(self.play_button_frames[0], 1.5),
            390,
            frames_idle=self.play_button_frames,
            frames_pressed=self.play_button_frames_pressed,
            frames_unpressed=self.play_button_frames_unpressed,
            scale=BUTTON_SCALE,
            animation_speed=8,
        )
        self.exit_button = animated_button.AnimatedButton(
            self.center_x(self.exit_button_frames[0], 1.5),
            510,
            frames_idle=self.exit_button_frames,
            frames_pressed=self.exit_button_frames_pressed,
            frames_unpressed=self.exit_button_frames_unpressed,  # empty → no release anim
            scale=2,
            animation_speed=8,
        )
        # Each sub-menu gets its OWN back-button instance so their state machines
        # never interfere with each other or with the main-menu exit button.
        self.back_btn_settings = self._make_back_btn()
        self.back_btn_sessions = self._make_back_btn()
        self.back_btn_play_menu = self._make_back_btn()
        self.back_btn_one_player = self._make_back_btn()
        self.back_btn_two_players = self._make_back_btn()
        self.back_btn_three_players = self._make_back_btn()
        self.video_button = button.Button(
            self.center_x(video_img, 1) - 350, 350, video_img, 1
        )
        self.audio_button = button.Button(
            self.center_x(audio_img, 1), 350, audio_img, 1
        )
        self.keys_button = button.Button(
            self.center_x(keys_img, 1) + 330, 350, keys_img, 1
        )
        self.zero_player_button = button.Button(
            self.center_x(zero_player_img, -0.5) + 150, 350, zero_player_img, 0.3
        )

        self.one_player_button = button.Button(
            self.center_x(one_player_img, 2) - 150, 350, one_player_img, 1
        )
        self.two_players_button = button.Button(
            self.center_x(two_players_img, 2), 350, two_players_img, 1
        )
        self.three_players_button = button.Button(
            self.center_x(three_players_img, -0.5), 350, three_players_img, 1
        )
        self.four_players_button = button.Button(
            self.center_x(four_players_img, -0.5) + 150, 350, four_players_img, 1
        )
        # Back arrow button in character selection screens
        self.Back_selection_character = button.Button(37, 6, back_char_img, 1)

        # # Sessions buttons
        self.join_button = button.Button(
            x=691, y=231, image=self.button_session, scale=0.25
        )

        self.create_session_button = button.Button(
            x=655, y=400, image=self.button_session, scale=0.5
        )

        # Colonne gauche
        self.character_1_button = button.Button(358, 213, image_ch[0], 1)
        self.character_2_button = button.Button(570, 213, image_ch[1], 1)

        # Colonne droite
        self.character_3_button = button.Button(781, 213, image_ch[2], 1)
        self.character_4_button = button.Button(420, 404, image_ch[3], 1)

        # Centre bas
        self.character_5_button = button.Button(713, 404, image_ch[4], 1)

        # character choosen
        character_choosen_img = pyg.image.load(
            "assets/buttons/character_choosen.png"
        ).convert_alpha()
        self.character_choosen_button = button.Button(
            self.center_x(character_choosen_img, -11), 100, character_choosen_img, 10
        )

        # start button — pixel-art Play button (scaled ×5 for crisp rendering)
        _play_raw = pyg.image.load(
            get_asset_path("characters_selection", "Button_Play.png")
        ).convert_alpha()
        _play_scale = 4
        _play_img = pyg.transform.scale(
            _play_raw,
            (_play_raw.get_width() * _play_scale, _play_raw.get_height() * _play_scale),
        )
        # Centred in the bottom-centre square, lowered to sit inside it properly.
        _play_x = (self.width - _play_img.get_width()) // 2
        _play_y = 596
        self.start_button = button.Button(_play_x, _play_y, _play_img, scale=1)
        # VARIABLES SESSIONS
        self.sessions = []
        self.scroll_y = 0
        self.sessionPending = None
        self.input_box = InputBox(
            100, 100, 140, 32, button_session=self.button_session, menu=self
        )

        # VARIABLES CHARACTERS SELECTIONS
        self.number_players = 0
        self.number_bot = 0
        self.CurrentPlayer_id = 1  # 1 by default
        self.slot_positions = {
            1: (64, 125),
            2: (64, 442),
            3: (1036, 125),
            4: (1036, 442),
        }

        self.preview_center_pos = (WINDOW_WIDTH // 2 - 100, 200)

        self.current_session_name = None
        self.players_characters = {
            1: [None, None, None],
            2: [None, None, None],
            3: [None, None, None],
            4: [None, None, None],
        }

        self.players_ready = {  # Dict pour voir c qui qui a cliqué
            1: False,
            2: False,
            3: False,
            4: False,
        }
        self.p_character_submission = None
        self.p_character_update = False
        self.p_unready = False
        self.p_leave_session = None
        self.p_join_session = None

        self.__mouse_prev = False

        self._arrow_cursor = {1: "main", 2: "main", 3: "main", 4: "main"}
        self._arrow_pos = {}
        self._arrow_target = {}
        self._arrow_bob = 0
        self._idle_click_rects = {}

        # Selection cursor image
        try:
            _csr_raw = pyg.image.load(
                get_asset_path("Menus_assets", "SELECT-CURSOR.png")
            ).convert_alpha()
            self._select_cursor_img = pyg.transform.scale(_csr_raw, (44, 34))
        except Exception:
            self._select_cursor_img = None

        _base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.slot_maps_selection = {
            1: (355, 285),
            2: (558, 285),
            3: (759, 285),
        }
        self.width_slots_map = 159
        self.height_slots_map = 135
        self.maps_not_implemented_yet = set()

        try:
            _bg_raw = pyg.image.load(
                os.path.join(_base, "assets", "maps", "maps_selection.png")
            )
            self.maps_selection_bg = pyg.transform.scale(
                _bg_raw, (self.width, self.height)
            )
        except Exception:
            self.maps_selection_bg = self.choice_chracters

        self.map_slot_previews = {}
        try:
            _forest = pyg.image.load(
                os.path.join(_base, "assets", "maps", "FOREST-WHOLE.png")
            )
            self.map_slot_previews[1] = pyg.transform.scale(
                _forest, (self.width_slots_map, self.height_slots_map)
            )
        except Exception:
            pass
        try:
            _desert = pyg.image.load(
                os.path.join(_base, "assets", "maps", "map_2", "map-2.png")
            )
            self.map_slot_previews[2] = pyg.transform.scale(
                _desert, (self.width_slots_map, self.height_slots_map)
            )
        except Exception:
            pass
        try:
            _grotte = pyg.image.load(
                os.path.join(_base, "assets", "maps", "map_3", "map-3.png")
            )
            self.map_slot_previews[3] = pyg.transform.scale(
                _grotte, (self.width_slots_map, self.height_slots_map)
            )
        except Exception:
            pass

        self.rects_img_maps = {
            i: pyg.Rect(
                self.slot_maps_selection[i],
                (self.width_slots_map, self.height_slots_map),
            )
            for i in self.slot_maps_selection
            if i not in self.maps_not_implemented_yet
        }

        self.map_player_votes = {}
        self.PLAYER_COLORS = {
            1: (220, 60, 60),
            2: (60, 100, 220),
            3: (60, 200, 60),
            4: (220, 200, 40),
        }

    def handle_session_menu(self):
        # Gère l'état du menu des sessions
        self.bg_session = pyg.transform.scale(
            self.bg_session, (self.width, self.height)
        )
        self.screen.blit(self.bg_session, (0, 0))

        zone_visible = pyg.Rect(300, 200, 750, 320)
        self.screen.set_clip(zone_visible)

        for i, session in enumerate(self.sessions):
            session.draw_session(session.y - self.scroll_y)

        self.screen.set_clip(None)

        if self.create_session_button.draw(self.screen):
            print("Session created")
            # new_session = Session(self)

            self.menu_state = "creation_parameters_session_menu"

            # calculated_y = 79 + (len(self.sessions) * new_session.gap)
            # new_session.y = calculated_y

            # self.sessions.append(new_session)

        self.draw_text(
            text="Create session", font=self.middle_font, text_col="Black", x=735, y=480
        )
        if self.back_btn_sessions.draw(self.screen):
            self.menu_state = "main"

    def draw_center_preview(self, char_index):
        try:
            i = int(char_index)
        except Exception:
            i = 0
        if i and 1 <= i <= len(self.image_ch):
            self._update_IDLE_p()
            px, py = self.preview_center_pos
            self._blit_largeChar(i, px, py, scale_factor=10)

    def update_sessions_from_server(self, sessions_json):
        try:
            sessions_data = json.loads(sessions_json)
            self.sessions = []

            # Recreate Session objects from server data
            for idx, session_data in enumerate(sessions_data):
                session = Session.from_dict(session_data, self)
                # Recalculate Y position based on index
                session.y = 79 + (idx * session.gap)
                self.sessions.append(session)

            print(f"Sessions mises à jour du serveur: {len(self.sessions)} sessions")
        except json.JSONDecodeError as e:
            print(f"Erreur de décodage JSON des sessions: {e}")
        except Exception as e:
            print(f"Erreur lors de la mise à jour des sessions: {e}")

    def update_player_character(self, player_id, character_1, character_2, character_3):
        if 1 <= player_id <= 4:
            self.players_characters[player_id] = [character_1, character_2, character_3]
            from ui.console import print_network

            print_network(
                f"Joueur {player_id} a sélectionné les personnages {character_1}, {character_2}, {character_3}"
            )

    def update_player_ready(self, player_id):
        if 1 <= player_id <= 4:
            self.players_ready[player_id] = True
            from ui.console import print_network

            print_network(f"Joueur {player_id} est READY !")

    def center_x(self, image, scale=1):
        w = int(image.get_width() * scale)
        return (self.width - w) // 2

    def draw_text(self, text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        self.screen.blit(img, (x, y))

    def draw_text_center(self, text, font, text_col, y):
        img = font.render(text, True, text_col)
        x = (self.width - img.get_width()) // 2
        self.screen.blit(img, (x, y))

    def _make_back_btn(self, y=580):
        """Return a fresh AnimatedButton using the exit animation, for back/return actions."""
        return animated_button.AnimatedButton(
            self.center_x(self.exit_button_frames[0], 1.5),
            y,
            frames_idle=self.exit_button_frames,
            frames_pressed=self.exit_button_frames_pressed,
            frames_unpressed=self.exit_button_frames_unpressed,
            scale=2,
            animation_speed=8,
        )

    def handle_main_menu(self):
        # Gère l'état du menu principal

        self.screen.blit(self.wallpaper, (0, 0))
        # Then draw animated buttons
        if self.play_button.draw(self.screen):
            self.menu_state = "play"
        if self.exit_button.draw(self.screen):
            pyg.quit()
            sys.exit(0)

    def handle_settings_menu(self):
        # Gère l'état du menu paramètres
        if self.video_button.draw(self.screen):
            print("Video Settings")
        if self.audio_button.draw(self.screen):
            print("Audio Settings")
        if self.keys_button.draw(self.screen):
            print("Keys Settings")
        if self.back_btn_settings.draw(self.screen):
            self.menu_state = "main"

    def handle_play_menu(self):
        self.draw_text_center(
            "Select the number",
            self.font,
            self.TEXT_COL2,
            20,
        )
        self.draw_text_center(
            "of players",
            self.font,
            self.TEXT_COL2,
            65,
        )

        # tmp = ["three", "two", "one"]
        # self.menu_state = f"{tmp[self.number_bot - 1]}{'_player' if self.number_bot == 3 else '_players'}"
        # print_debug(self.menu_state)
        self.menu_state = "choice_characters_1"
        if self.back_btn_play_menu.draw(self.screen):
            self.menu_state = "play"

    def handle_one_player_menu(self):
        self.draw_text_center(
            "Select the number of bots", self.font, self.TEXT_COL2, 50
        )
        if self.one_player_button.draw(self.screen):
            self.menu_state = "choice_characters_1"
            self.number_bot = 1
        if self.two_players_button.draw(self.screen):
            self.menu_state = "choice_characters_1"
            self.number_bot = 2
        if self.three_players_button.draw(self.screen):
            self.menu_state = "choice_characters_1"
            self.number_bot = 3
        if self.back_btn_one_player.draw(self.screen):
            self.menu_state = "play"

    def handle_two_players_menu(self):
        self.draw_text_center(
            "Select the number of bots", self.font, self.TEXT_COL2, 50
        )
        if self.zero_player_button.draw(self.screen):
            self.menu_state = "choice_characters_1"
            self.number_bot = 0
        if self.one_player_button.draw(self.screen):
            self.menu_state = "choice_characters_1"
            self.number_bot = 1
        if self.two_players_button.draw(self.screen):
            self.menu_state = "choice_characters_1"
            self.number_bot = 2
        if self.back_btn_two_players.draw(self.screen):
            self.menu_state = "play"

    def handle_three_players_menu(self):
        self.draw_text_center(
            "Select the number of bots", self.font, self.TEXT_COL2, 50
        )
        if self.zero_player_button.draw(self.screen):
            self.menu_state = "choice_characters_1"
            self.number_bot = 0
        if self.one_player_button.draw(self.screen):
            self.menu_state = "choice_characters_1"
            self.number_bot = 1
        if self.back_btn_three_players.draw(self.screen):
            self.menu_state = "play"

    def _update_IDLE_p(self):
        now = pyg.time.get_ticks()
        delta = now - self._idle_anim_last_tick
        self._idle_anim_last_tick = now
        for char_num, frames in self._idle_preview_frames.items():
            self._idle_anim_accum[char_num] += delta
            while self._idle_anim_accum[char_num] >= 100:
                self._idle_anim_accum[char_num] -= 100
                self._idle_anim_i[char_num] = (self._idle_anim_i[char_num] + 1) % len(
                    frames
                )
        # Arrow smooth lerp (all players)
        self._arrow_bob += delta / 1000.0
        for pid in list(self._arrow_target.keys()):
            if pid in self._arrow_pos:
                diff = self._arrow_target[pid] - self._arrow_pos[pid]
                self._arrow_pos[pid] += diff * 0.20  # ~20 % per tick → smooth slide

    def _get_IDLe_p__frame(self, char_num, pixel_size):

        frames = self._idle_preview_frames.get(char_num)
        if not frames:
            return None
        frame = frames[self._idle_anim_i.get(char_num, 0)]
        size = max(pixel_size, 1)
        return pyg.transform.scale(frame, (size, size))

    def _blit_largeChar(self, char_num, pos_x, pos_y, scale_factor=5):
        if not (1 <= char_num <= len(self.image_ch)):
            return
        icon = self.image_ch[char_num - 1]
        target_w = int(icon.get_width() * scale_factor)
        target_h = int(icon.get_height() * scale_factor)

        if 1 <= char_num <= 9 and char_num in self._idle_preview_frames:
            frame = self._get_IDLe_p__frame(char_num, target_h)
            if frame:
                self.screen.blit(frame, (pos_x, pos_y))
                return
        self.screen.blit(
            pyg.transform.scale(icon, (target_w, target_h)), (pos_x, pos_y)
        )

    def draw_character_preview(self, char_index):
        try:
            i = int(char_index)
        except Exception:
            i = 0

        if i and 1 <= i <= len(self.image_ch):
            self._update_IDLE_p()
            pos_x, pos_y = self.slot_positions.get(self.CurrentPlayer_id, (64, 125))
            s = max(1.0, float(self.char_p_scale))
            self._blit_largeChar(i, pos_x, pos_y, scale_factor=round(s))

    def draw_small_character_preview(self, char_index, x_offset):
        if isinstance(char_index, int) and 1 <= char_index <= len(self.image_ch):
            prev_img = self.image_ch[char_index - 1]
            self.screen.blit(prev_img, (self.center_x(prev_img, x_offset), 345))

    # ── Slot character display ───────────────────────────────────────────────
    # Fixed role positions within a slot: (dx from slot_x, size_px, dy from slot_y)
    # Visual layout:  [SUPPORT1 left]  [MAIN centre]  [SUPPORT2 right]
    #   char_1 = main      → centre, largest
    #   char_2 = support 1 → left,   smaller
    #   char_3 = support 2 → right,  smaller
    # Layout: support1 starts before slot_x (negative dx), group shifted left.
    #   support=72px  gap=5px  main=130px
    #   support1 dx = -40
    #   main     dx = -40+72+5 = 37
    #   support2 dx = 37+130+5 = 172
    #   dy: supports are vertically centred on the main (not bottom-aligned with it)
    #       main centre  = 72 + 65 = 137
    #       support dy   = 137 - 36 = 101   (both supports identical → always aligned)
    _SLOT_ROLE_LAYOUT = {
        #             dx    size   dy
        "support1": (-40, 72, 101),  # left,   small, centred on main
        "main": (37, 130, 72),  # centre, large
        "support2": (172, 72, 101),  # right,  small, centred on main
    }

    def _draw_slot_preview(self, pos_x, pos_y, char_1, char_2, char_3, player_id=None):
        """Draw one player slot with fixed role positions.

        char_1 (main) → centre large; char_2 (support1) → left small;
        char_3 (support2) → right small.
        Returns [(char_num, Rect), ...] for click hit-testing.
        """
        rl = self._SLOT_ROLE_LAYOUT
        # Draw order: support1 & support2 first, then main on top
        draw_pairs = [
            (char_2, "support1"),
            (char_3, "support2"),
            (char_1, "main"),
        ]
        click_rects = []
        for char, role in draw_pairs:
            if not char:
                continue
            dx, size, dy = rl[role]
            frame = self._get_IDLe_p__frame(char, size)
            bx, by = pos_x + dx, pos_y + dy
            if frame:
                self.screen.blit(frame, (bx, by))
            click_rects.append((char, pyg.Rect(bx, by, size, size)))
        return click_rects

    def _draw_arrow_indicator(self, player_id, slot_top_y):
        """Draw the selection cursor arrow above the current cursor slot.

        The arrow always points to the NEXT slot to fill:
          - 'main'     → centre  (choosing main)
          - 'support1' → left    (choosing support 1)
          - 'support2' → right   (choosing support 2)
        """
        cursor = self._arrow_cursor.get(player_id, "main")
        pos_x, _ = self.slot_positions.get(player_id, (64, 125))
        dx, size, dy = self._SLOT_ROLE_LAYOUT[cursor]
        target_x = float(pos_x + dx + size // 2)

        # Update smooth lerp target and snap on first appearance
        self._arrow_target[player_id] = target_x
        if player_id not in self._arrow_pos:
            self._arrow_pos[player_id] = target_x

        ax = int(self._arrow_pos[player_id])
        bob = int(5 * math.sin(self._arrow_bob * 4.5))  # ±5 px vertical bounce
        # Arrow always sits at the TOP of the slot (y fixed, only x varies)
        img_top_y = slot_top_y + 6 + bob  # 6 px below slot top → always inside

        if self._select_cursor_img:
            img = self._select_cursor_img
            self.screen.blit(img, (ax - img.get_width() // 2, img_top_y))
        else:
            # Fallback: simple gold triangle (tip at bottom of arrow area)
            tip_y = img_top_y + 30
            tip = (ax, tip_y)
            left = (ax - 13, tip_y - 18)
            right = (ax + 13, tip_y - 18)
            pyg.draw.polygon(self.screen, (110, 70, 0), [tip, left, right], 3)
            pyg.draw.polygon(self.screen, (255, 210, 30), [tip, left, right])

    def _deselect_char(self, char_num):
        """Remove *char_num* from the current player's selection.

        Each role slot is independent — no shifting.
        After removal the cursor always jumps to the EARLIEST empty slot
        (main → support1 → support2) to prevent ever getting stuck when
        multiple characters are deselected in sequence.
        """
        pid = self.CurrentPlayer_id
        if char_num == self.character_1:
            self.character_1 = 0
        elif char_num == self.character_2:
            self.character_2 = 0
        elif char_num == self.character_3:
            self.character_3 = 0
        else:
            return  # char not in selection — nothing to do
        self.p_character_update = True
        # Always point to the first empty slot so the player is never stuck
        if not self.character_1:
            self._arrow_cursor[pid] = "main"
        elif not self.character_2:
            self._arrow_cursor[pid] = "support1"
        else:
            self._arrow_cursor[pid] = "support2"
        self._arrow_pos.pop(pid, None)

    def handle_character_selection(self, character_var, next_state, title):
        # Handle the character selection
        self.screen.blit(self.choice_chracters, (0, 0))
        self.draw_text(title, self.font, self.TEXT_COL, 70, 0)

        if self.Back_selection_character.draw(self.screen):
            if character_var == self.character_1:
                self.menu_state = "play"
            elif character_var == self.character_2:
                self.menu_state = "choice_characters_1"
            elif character_var == self.character_3:
                self.menu_state = "choice_characters_2"

        # Gérer les clics sur les boutons de personnage
        character_buttons = [
            (self.character_1_button, 1),
            (self.character_2_button, 2),
            (self.character_3_button, 3),
            (self.character_4_button, 4),
            (self.character_5_button, 5),
        ]

        for button_obj, char_num in character_buttons:
            if button_obj.draw(self.screen):
                if character_var == self.character_1:
                    self.character_1 = char_num
                elif character_var == self.character_2:
                    self.character_2 = char_num
                elif character_var == self.character_3:
                    self.character_3 = char_num
                self.menu_state = next_state

        self.draw_character_preview(character_var)

    def handle_choice_characters_1(self):
        self.screen.blit(self.choice_chracters, (0, 0))
        self._update_IDLE_p()
        self.draw_text("Choose three characters", self.font, self.TEXT_COL, 70, 0)

        if self.Back_selection_character.draw(self.screen):
            self.menu_state = "play"

        character_buttons = [
            (self.character_1_button, 1),
            (self.character_2_button, 2),
            (self.character_3_button, 3),
            (self.character_4_button, 4),
            (self.character_5_button, 5),
        ]

        for button_obj, char_num in character_buttons:
            if button_obj.draw(self.screen):
                self.character_1 = char_num
                self.menu_state = "choice_characters_2"

        pos_x, pos_y = self.slot_positions.get(self.CurrentPlayer_id, (64, 125))
        rects = self._draw_slot_preview(
            pos_x, pos_y, self.character_1, 0, 0, player_id=self.CurrentPlayer_id
        )
        self._idle_click_rects[self.CurrentPlayer_id] = rects
        if self.character_1:
            self._draw_arrow_indicator(self.CurrentPlayer_id, pos_y)

    def handle_choice_characters_2(self):
        self.screen.blit(self.choice_chracters, (0, 0))
        self._update_IDLE_p()
        self.draw_text("Choose two characters", self.font, self.TEXT_COL, 70, 0)

        if self.Back_selection_character.draw(self.screen):
            self.menu_state = "choice_characters_1"

        character_buttons = [
            (self.character_1_button, 1),
            (self.character_2_button, 2),
            (self.character_3_button, 3),
            (self.character_4_button, 4),
            (self.character_5_button, 5),
        ]

        for button_obj, char_num in character_buttons:
            if button_obj.draw(self.screen):
                self.character_2 = char_num
                self.menu_state = "choice_characters_3"

        pos_x, pos_y = self.slot_positions.get(self.CurrentPlayer_id, (64, 125))
        rects = self._draw_slot_preview(
            pos_x,
            pos_y,
            self.character_1,
            self.character_2,
            0,
            player_id=self.CurrentPlayer_id,
        )
        self._idle_click_rects[self.CurrentPlayer_id] = rects
        if self.character_1 or self.character_2:
            self._draw_arrow_indicator(self.CurrentPlayer_id, pos_y)

    def handle_choice_characters_3(self):
        self.screen.blit(self.choice_chracters, (0, 0))
        self._update_IDLE_p()
        self.draw_text("Choose one character", self.font, self.TEXT_COL, 70, 0)

        if self.Back_selection_character.draw(self.screen):
            self.menu_state = "choice_characters_2"

        character_buttons = [
            (self.character_1_button, 1),
            (self.character_2_button, 2),
            (self.character_3_button, 3),
            (self.character_4_button, 4),
            (self.character_5_button, 5),
        ]

        for button_obj, char_num in character_buttons:
            if button_obj.draw(self.screen):
                self.character_3 = char_num

        pos_x, pos_y = self.slot_positions.get(self.CurrentPlayer_id, (64, 125))
        rects = self._draw_slot_preview(
            pos_x,
            pos_y,
            self.character_1,
            self.character_2,
            self.character_3,
            player_id=self.CurrentPlayer_id,
        )
        self._idle_click_rects[self.CurrentPlayer_id] = rects
        if self.character_1 or self.character_2 or self.character_3:
            self._draw_arrow_indicator(self.CurrentPlayer_id, pos_y)

        if self.character_3 and self.start_button.draw(self.screen):
            self.menu_state = "start game"
            self.etat = "game"

    def handle_character_selection_final(self):
        # Draw background
        self.screen.blit(self.choice_chracters, (0, 0))
        self._update_IDLE_p()
        self.draw_text_center("Choose three characters", self.font, self.TEXT_COL, 20)

        if self.Back_selection_character.draw(self.screen):
            self.menu_state = "play"
            self.character_1 = 0
            self.character_2 = 0
            self.character_3 = 0
            self._arrow_cursor[self.CurrentPlayer_id] = "main"
            self._arrow_pos.pop(self.CurrentPlayer_id, None)
            if self.current_session_name:
                self.p_leave_session = self.current_session_name
            self.current_session_name = None

        # ── character buttons ──────────────────────────────────────────────
        character_buttons = [
            (self.character_1_button, 1),
            (self.character_2_button, 2),
            (self.character_3_button, 3),
            (self.character_4_button, 4),
            (self.character_5_button, 5),
        ]

        # Handle character button clicks for current player's selection
        for button_obj, char_num in character_buttons:
            if button_obj.draw(self.screen):
                if self.players_ready[self.CurrentPlayer_id]:
                    continue
                if char_num in (self.character_1, self.character_2, self.character_3):
                    # Re-clicking an already-selected char → deselect it
                    self._deselect_char(char_num)
                else:
                    # Place char in the cursor's slot, then advance unless all 3 are filled
                    pid = self.CurrentPlayer_id
                    cursor = self._arrow_cursor.get(pid, "main")
                    filled = False
                    if cursor == "main" and not self.character_1:
                        self.character_1 = char_num
                        filled = True
                    elif cursor == "support1" and not self.character_2:
                        self.character_2 = char_num
                        filled = True
                    elif cursor == "support2" and not self.character_3:
                        self.character_3 = char_num
                        filled = True
                    if filled:
                        self.p_character_update = True
                        # Advance to first empty slot; if all filled keep current position
                        if not self.character_1:
                            self._arrow_cursor[pid] = "main"
                        elif not self.character_2:
                            self._arrow_cursor[pid] = "support1"
                        elif not self.character_3:
                            self._arrow_cursor[pid] = "support2"
                        # else all 3 filled → cursor stays wherever it is

        self.players_characters[self.CurrentPlayer_id] = [
            self.character_1 or None,
            self.character_2 or None,
            self.character_3 or None,
        ]

        # Les slots > max_human_slot sont des bots
        max_human_slot = 4 - self.number_bot

        cur_mouse = pyg.mouse.get_pressed()[0]
        just_clicked = cur_mouse and not self.__mouse_prev
        self.__mouse_prev = cur_mouse
        mouse_pos = pyg.mouse.get_pos()

        # ── Click on idle animations in current player's slot → deselect ──────
        if just_clicked and not self.players_ready[self.CurrentPlayer_id]:
            for char_num, rect in self._idle_click_rects.get(self.CurrentPlayer_id, []):
                if rect.collidepoint(mouse_pos):
                    self._deselect_char(char_num)
                    break

        for player_id in range(1, 5):
            if player_id > max_human_slot:
                px, py = self.slot_positions[player_id]
                self.draw_text(
                    "BOT", self.middle_font, (150, 150, 255), px + 20, py + 50
                )
                continue
            pos_x, pos_y = self.slot_positions[player_id]

            characters = self.players_characters[player_id]
            char_1, char_2, char_3 = characters

            # ── Draw slot: animated idle stack + arrow indicator ──────────────
            rects = self._draw_slot_preview(
                pos_x, pos_y, char_1, char_2, char_3, player_id=player_id
            )
            self._idle_click_rects[player_id] = rects
            # Arrow only shown for the local player (other players have no cursor)
            if player_id == self.CurrentPlayer_id and not self.players_ready[player_id]:
                self._draw_arrow_indicator(player_id, pos_y)

            if (
                just_clicked
                and player_id == self.CurrentPlayer_id
                and self.players_ready[self.CurrentPlayer_id]
            ):
                rect_ready = pyg.Rect(pos_x, pos_y - 25, 120, 20)
                if rect_ready.collidepoint(mouse_pos):
                    self.players_ready[self.CurrentPlayer_id] = False
                    self.p_unready = True

            if char_1 or char_2 or char_3:
                player_label = (
                    "YOU"
                    if player_id == self.CurrentPlayer_id
                    else f"Player {player_id}"
                )
                self.draw_text(
                    player_label, self.middle_font, self.TEXT_COL, pos_x, pos_y - 40
                )

                status_text = "READY" if self.players_ready[player_id] else "WAITING"
                status_color = (
                    (0, 255, 0) if self.players_ready[player_id] else (255, 255, 0)
                )
                self.draw_text(
                    status_text, self.mini_font, status_color, pos_x, pos_y - 20
                )

            else:
                if player_id != self.CurrentPlayer_id and player_id < self.number_bot:
                    self.draw_text(
                        f"Player {player_id}",
                        self.middle_font,
                        self.TEXT_COL2,
                        pos_x + 20,
                        pos_y + 50,
                    )
                    self.draw_text(
                        "Waiting...",
                        self.mini_font,
                        (255, 255, 0),
                        pos_x + 20,
                        pos_y + 100,
                    )

        my_slot_x, my_slot_y = self.slot_positions[self.CurrentPlayer_id]

        if (
            self.character_1
            and self.character_2
            and self.character_3
            and not self.players_ready[self.CurrentPlayer_id]
        ):
            if self.start_button.draw(self.screen):
                # Mark current player as ready
                self.players_ready[self.CurrentPlayer_id] = True
                # Prepare data to send to server with all 3 characters
                self.p_character_submission = {
                    "player_id": self.CurrentPlayer_id,
                    "character_1": self.character_1,
                    "character_2": self.character_2,
                    "character_3": self.character_3,
                    "session_name": self.current_session_name,
                }
                from ui.console import print_network

                print_network(
                    f"Joueur {self.CurrentPlayer_id} a cliqué PLAY avec {self.character_1}, {self.character_2}, {self.character_3}"
                )

        # Check if all players are ready
        # total_players_in_session = self.number_players + 1  # Include the current player

        human_present = {self.CurrentPlayer_id}
        for p_id in range(1, max_human_slot + 1):
            if any(c is not None for c in self.players_characters[p_id]):
                human_present.add(p_id)

        ready_count = sum(1 for p_id in human_present if self.players_ready[p_id])
        if ready_count == len(human_present) and ready_count > 0:
            self.menu_state = "maps_selection"

    def maps_selection(self):
        self.screen.blit(self.maps_selection_bg, (0, 0))

        for i, pos in self.slot_maps_selection.items():
            if i in self.map_slot_previews:
                self.screen.blit(self.map_slot_previews[i], pos)

        voters_per_map = {}
        for player_id, map_id in self.map_player_votes.items():
            voters_per_map.setdefault(map_id, []).append(player_id)

        sq = 14
        gap = 2
        for map_id, voter_ids in voters_per_map.items():
            if map_id not in self.slot_maps_selection:
                continue
            sx, sy = self.slot_maps_selection[map_id]
            for idx, pid in enumerate(sorted(voter_ids)):
                color = self.PLAYER_COLORS.get(pid, (200, 200, 200))
                pyg.draw.rect(self.screen, color, (sx + idx * (sq + gap), sy, sq, sq))

    def update_map_votes(self, votes):
        self.map_player_votes = {int(k): v for k, v in votes.items()}

    def method_menu(self):
        # MAIN METHOD FOR THE MENU

        if self.menu_state == "main":
            self.handle_main_menu()
        elif self.menu_state == "creation_parameters_session_menu":
            button.Button.blocked_rect = self.input_box.modal_rect
            self.handle_session_menu()
            self.input_box.draw(self.screen)

            if self.input_box.wants_validate:
                session_data = {
                    "titre": self.input_box.text
                    if self.input_box.text != ""
                    else "Without title",
                    "nb_bots": self.input_box.temp_nb_ia,
                    "nb_players": 0,
                    "y": 79,
                    "gap": 125,
                }
                self.sessionPending = session_data
                button.Button.blocked_rect = None
                self.menu_state = "play"

            if self.input_box.wants_cancel:
                button.Button.blocked_rect = None
                self.menu_state = "play"

        elif self.menu_state == "play":
            button.Button.blocked_rect = None
            self.input_box.clean()
            self.handle_session_menu()
        elif self.menu_state == "play_menu":
            self.handle_play_menu()
        elif self.menu_state == "one_player":
            self.handle_one_player_menu()
        elif self.menu_state == "two_players":
            self.handle_two_players_menu()
        elif self.menu_state == "three_players":
            self.handle_three_players_menu()
        elif self.menu_state == "choice_characters_1":
            self.handle_choice_characters_1()
        elif self.menu_state == "choice_characters_2":
            self.handle_choice_characters_2()
        elif self.menu_state == "choice_characters_3":
            self.handle_choice_characters_3()
        elif self.menu_state == "waiting_player_id":
            self.draw_text_center(
                "Connexion à la session...",
                self.middle_font,
                self.TEXT_COL,
                self.height // 2,
            )
            print_debug("Enter, laoding for the session's connexion")
        elif self.menu_state == "character_selection_final":
            self.handle_character_selection_final()
        elif self.menu_state == "maps_selection":
            self.maps_selection()
        elif self.menu_state == "start game":
            self.etat = "game"
            print_warning("start of the game!!!")
        else:
            self.draw_text_center("Press Space to start", self.font, self.TEXT_COL, 250)


class Session:
    def __init__(self, menu):
        self.menu = menu
        self.screen = menu.screen

        # Laod & redimensionnement of assets
        self.bar_session = pyg.image.load(
            "assets/Menus_assets/sessions_section/BAR.png"
        ).convert_alpha()
        self.bot_session = pyg.transform.scale(
            pyg.image.load("assets/Menus_assets/sessions_section/BOT.png"), (30, 20)
        ).convert_alpha()
        self.player_session = pyg.transform.scale(
            pyg.image.load("assets/Menus_assets/sessions_section/player.png"), (30, 20)
        ).convert_alpha()
        self.button_img = pyg.image.load(
            "assets/Menus_assets/sessions_section/Button.png"
        ).convert_alpha()
        self.splash_session = pyg.transform.scale(
            pyg.image.load("assets/Menus_assets/sessions_section/splash.png"),
            (150, 150),
        ).convert_alpha()
        self.star_bar_session = pyg.transform.scale(
            pyg.image.load("assets/Menus_assets/sessions_section/Star_Bar.png"),
            (367, 244),
        ).convert_alpha()

        # Bouton "Join" spécifique à cette session
        self.join_button = button.Button(
            x=691, y=231, image=self.button_img, scale=0.25
        )

        self.gap = 125
        self.y = 79

        self.titre = "Without title"
        self.nb_bots = 0
        self.nb_players = 0

    def to_dict(self):
        return {
            "titre": self.titre,
            "nb_bots": self.nb_bots,
            "nb_players": self.nb_players,
            "y": self.y,
            "gap": self.gap,
        }

    @staticmethod  # Pour quentin: une static method c'est juste une method de la class qui n'utilise pas self
    def from_dict(data, menu):
        session = Session(menu)
        session.titre = data.get("titre", "Without title")
        session.nb_bots = data.get("nb_bots", 0)
        session.nb_players = data.get("nb_players", 1)
        session.y = data.get("y", 79)
        session.gap = data.get("gap", 125)
        return session

    def draw_session(self, y_scrollé):
        self.join_button.rect.y = y_scrollé + 152

        # Barre de fond
        self.screen.blit(self.bar_session, (310, y_scrollé))

        # Nom de la session (Text)
        self.menu.draw_text(self.titre, self.menu.font, "Black", 391, y_scrollé + 113)

        # Check if session is full
        is_session_full = self.nb_players + self.nb_bots >= 4

        # Bouton Rejoindre ou FULL et son texte
        if not is_session_full:
            if self.join_button.draw(self.screen):
                print(f"Tentative de rejoindre : {self.titre}")
                # Réinitialiser les variables de sélection
                self.menu.character_1 = 0
                self.menu.character_2 = 0
                self.menu.character_3 = 0
                self.menu.current_session_name = self.titre
                self.menu.number_players = self.nb_players
                self.menu.number_bot = self.nb_bots

                # Réinitialiser les sélections de tous les joueurs
                for p_id in range(1, 5):
                    self.menu.players_characters[p_id] = [None, None, None]
                    self.menu.players_ready[p_id] = False

                self.menu.p_join_session = self.titre
                self.menu.menu_state = "waiting_player_id"

            button_text = "Join"
        else:
            # Session is full - display FULL button (disabled)
            self.join_button.draw(
                self.screen
            )  # Still draw button for visual consistency
            button_text = "FULL"

        self.menu.draw_text(
            button_text, self.menu.middle_font, "Black", 745, y_scrollé + 165
        )

        # Décorations (Splash et Star Bar)
        self.screen.blit(self.splash_session, (845, y_scrollé + 100))
        self.screen.blit(self.star_bar_session, (357, y_scrollé + 87))

        # Icones (IA et Joueurs)
        self.screen.blit(self.bot_session, (450, y_scrollé + 188))
        self.screen.blit(self.player_session, (530, y_scrollé + 188))

        # values des paramètres
        self.menu.draw_text(
            str(self.nb_bots), self.menu.middle_font, "Black", 490, y_scrollé + 188
        )
        available_slots = self.nb_players
        self.menu.draw_text(
            str(available_slots), self.menu.middle_font, "Black", 570, y_scrollé + 188
        )


class InputBox:
    def __init__(self, x, y, w, h, text="", button_session=None, menu=None):
        self.rect = pyg.Rect(x, y, w, h)
        self.color = pyg.Color("lightskyblue3")
        self.text = text
        self.font = pyg.font.SysFont("Arial", 22)
        self.active = False
        self.screen = menu.screen
        self.menu = menu

        self.temp_nb_ia = 0
        self.temp_nb_players = 1
        self.wants_validate = False
        self.wants_cancel = False

        self._cursor_visible = True
        self._cursor_timer = 0
        self._CURSOR_INTERVAL = 500

        self.assets = [
            "assets/Menus_assets/Parameters_session/+_-_Sessions_parameters.png",
            "assets/Menus_assets/Parameters_session/bg_parameters_interface.png",
            "assets/Menus_assets/Parameters_session/Input_parameters_sessions.png",
            "assets/Menus_assets/Parameters_session/Title_name_of_the_Session_parameters.png",
            "assets/Menus_assets/Parameters_session/Title_numbers_of_bots_sessions_parameters.png",
        ]

        _pm = pyg.image.load(self.assets[0]).convert_alpha()
        _bg = pyg.image.load(self.assets[1]).convert_alpha()
        _input = pyg.image.load(self.assets[2]).convert_alpha()
        _title_name = pyg.image.load(self.assets[3]).convert_alpha()
        _title_bots = pyg.image.load(self.assets[4]).convert_alpha()

        SCALE_TITLE = 0.45
        SIZE = (612, 408)
        _title_name = pyg.transform.scale(
            _title_name, (int(SIZE[0] * SCALE_TITLE), int(SIZE[1] * SCALE_TITLE))
        )
        _title_bots = pyg.transform.scale(
            _title_bots, (int(SIZE[0] * SCALE_TITLE), int(SIZE[1] * SCALE_TITLE))
        )
        _input = pyg.transform.scale(
            _input, (int(SIZE[0] * SCALE_TITLE), int(SIZE[1] * SCALE_TITLE))
        )

        BG_SCALE = 1.7
        self.img_bg = pyg.transform.scale(
            _bg,
            (int(_bg.get_width() * BG_SCALE), int(_bg.get_height() * BG_SCALE)),
        )
        self.bg_pos = (
            menu.width // 2 - self.img_bg.get_width() // 2,
            menu.height // 2 - self.img_bg.get_height() // 2,
        )

        MODAL_X = self.bg_pos[0]
        MODAL_Y = self.bg_pos[1]
        MODAL_W = self.img_bg.get_width()
        MODAL_H = self.img_bg.get_height()

        self.img_title_name = _title_name
        self.img_title_bots = _title_bots
        self.img_input_name = _input
        self.img_input_bots = _input

        pm_w, pm_h = _pm.get_size()
        half = pm_w // 2
        BTN_SZ = 52
        plus_surf = pyg.transform.scale(
            _pm.subsurface(pyg.Rect(0, 0, half - 24, pm_h)).copy(), (BTN_SZ, BTN_SZ)
        )
        minus_surf = pyg.transform.scale(
            _pm.subsurface(pyg.Rect(half - 24, 0, pm_w - half, pm_h)).copy(),
            (BTN_SZ, BTN_SZ),
        )

        LABEL_W = _title_name.get_width()
        INPUT_W = _input.get_width()
        INPUT_H = _input.get_height()
        LABEL_H = _title_name.get_height()

        PAD_X = (MODAL_W - LABEL_W - 30 - INPUT_W) // 2
        COL1_X = MODAL_X + PAD_X + 35
        COL2_X = COL1_X + LABEL_W - 10
        ROW1_Y = MODAL_Y + int(MODAL_H * 0.22) + 30
        ROW2_Y = MODAL_Y + int(MODAL_H * 0.47) - 60

        self.pos_title_name = (COL1_X, ROW1_Y + (INPUT_H - LABEL_H) // 2)
        self.pos_title_bots = (COL1_X, ROW2_Y + (INPUT_H - LABEL_H) // 2)
        self.pos_input_name = (COL2_X, ROW1_Y - 8)
        self.pos_input_bots = (COL2_X, ROW2_Y - 8)

        self.rect = pyg.Rect(COL2_X + 10, ROW1_Y + 8, INPUT_W - 20, INPUT_H - 16)

        PM_X = COL2_X + INPUT_W - 120
        PM_Y = ROW2_Y + (INPUT_H - BTN_SZ) // 2 - 8
        self.btn_plus_ia = button.Button(PM_X, PM_Y, plus_surf, 1.0, bypass_block=True)
        self.btn_moins_ia = button.Button(
            PM_X + BTN_SZ + 4, PM_Y, minus_surf, 1.0, bypass_block=True
        )

        BTN_Y = MODAL_Y + int(MODAL_H * 0.78) - 200
        ofx = 100
        self.validate_button = button.Button(
            MODAL_X + MODAL_W // 2 + 20 + ofx,
            BTN_Y,
            button_session,
            0.3,
            bypass_block=True,
        )
        self.cancel_button = button.Button(
            MODAL_X + MODAL_W // 2 - 130 + ofx,
            BTN_Y,
            button_session,
            0.3,
            bypass_block=True,
        )

        self.count_font = pyg.font.SysFont("arialblack", 20)
        self.label_font = pyg.font.SysFont("arialblack", 16)
        self.txt_surface = self.count_font.render(self.text, True, (180, 60, 0))

        self.modal_rect = pyg.Rect(
            self.bg_pos[0],
            self.bg_pos[1],
            self.img_bg.get_width(),
            self.img_bg.get_height(),
        )

    def handle_event(self, event):
        if event.type == pyg.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = (
                pyg.Color("dodgerblue2") if self.active else pyg.Color("lightskyblue3")
            )

        if event.type == pyg.KEYDOWN and self.active:
            if event.key == pyg.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < 15:
                self.text += event.unicode
            self.txt_surface = self.count_font.render(self.text, True, (180, 60, 0))

    def draw(self, screen):
        self.wants_validate = False
        self.wants_cancel = False

        screen.blit(self.img_bg, self.bg_pos)

        screen.blit(self.img_title_name, self.pos_title_name)
        screen.blit(self.img_input_name, self.pos_input_name)

        text_x = self.rect.x + 20
        text_y = (
            self.rect.y + (self.rect.height - self.txt_surface.get_height()) // 2 - 5
        )
        screen.blit(self.txt_surface, (text_x, text_y))

        if self.active:
            now = pyg.time.get_ticks()
            if now - self._cursor_timer >= self._CURSOR_INTERVAL:
                self._cursor_visible = not self._cursor_visible
                self._cursor_timer = now
            if self._cursor_visible:
                cursor_x = text_x + self.txt_surface.get_width() + 2
                cursor_top = text_y + 2
                cursor_bottom = text_y + self.txt_surface.get_height() - 2
                pyg.draw.line(
                    screen,
                    (180, 60, 0),
                    (cursor_x, cursor_top),
                    (cursor_x, cursor_bottom),
                    2,
                )

        screen.blit(self.img_title_bots, self.pos_title_bots)
        screen.blit(self.img_input_bots, self.pos_input_bots)

        count_surf = self.count_font.render(str(self.temp_nb_ia), True, (180, 60, 0))
        bx, by = self.pos_input_bots
        bw = self.img_input_bots.get_width()
        bh = self.img_input_bots.get_height()
        screen.blit(
            count_surf,
            (
                bx + (bw - count_surf.get_width()) // 2,
                by + (bh - count_surf.get_height()) // 2,
            ),
        )

        if self.btn_plus_ia.draw(screen):
            self.temp_nb_ia += 1
        if self.btn_moins_ia.draw(screen) and self.temp_nb_ia > 0:
            self.temp_nb_ia -= 1

        if self.validate_button.draw(screen):
            self.wants_validate = True
        if self.cancel_button.draw(screen):
            self.wants_cancel = True

        for btn, label in [
            (self.validate_button, "Confirm"),
            (self.cancel_button, "Cancel"),
        ]:
            surf = self.label_font.render(label, True, (0, 0, 0))
            draw_x = btn.rect.x - btn._inset_x
            draw_y = btn.rect.y - btn._inset_y
            cx = draw_x + btn.image.get_width() // 2 - surf.get_width() // 2
            cy = draw_y + btn.image.get_height() // 2 - surf.get_height() // 2 - 7
            screen.blit(surf, (cx, cy))

    def draw_text(self, text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        self.screen.blit(img, (x, y))

    def clean(self):
        self.text = ""
        self.txt_surface = self.count_font.render(self.text, True, (180, 60, 0))
        self.active = False
        self.color = pyg.Color("lightskyblue3")
        self.temp_nb_ia = 0
        self.temp_nb_players = 1
