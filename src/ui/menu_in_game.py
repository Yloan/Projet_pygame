import pygame as pyg
import sys
from . import button
from . import animated_button
import game.characters as player_module

from utils.paths import get_asset_path
from ui import Buttons as ObjButton

# ============================================================================
# CONSTANTS - Menu configuration
# ============================================================================
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
BUTTON_SCALE = 2

class Menu_in_game:
    def __init__(self, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, fullscreen=False):
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
        self.etat = "menu_in_game"  # Current menu state
        self.game_started = True
        self.menu_state = "main"  # Main submenu state


        #define front
        font = pyg.font.SysFont("arialblack", 40)

        #define colors
        TEXT_COL = (255, 255, 255)

        # ====================================================================
        # LOAD BUTTON IMAGES
        # ====================================================================
        # Main menu buttons
        

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
        self.TEXT_COL = (255, 255, 255)  # White

        # ====================================================================
        # LOAD BUTTON IMAGES
        # ====================================================================
        # Main menu buttons
        

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

        # ====================================================================
        # CREATE BUTTON INSTANCES
        # ====================================================================
        # Main menu buttons with animations (horizontally centered)
        self.play_button = animated_button.AnimatedButton(
            self.center_x(self.play_button_frames[0], 1.5), 
            370, 
            self.play_button_frames, 
            BUTTON_SCALE,
            animation_speed=1
        )
        self.settings_button = animated_button.AnimatedButton(
            self.center_x(self.settings_button_frames[0], 1.5), 
            455, 
            self.settings_button_frames, 
            2,
            animation_speed=1
        )
        self.exit_button = animated_button.AnimatedButton(
            self.center_x(self.exit_button_frames[0], 1.5), 
            540, 
            self.exit_button_frames, 
            2,
            animation_speed=1
        )
        self.video_button = button.Button(
            self.center_x(video_img, 1) - 350, 350, video_img, 1
        )
        self.audio_button = button.Button(
            self.center_x(audio_img, 1), 350, audio_img, 1
        )
        self.keys_button = button.Button(self.center_x(keys_img, 1) + 350, 350, keys_img, 1)
        self.back_button = button.Button(self.center_x(back_img, 1), 700, back_img, 1)
        
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
            self.menu_state = "menu"
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
    def method_menu_in_game(self):
        """Méthode principale gérant tous les états du menu"""
        if self.menu_state == "main":
            self.handle_main_menu()
        elif self.menu_state == "settings":
            self.handle_settings_menu()
        elif self.menu_state == "play":
            self.handle_play_menu()
        elif self.menu_state == "menu":
            self.method_menu()