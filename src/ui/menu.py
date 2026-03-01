"""
MENU SYSTEM MODULE - Main menu and game menus

This module handles all menu systems for the game:
- Main menu with play/settings/exit options
- Settings menu (video, audio, keybindings)
- Character selection menu
- Game lobby menu for multiplayer setup

The Menu class manages menu state transitions and rendering.

Recommendations:
1. Extract menu states into separate menu classes
2. Use a state machine pattern for better menu management
3. Create a central button manager to avoid duplication
4. Add menu animations and transitions
5. Implement a proper layout system for button positioning
"""

import json
import sys
from typing import Optional

import pygame as pyg

import game.characters as player_module
from ui import Buttons as ObjButton
from ui.server import Serveur
from utils.paths import get_asset_path

from . import animated_button, button

# ============================================================================
# CONSTANTS - Menu configuration
# ============================================================================
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
BUTTON_SCALE = 2


class Menu:
    """
    Main Menu class handling all menu screens and navigation.

    Menu States:
        - "main": Main menu screen (play, settings, exit)
        - "character_selection": Character selection screen
        - "settings": Settings submenu
        - "game": Game started state
    """

    def __init__(self, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, fullscreen=False):
        """
        Initialize menu system with window configuration.

        Args:
            width (int): Window width (default 1280)
            height (int): Window height (default 720)
            fullscreen (bool): Enable fullscreen (default False)
        """

        # ====================================================================
        # WINDOW CONFIGURATION
        # ====================================================================
        self.width = width
        self.height = height
        self.fullscreen = fullscreen

        # ====================================================================
        # PLAYER INITIALIZATION
        # ====================================================================
        self.player = player_module.Furnace()

        # ====================================================================
        # MENU STATE VARIABLES
        # ====================================================================
        self.etat = "menu"  # Current menu state
        self.game_started = False
        self.menu_state = "main"  # Main submenu state

        # Character selection variables
        self.number_players = 0
        self.number_bot = 0
        self.character_1 = 0
        self.character_2 = 0
        self.character_3 = 0

        # ====================================================================
        # PYGAME INITIALIZATION
        # ====================================================================
        pyg.init()

        # Display setup
        flags = pyg.FULLSCREEN if self.fullscreen else 0
        self.screen = pyg.display.set_mode((self.width, self.height), flags)
        pyg.display.set_caption("Jeu Multijoueur")
        self.clock = pyg.time.Clock()

        # ====================================================================
        # FONT AND COLOR SETUP
        # ====================================================================
        self.font = pyg.font.SysFont("arialblack", 40)
        self.middle_font = pyg.font.SysFont("arialblack", 20)
        self.little_font = pyg.font.SysFont("arialblack", 10)
        self.TEXT_COL = (255, 255, 255)  # White
        self.TEXT_COL2 = (255, 0, 0)  # Red

        # ====================================================================
        # LOAD MENU BACKGROUNDS
        # ====================================================================
        self.wallpaper = pyg.image.load(
            "assets/buttons/21-MENUS/MAIN MENU-Sheet.png"
        ).convert_alpha()
        # Scale wallpaper to fill window
        self.wallpaper = pyg.transform.scale(self.wallpaper, (self.width, self.height))
        self.choice_chracters = pyg.image.load(
            "assets/wallpapers/SELECT-SCREEN.png"
        ).convert_alpha()
        # Scale character selection background to fill window
        self.choice_chracters = pyg.transform.scale(
            self.choice_chracters, (self.width, self.height)
        )

        # ====================================================================
        # play button frames
        # ====================================================================

        play_button = ObjButton.PlayButton()
        self.play_button_frames = play_button.play_button_frames

        # ====================================================================
        # Settings button frames
        # ====================================================================

        settings_button = ObjButton.OptionsButton()
        self.settings_button_frames = settings_button.settings_button_frames

        # ====================================================================
        # Exit button frames
        # ====================================================================

        exit_button = ObjButton.ExitButton()
        self.exit_button_frames = exit_button.exit_button_frames

        # Static button images for non-animated buttons
        settings_img = pyg.image.load(
            "assets/buttons/button_settings.png"
        ).convert_alpha()
        exit_img = pyg.image.load("assets/buttons/button_exit.png").convert_alpha()

        # Settings submenu buttons
        video_img = pyg.image.load("assets/buttons/button_video.png").convert_alpha()
        audio_img = pyg.image.load("assets/buttons/button_audio.png").convert_alpha()
        keys_img = pyg.image.load("assets/buttons/button_keys.png").convert_alpha()
        back_img = pyg.image.load("assets/buttons/button_back.png").convert_alpha()

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
        Back_selection_character_img = pyg.image.load(
            "assets/buttons/Back_selection_character.png"
        ).convert_alpha()

        # # ====================================================================
        # # Images for session's interface
        # # ====================================================================

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

        # ====================================================================
        # LOAD CHARACTER SELECTION IMAGES
        # ====================================================================
        image_ch = []
        for i in range(1, 19):
            Img = pyg.image.load(
                f"assets/characters_selection/Character_{i}.png"
            ).convert_alpha()
            image_ch.append(Img)

        # Store character images for display
        self.image_ch = image_ch
        self.char_preview_scale = 9.5  # Character preview scale factor

        # ====================================================================
        # CREATE BUTTON INSTANCES
        # ====================================================================
        # Main menu buttons with animations (horizontally centered)
        self.play_button = animated_button.AnimatedButton(
            self.center_x(self.play_button_frames[0], 1.5),
            370,
            self.play_button_frames,
            BUTTON_SCALE,
            animation_speed=1,
        )
        self.settings_button = animated_button.AnimatedButton(
            self.center_x(self.settings_button_frames[0], 1.5),
            475,
            self.settings_button_frames,
            2,
            animation_speed=1,
        )
        self.exit_button = animated_button.AnimatedButton(
            self.center_x(self.exit_button_frames[0], 1.5),
            580,
            self.exit_button_frames,
            2,
            animation_speed=1,
        )
        self.video_button = button.Button(
            self.center_x(video_img, 1) - 350, 350, video_img, 1
        )
        self.audio_button = button.Button(
            self.center_x(audio_img, 1), 350, audio_img, 1
        )
        self.keys_button = button.Button(
            self.center_x(keys_img, 1) + 330, 350, keys_img, 1
        )
        self.back_button = button.Button(self.center_x(back_img, 1), 700, back_img, 1)
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
        self.Back_selection_character = button.Button(
            self.center_x(Back_selection_character_img, 77),
            10,
            Back_selection_character_img,
            2.7,
        )

        # # Sessions buttons
        # self.join_button = button.Button(
        #     x=691, y=231, image= self.button_session, scale=0.25
        # )

        self.create_session_button = button.Button(
            x=655, y=400, image=self.button_session, scale=0.5
        )

        # character buttons left
        self.character_1_button = button.Button(
            self.center_x(image_ch[0], 25), 125, image_ch[0], 4
        )
        self.character_2_button = button.Button(
            self.center_x(image_ch[1], 12), 125, image_ch[1], 4
        )
        self.character_3_button = button.Button(
            self.center_x(image_ch[2], 25), 240, image_ch[2], 4
        )
        self.character_4_button = button.Button(
            self.center_x(image_ch[3], 12.5), 240, image_ch[3], 4
        )
        self.character_5_button = button.Button(
            self.center_x(image_ch[4], 24.4), 355, image_ch[4], 4
        )
        self.character_6_button = button.Button(
            self.center_x(image_ch[5], 12.5), 355, image_ch[5], 4
        )
        self.character_7_button = button.Button(
            self.center_x(image_ch[6], 25), 470, image_ch[6], 4
        )
        self.character_8_button = button.Button(
            self.center_x(image_ch[7], 12.5), 470, image_ch[7], 4
        )
        self.character_9_button = button.Button(
            self.center_x(image_ch[8], 19), 582, image_ch[8], 4
        )

        # character buttons right
        self.character_10_button = button.Button(
            self.center_x(image_ch[9], -17), 125, image_ch[9], 4
        )
        self.character_11_button = button.Button(
            self.center_x(image_ch[10], -4), 125, image_ch[10], 4
        )
        self.character_12_button = button.Button(
            self.center_x(image_ch[11], -16), 240, image_ch[11], 4
        )
        self.character_13_button = button.Button(
            self.center_x(image_ch[12], -4), 240, image_ch[12], 4
        )
        self.character_14_button = button.Button(
            self.center_x(image_ch[13], -16.2), 355, image_ch[13], 4
        )
        self.character_15_button = button.Button(
            self.center_x(image_ch[14], -4.1), 355, image_ch[14], 4
        )
        self.character_16_button = button.Button(
            self.center_x(image_ch[15], -16.2), 470, image_ch[15], 4
        )
        self.character_17_button = button.Button(
            self.center_x(image_ch[16], -4.1), 470, image_ch[16], 4
        )
        self.character_18_button = button.Button(
            self.center_x(image_ch[17], -11), 582, image_ch[17], 4
        )

        # character choosen
        character_choosen_img = pyg.image.load(
            "assets/buttons/character_choosen.png"
        ).convert_alpha()
        self.character_choosen_button = button.Button(
            self.center_x(character_choosen_img, -11), 100, character_choosen_img, 10
        )

        # start button
        start_img = pyg.image.load("assets/buttons/start_button.png").convert_alpha()
        self.start_button = button.Button(
            self.center_x(start_img, 1), 600, start_img, 1
        )

        # ====================================================================
        # dev settings
        # ====================================================================
        # self.images_session = [self.bg_session, self.bar_session, self.bot_session, self.button_session, self.player_session, self.splash_session, self.star_bar_session]

        # ====================================================================
        # Server variables
        # ====================================================================
        self.server: Optional[Serveur] = (
            None  # Reference to server instance (set from main)
        )

        # ====================================================================
        # Variables sessions
        # ====================================================================
        self.sessions = []  # Local sessions (will be synced with server)
        self.scroll_y = 0

        self.input_box = InputBox(
            100, 100, 140, 32, button_session=self.button_session, menu=self
        )

    def handle_session_menu(self):
        """Gère l'état du menu des sessions"""
        self.bg_session = pyg.transform.scale(
            self.bg_session, (self.width, self.height)
        )
        self.screen.blit(self.bg_session, (0, 0))

        zone_visible = pyg.Rect(300, 200, 750, 320)
        self.screen.set_clip(zone_visible)

        for i, session in enumerate(self.sessions):
            # print(f"Session nb {i}: {session}. Y-->{session.y}")
            print(
                f"Session nb {i}: {session}. Y-->{session.y} - title-->{session.titre}"
            )
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
        if self.exit_button.draw(self.screen):
            self.menu_state = "main"

    def send_session_to_server(self, session):
        """
        Send a session to the server as JSON.

        Args:
            session (Session): Session object to send to server
        """
        if self.server is None:
            print("Serveur non connecté")
            return

        try:
            # Convert session to dictionary
            session_dict = session.to_dict()
            # Create JSON message
            message = f"[Sessions]:{json.dumps(session_dict)}"
            # Send to all connected clients via server
            self.server.broadcast(message, None)
            print(f"Session '{session.titre}' envoyée au serveur")
        except Exception as e:
            print(f"Erreur lors de l'envoi de la session: {e}")

    def update_sessions_from_server(self, sessions_json):
        """
        Update local sessions list from server JSON data.

        Args:
            sessions_json (str): JSON string containing sessions list
        """
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

    def center_x(self, image, scale=1):
        """Retourne la coordonnée x pour centrer `image` horizontalement.

        `scale` est le facteur de mise à l'échelle appliqué lors de la création du bouton.
        """
        w = int(image.get_width() * scale)
        return (self.width - w) // 2

    def draw_text(self, text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        self.screen.blit(img, (x, y))

    def draw_text_center(self, text, font, text_col, y):
        img = font.render(text, True, text_col)
        x = (self.width - img.get_width()) // 2
        self.screen.blit(img, (x, y))

    def handle_main_menu(self):
        """Gère l'état du menu principal"""
        # Draw background first to clear previous frame
        self.screen.blit(self.wallpaper, (0, 0))
        # Then draw animated buttons
        if self.play_button.draw(self.screen):
            self.menu_state = "play"
        if self.settings_button.draw(self.screen):
            self.menu_state = "settings"
        if self.exit_button.draw(self.screen):
            pyg.quit()
            sys.exit(0)

    def handle_settings_menu(self):
        """Gère l'état du menu paramètres"""
        if self.video_button.draw(self.screen):
            print("Video Settings")
        if self.audio_button.draw(self.screen):
            print("Audio Settings")
        if self.keys_button.draw(self.screen):
            print("Keys Settings")
        if self.exit_button.draw(self.screen):
            self.menu_state = "main"

    def handle_play_menu(self):
        """Gère la sélection du nombre de joueurs"""
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
        if self.one_player_button.draw(self.screen):
            self.menu_state = "one_player"
            self.number_players = 1
        if self.two_players_button.draw(self.screen):
            self.menu_state = "two_players"
            self.number_players = 2
        if self.three_players_button.draw(self.screen):
            self.menu_state = "three_players"
            self.number_players = 3
        if self.four_players_button.draw(self.screen):
            self.menu_state = "choice_characters_1"
            self.number_players = 4
        if self.exit_button.draw(self.screen):
            self.menu_state = "main"

    def handle_one_player_menu(self):
        """Gère la sélection du nombre de bots pour 1 joueur"""
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
        if self.exit_button.draw(self.screen):
            self.menu_state = "play"

    def handle_two_players_menu(self):
        """Gère la sélection du nombre de bots pour 2 joueurs"""
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
        if self.exit_button.draw(self.screen):
            self.menu_state = "play"

    def handle_three_players_menu(self):
        """Gère la sélection du nombre de bots pour 3 joueurs"""
        self.draw_text_center(
            "Select the number of bots", self.font, self.TEXT_COL2, 50
        )
        if self.zero_player_button.draw(self.screen):
            self.menu_state = "choice_characters_1"
            self.number_bot = 0
        if self.one_player_button.draw(self.screen):
            self.menu_state = "choice_characters_1"
            self.number_bot = 1
        if self.exit_button.draw(self.screen):
            self.menu_state = "play"

    def draw_character_preview(self, char_index):
        """Affiche l'aperçu d'un personnage à l'écran"""
        try:
            idx = int(char_index)
        except Exception:
            idx = 0
        if idx and 1 <= idx <= len(self.image_ch):
            sel_img = self.image_ch[idx - 1]
            s = max(1.0, float(self.char_preview_scale))
            scaled = pyg.transform.scale(
                sel_img,
                (
                    int(sel_img.get_width() * s),
                    int(sel_img.get_height() * s),
                ),
            )
            self.screen.blit(scaled, (self.center_x(sel_img, 50), 127))

    def draw_small_character_preview(self, char_index, x_offset):
        """Affiche un petit aperçu d'un personnage"""
        if isinstance(char_index, int) and 1 <= char_index <= len(self.image_ch):
            prev_img = self.image_ch[char_index - 1]
            self.screen.blit(prev_img, (self.center_x(prev_img, x_offset), 345))

    def handle_character_selection(self, character_var, next_state, title):
        """Gère la sélection d'un personnage avec aperçu"""
        self.screen.blit(self.choice_chracters, (0, 0))
        self.draw_text(title, self.font, self.TEXT_COL, 70, 0)

        if self.Back_selection_character.draw(self.screen):
            # Déterminer l'état précédent
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
            (self.character_6_button, 6),
            (self.character_7_button, 7),
            (self.character_8_button, 8),
            (self.character_9_button, 9),
            (self.character_10_button, 10),
            (self.character_11_button, 11),
            (self.character_12_button, 12),
            (self.character_13_button, 13),
            (self.character_14_button, 14),
            (self.character_15_button, 15),
            (self.character_16_button, 16),
            (self.character_17_button, 17),
            (self.character_18_button, 18),
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

        # Afficher l'aperçu du personnage sélectionné
        self.draw_character_preview(character_var)

    def handle_choice_characters_1(self):
        """Gère la sélection du premier personnage"""
        self.screen.blit(self.choice_chracters, (0, 0))
        self.draw_text("Choose three characters", self.font, self.TEXT_COL, 70, 0)

        if self.Back_selection_character.draw(self.screen):
            self.menu_state = "play"

        character_buttons = [
            (self.character_1_button, 1),
            (self.character_2_button, 2),
            (self.character_3_button, 3),
            (self.character_4_button, 4),
            (self.character_5_button, 5),
            (self.character_6_button, 6),
            (self.character_7_button, 7),
            (self.character_8_button, 8),
            (self.character_9_button, 9),
            (self.character_10_button, 10),
            (self.character_11_button, 11),
            (self.character_12_button, 12),
            (self.character_13_button, 13),
            (self.character_14_button, 14),
            (self.character_15_button, 15),
            (self.character_16_button, 16),
            (self.character_17_button, 17),
            (self.character_18_button, 18),
        ]

        for button_obj, char_num in character_buttons:
            if button_obj.draw(self.screen):
                self.character_1 = char_num
                self.menu_state = "choice_characters_2"

        self.draw_character_preview(self.character_1)

    def handle_choice_characters_2(self):
        """Gère la sélection du deuxième personnage"""
        self.screen.blit(self.choice_chracters, (0, 0))
        self.draw_text("Choose two characters", self.font, self.TEXT_COL, 70, 0)

        if self.Back_selection_character.draw(self.screen):
            self.menu_state = "choice_characters_1"

        character_buttons = [
            (self.character_1_button, 1),
            (self.character_2_button, 2),
            (self.character_3_button, 3),
            (self.character_4_button, 4),
            (self.character_5_button, 5),
            (self.character_6_button, 6),
            (self.character_7_button, 7),
            (self.character_8_button, 8),
            (self.character_9_button, 9),
            (self.character_10_button, 10),
            (self.character_11_button, 11),
            (self.character_12_button, 12),
            (self.character_13_button, 13),
            (self.character_14_button, 14),
            (self.character_15_button, 15),
            (self.character_16_button, 16),
            (self.character_17_button, 17),
            (self.character_18_button, 18),
        ]

        for button_obj, char_num in character_buttons:
            if button_obj.draw(self.screen):
                self.character_2 = char_num
                self.menu_state = "choice_characters_3"

        # Afficher l'aperçu du 2e personnage (ou 1er s'il n'est pas encore choisi)
        if self.character_2:
            self.draw_character_preview(self.character_2)
            self.draw_small_character_preview(self.character_1, 50)
        else:
            self.draw_character_preview(self.character_1)

    def handle_choice_characters_3(self):
        """Gère la sélection du troisième personnage et affiche le bouton start"""
        self.screen.blit(self.choice_chracters, (0, 0))
        self.draw_text("Choose one character", self.font, self.TEXT_COL, 70, 0)

        if self.Back_selection_character.draw(self.screen):
            self.menu_state = "choice_characters_2"

        character_buttons = [
            (self.character_1_button, 1),
            (self.character_2_button, 2),
            (self.character_3_button, 3),
            (self.character_4_button, 4),
            (self.character_5_button, 5),
            (self.character_6_button, 6),
            (self.character_7_button, 7),
            (self.character_8_button, 8),
            (self.character_9_button, 9),
            (self.character_10_button, 10),
            (self.character_11_button, 11),
            (self.character_12_button, 12),
            (self.character_13_button, 13),
            (self.character_14_button, 14),
            (self.character_15_button, 15),
            (self.character_16_button, 16),
            (self.character_17_button, 17),
            (self.character_18_button, 18),
        ]

        for button_obj, char_num in character_buttons:
            if button_obj.draw(self.screen):
                self.character_3 = char_num

        # Afficher l'aperçu du 3e personnage (ou 2e s'il n'est pas encore choisi)
        if self.character_3:
            self.draw_character_preview(self.character_3)
            self.draw_small_character_preview(self.character_1, 50)
            self.draw_small_character_preview(self.character_2, 40)
        else:
            self.draw_character_preview(self.character_2)
            self.draw_small_character_preview(self.character_1, 50)

        # Afficher le bouton start si les 3 personnages sont choisis
        if self.character_3 and self.start_button.draw(self.screen):
            self.menu_state = "start game"
            self.etat = "game"

    def method_menu(self):
        """Méthode principale gérant tous les états du menu"""
        if self.menu_state == "main":
            self.handle_main_menu()
        elif self.menu_state == "settings":
            self.handle_settings_menu()
        elif self.menu_state == "creation_parameters_session_menu":
            self.handle_session_menu()

            # Fond du modal
            pyg.draw.rect(self.screen, (30, 30, 30), (350, 150, 600, 450))

            self.draw_text_center("Configuration", self.font, self.TEXT_COL, 170)

            self.input_box.rect.x = 500
            self.input_box.rect.y = 245
            self.input_box.draw(self.screen)

            self.draw_text(
                f"IA: {self.input_box.temp_nb_ia}",
                self.middle_font,
                self.TEXT_COL,
                380,
                320,
            )
            if self.input_box.btn_plus_ia.draw(self.screen):
                self.input_box.temp_nb_ia += 1
            if (
                self.input_box.btn_moins_ia.draw(self.screen)
                and self.input_box.temp_nb_ia > 0
            ):
                self.input_box.temp_nb_ia -= 1

            if self.input_box.validate_button.draw(self.screen):
                new_s = Session(self)
                new_s.titre = (
                    self.input_box.text if self.input_box.text != "" else "Sans titre"
                )
                new_s.nb_bots = self.input_box.temp_nb_ia

                new_s.y = 79 + (len(self.sessions) * new_s.gap)

                self.sessions.append(new_s)

                # Envoyer la session au serveur
                self.send_session_to_server(new_s)

                self.menu_state = "play"

        elif self.menu_state == "play":
            self.input_box.clean()
            self.handle_session_menu()
            # self.handle_play_menu()
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
        elif self.menu_state == "start game":
            self.etat = "game"
        else:
            self.draw_text_center("Press Space to start", self.font, self.TEXT_COL, 250)


class Session:
    def __init__(self, menu):
        self.menu = menu
        self.screen = menu.screen

        # Chargement et redimensionnement des assets
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

        # Paramètres qui seront remplis à la création
        self.titre = "Sans titre"
        self.nb_bots = 0
        self.nb_players = 1

    def to_dict(self):
        """
        Convert session to dictionary for JSON serialization.

        Returns:
            dict: Session data that can be serialized to JSON
        """
        return {
            "titre": self.titre,
            "nb_bots": self.nb_bots,
            "nb_players": self.nb_players,
            "y": self.y,
            "gap": self.gap,
        }

    @staticmethod
    def from_dict(data, menu):
        """
        Create a Session instance from dictionary data.

        Args:
            data (dict): Dictionary containing session data
            menu: Menu instance for rendering

        Returns:
            Session: New Session instance with data from dictionary
        """
        session = Session(menu)
        session.titre = data.get("titre", "Sans titre")
        session.nb_bots = data.get("nb_bots", 0)
        session.nb_players = data.get("nb_players", 1)
        session.y = data.get("y", 79)
        session.gap = data.get("gap", 125)
        return session

    def draw_session(self, y_scrollé):
        """Affiche la ligne de session avec ses paramètres"""
        self.join_button.rect.y = y_scrollé + 152

        # Barre de fond
        self.screen.blit(self.bar_session, (310, y_scrollé))

        # Nom de la session (Text)
        self.menu.draw_text(self.titre, self.menu.font, "Black", 391, y_scrollé + 113)

        # Bouton Rejoindre et son texte
        if self.join_button.draw(self.screen):
            print(f"Tentative de rejoindre : {self.titre}")
            self.menu_state = "choice_characters_1"

        self.menu.draw_text(
            "Join", self.menu.middle_font, "Black", 745, y_scrollé + 186
        )

        # Décorations (Splash et Star Bar)
        self.screen.blit(self.splash_session, (845, y_scrollé + 100))
        self.screen.blit(self.star_bar_session, (357, y_scrollé + 87))

        # Icones (IA et Joueurs)
        self.screen.blit(self.bot_session, (450, y_scrollé + 188))
        self.screen.blit(self.player_session, (530, y_scrollé + 188))

        # VALEURS des paramètres
        self.menu.draw_text(
            str(self.nb_bots), self.menu.middle_font, "Black", 490, y_scrollé + 188
        )
        self.menu.draw_text(
            str(self.nb_players), self.menu.middle_font, "Black", 570, y_scrollé + 188
        )


class InputBox:
    def __init__(self, x, y, w, h, text="", button_session=None, menu=None):
        self.rect = pyg.Rect(x, y, w, h)
        self.color = pyg.Color("lightskyblue3")
        self.text = text
        self.font = pyg.font.SysFont("Arial", 24)
        self.txt_surface = self.font.render(text, True, self.color)
        self.active = False
        self.screen = menu.screen

        # Variables parameters
        self.temp_nb_ia = 0
        self.temp_nb_players = 1

        self.draw_text(text="-", font=self.font, text_col="Black", x=600, y=320)
        self.btn_plus_ia = button.Button(600, 320, button_session, 0.5)
        self.draw_text(text="+", font=self.font, text_col="Black", x=530, y=320)
        self.btn_moins_ia = button.Button(530, 320, button_session, 0.5)

        self.draw_text(text="Confirm", font=self.font, text_col="Black", x=550, y=520)
        self.validate_button = button.Button(550, 520, button_session, 0.5)

    def handle_event(self, event):
        if event.type == pyg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = (
                pyg.Color("dodgerblue2") if self.active else pyg.Color("lightskyblue3")
            )

        if event.type == pyg.KEYDOWN and self.active:
            if event.key == pyg.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < 15:
                self.text += event.unicode
            self.txt_surface = self.font.render(self.text, True, (255, 255, 255))

    def draw(self, screen):
        # Dessin du texte de l'InputBox et son contour
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pyg.draw.rect(screen, self.color, self.rect, 2)

        # Rectangle derrière le '-' (Bouton Plus IA)
        pyg.draw.rect(screen, (255, 0, 0), (600, 320, 30, 30))
        self.draw_text(text="+", font=self.font, text_col="Black", x=607, y=320)

        # Rectangle derrière le '+' (Bouton Moins IA)
        pyg.draw.rect(screen, (255, 0, 0), (530, 320, 30, 30))
        self.draw_text(text="-", font=self.font, text_col="Black", x=535, y=320)

        # Rectangle derrière le 'Confirm' (Bouton Valider)
        pyg.draw.rect(screen, (255, 0, 0), (545, 515, 110, 40))
        self.draw_text(text="Confirm", font=self.font, text_col="Black", x=550, y=520)

    def draw_text(self, text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        self.screen.blit(img, (x, y))

    def clean(self):
        self.text = ""
        self.txt_surface = self.font.render(self.text, True, self.color)
        self.active = False
        self.color = pyg.Color("lightskyblue3")
        self.temp_nb_ia = 0
        self.temp_nb_players = 1
