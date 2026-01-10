import pygame as pyg
import sys
from . import button
import game.characters as player_module


class Menu:
    def __init__(self, width=1280, height=720, fullscreen=False):
        # Configuration de la fenêtre
        self.width = width
        self.height = height
        self.fullscreen = fullscreen

        # This are temporary variables for player
        self.player = player_module.Furnace()

        # Variables
        self.etat = "menu"
        # game variables
        self.game_started = False
        self.menu_state = "main"
        self.number_players = 0
        self.number_bot = 0
        self.character_1 = 0
        self.character_2 = 0
        self.character_3 = 0

        # Initialisation Pygame avant chargement des assets
        pyg.init()

        # initialisation de l'affichage (doit être fait avant les convert_alpha)
        flags = pyg.FULLSCREEN if self.fullscreen else 0
        self.screen = pyg.display.set_mode((self.width, self.height), flags)
        pyg.display.set_caption("Jeu Multijoueur")
        self.clock = pyg.time.Clock()

        # define font
        self.font = pyg.font.SysFont("arialblack", 40)

        # define colors
        self.TEXT_COL = (255, 255, 255)
        self.TEXT_COL2 = (255, 0, 0)

        self.wallpaper = pyg.image.load(
            "assets/wallpapers/wallpaper.png"
        ).convert_alpha()
        self.choice_chracters = pyg.image.load(
            "assets/wallpapers/SELECT-SCREEN.png"
        ).convert_alpha()
        # Mettre à l'échelle l'image de sélection pour remplir la fenêtre
        self.choice_chracters = pyg.transform.scale(
            self.choice_chracters, (self.width, self.height)
        )

        # load button images
        play_img = pyg.image.load("assets/buttons/button_play.png").convert_alpha()
        settings_img = pyg.image.load(
            "assets/buttons/button_settings.png"
        ).convert_alpha()
        exit_img = pyg.image.load("assets/buttons/button_exit.png").convert_alpha()
        video_img = pyg.image.load("assets/buttons/button_video.png").convert_alpha()
        audio_img = pyg.image.load("assets/buttons/button_audio.png").convert_alpha()
        keys_img = pyg.image.load("assets/buttons/button_keys.png").convert_alpha()
        back_img = pyg.image.load("assets/buttons/button_back.png").convert_alpha()
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

        # character buttons
        image_ch = []
        for i in range(1, 19):
            Img = pyg.image.load(
                f"assets/characters_selection/Character_{i}.png"
            ).convert_alpha()
            image_ch.append(Img)

        # garder la liste d'images pour l'affichage du personnage sélectionné
        self.image_ch = image_ch

        # échelle par défaut pour l'aperçu du personnage sélectionné (modifiable)
        self.char_preview_scale = 9.5

        # create button instances (centrés horizontalement)
        self.play_button = button.Button(self.center_x(play_img, 1), 200, play_img, 1.5)
        self.settings_button = button.Button(
            self.center_x(settings_img, 1), 350, settings_img, 1.5
        )
        self.exit_button = button.Button(self.center_x(exit_img, 1), 500, exit_img, 1.5)
        self.video_button = button.Button(
            self.center_x(video_img, 1), 200, video_img, 1
        )
        self.audio_button = button.Button(
            self.center_x(audio_img, 1), 350, audio_img, 1
        )
        self.keys_button = button.Button(self.center_x(keys_img, 1), 500, keys_img, 1)
        self.back_button = button.Button(self.center_x(back_img, 1), 700, back_img, 1)
        self.zero_player_button = button.Button(
            self.center_x(zero_player_img, 0.3), 500, zero_player_img, 0.3
        )
        self.one_player_button = button.Button(
            self.center_x(one_player_img, 2), 200, one_player_img, 1
        )
        self.two_players_button = button.Button(
            self.center_x(two_players_img, -0.5), 200, two_players_img, 1
        )
        self.three_players_button = button.Button(
            self.center_x(three_players_img, 2), 350, three_players_img, 1
        )
        self.four_players_button = button.Button(
            self.center_x(four_players_img, -0.5), 350, four_players_img, 1
        )
        self.Back_selection_character = button.Button(
            self.center_x(Back_selection_character_img, 77),
            10,
            Back_selection_character_img,
            2.7,
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

    def method_menu (self):
        # main menu
        if self.menu_state == "main":
            if self.play_button.draw(self.screen):
                self.menu_state = "play"
            if self.settings_button.draw(self.screen):
                self.menu_state = "settings"
            if self.exit_button.draw(self.screen):
                # quitter proprement l'application
                pyg.quit()
                sys.exit(0)

        # settings menu
        elif self.menu_state == "settings":
            if self.video_button.draw(self.screen):
                print("Video Settings")
            if self.audio_button.draw(self.screen):
                print("Audio Settings")
            if self.keys_button.draw(self.screen):
                print("Keys Settings")
            if self.back_button.draw(self.screen):
                self.menu_state = "main"

        # play -> choose number of players
        elif self.menu_state == "play":
            self.draw_text_center(
                "Select the number of players",
                self.font,
                self.TEXT_COL2,
                50,
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
            if self.back_button.draw(self.screen):
                self.menu_state = "main"

        # one player -> choose number of bots
        elif self.menu_state == "one_player":
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
            if self.back_button.draw(self.screen):
                self.menu_state = "play"

        # two players -> choose number of bots (example)
        elif self.menu_state == "two_players":
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
            if self.back_button.draw(self.screen):
                self.menu_state = "play"

        # three_players / four_players can be handled similarly if needed
        elif self.menu_state == "three_players":
            self.draw_text_center(
                "Select the number of bots", self.font, self.TEXT_COL2, 50
            )
            if self.zero_player_button.draw(self.screen):
                self.menu_state = "choice_characters_1"
                self.number_bot = 0
            if self.one_player_button.draw(self.screen):
                self.menu_state = "choice_characters"
                self.number_bot = 1
            if self.back_button.draw(self.screen):
                self.menu_state = "play"

        elif self.menu_state == "choice_characters_1":
            self.screen.blit(self.choice_chracters, (0, 0))
            self.draw_text(
                "Choose three characters", self.font, self.TEXT_COL, 70, 0
            )
            if self.Back_selection_character.draw(self.screen):
                self.menu_state = "play"
            # chaque bouton définit l'indice (1..18) du personnage sélectionné
            if self.character_1_button.draw(self.screen):
                self.character_1 = 1
                self.menu_state = "choice_characters_2"
            if self.character_2_button.draw(self.screen):
                self.character_1 = 2
                self.menu_state = "choice_characters_2"
            if self.character_3_button.draw(self.screen):
                self.character_1 = 3
                self.menu_state = "choice_characters_2"
            if self.character_4_button.draw(self.screen):
                self.character_1 = 4
                self.menu_state = "choice_characters_2"
            if self.character_5_button.draw(self.screen):
                self.character_1 = 5
                self.menu_state = "choice_characters_2"
            if self.character_6_button.draw(self.screen):
                self.character_1 = 6
                self.menu_state = "choice_characters_2"
            if self.character_7_button.draw(self.screen):
                self.character_1 = 7
                self.menu_state = "choice_characters_2"
            if self.character_8_button.draw(self.screen):
                self.character_1 = 8
                self.menu_state = "choice_characters_2"
            if self.character_9_button.draw(self.screen):
                self.character_1 = 9
                self.menu_state = "choice_characters_2"
            if self.character_10_button.draw(self.screen):
                self.character_1 = 10
                self.menu_state = "choice_characters_2"
            if self.character_11_button.draw(self.screen):
                self.character_1 = 11
                self.menu_state = "choice_characters_2"
            if self.character_12_button.draw(self.screen):
                self.character_1 = 12
                self.menu_state = "choice_characters_2"
            if self.character_13_button.draw(self.screen):
                self.character_1 = 13
                self.menu_state = "choice_characters_2"
            if self.character_14_button.draw(self.screen):
                self.character_1 = 14
                self.menu_state = "choice_characters_2"
            if self.character_15_button.draw(self.screen):
                self.character_1 = 15
                self.menu_state = "choice_characters_2"
            if self.character_16_button.draw(self.screen):
                self.character_1 = 16
                self.menu_state = "choice_characters_2"
            if self.character_17_button.draw(self.screen):
                self.character_1 = 17
                self.menu_state = "choice_characters_2"
            if self.character_18_button.draw(self.screen):
                self.character_1 = 18
                self.menu_state = "choice_characters_2"
            # Afficher l'aperçu du personnage sélectionné (si un indice est présent)
            try:
                idx = int(self.character_1)
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

        elif self.menu_state == "choice_characters_2":
            self.screen.blit(self.choice_chracters, (0, 0))
            self.draw_text(
                "Choose two characters", self.font, self.TEXT_COL, 70, 0
            )

            if self.Back_selection_character.draw(self.screen):
                self.menu_state = "choice_characters_1"
            if self.character_1_button.draw(self.screen):
                self.character_2 = 1
                self.menu_state = "choice_characters_3"
            if self.character_2_button.draw(self.screen):
                self.character_2 = 2
                self.menu_state = "choice_characters_3"
            if self.character_3_button.draw(self.screen):
                self.character_2 = 3
                self.menu_state = "choice_characters_3"
            if self.character_4_button.draw(self.screen):
                self.character_2 = 4
                self.menu_state = "choice_characters_3"
            if self.character_5_button.draw(self.screen):
                self.character_2 = 5
                self.menu_state = "choice_characters_3"
            if self.character_6_button.draw(self.screen):
                self.character_2 = 6
                self.menu_state = "choice_characters_3"
            if self.character_7_button.draw(self.screen):
                self.character_2 = 7
                self.menu_state = "choice_characters_3"
            if self.character_8_button.draw(self.screen):
                self.character_2 = 8
                self.menu_state = "choice_characters_3"
            if self.character_9_button.draw(self.screen):
                self.character_2 = 9
                self.menu_state = "choice_characters_3"
            if self.character_10_button.draw(self.screen):
                self.character_2 = 10
                self.menu_state = "choice_characters_3"
            if self.character_11_button.draw(self.screen):
                self.character_2 = 11
                self.menu_state = "choice_characters_3"
            if self.character_12_button.draw(self.screen):
                self.character_2 = 12
                self.menu_state = "choice_characters_3"
            if self.character_13_button.draw(self.screen):
                self.character_2 = 13
                self.menu_state = "choice_characters_3"
            if self.character_14_button.draw(self.screen):
                self.character_2 = 14
                self.menu_state = "choice_characters_3"
            if self.character_15_button.draw(self.screen):
                self.character_2 = 15
                self.menu_state = "choice_characters_3"
            if self.character_16_button.draw(self.screen):
                self.character_2 = 16
                self.menu_state = "choice_characters_3"
            if self.character_17_button.draw(self.screen):
                self.character_2 = 17
                self.menu_state = "choice_characters_3"
            if self.character_18_button.draw(self.screen):
                self.character_2 = 18
                self.menu_state = "choice_characters_3"

            # Afficher le grand aperçu : si `character_2` est choisi, l'afficher grand,
            # sinon afficher en grand `character_1` (sélection précédente).
            try:
                idx2 = int(self.character_2)
            except Exception:
                idx2 = 0
            if idx2 and 1 <= idx2 <= len(self.image_ch):
                # grand aperçu pour le 2e personnage choisi
                sel_img = self.image_ch[idx2 - 1]
                s = max(1.0, float(self.char_preview_scale))
                scaled = pyg.transform.scale(
                    sel_img,
                    (
                        int(sel_img.get_width() * s),
                        int(sel_img.get_height() * s),
                    ),
                )
                self.screen.blit(scaled, (self.center_x(sel_img, 50), 127))
                # afficher le premier en petit en bas
                if isinstance(
                    self.character_1, int
                ) and 1 <= self.character_1 <= len(self.image_ch):
                    prev_img = self.image_ch[self.character_1 - 1]
                    self.screen.blit(
                        prev_img, (self.center_x(prev_img, 50), 345)
                    )
            else:
                # pas encore de 2e choisi : afficher le 1er en grand
                if isinstance(
                    self.character_1, int
                ) and 1 <= self.character_1 <= len(self.image_ch):
                    sel_img = self.image_ch[self.character_1 - 1]
                    s = max(1.0, float(self.char_preview_scale))
                    scaled = pyg.transform.scale(
                        sel_img,
                        (
                            int(sel_img.get_width() * s),
                            int(sel_img.get_height() * s),
                        ),
                    )
                    self.screen.blit(
                        scaled, (self.center_x(sel_img, 50), 127)
                    )

        elif self.menu_state == "choice_characters_3":
            self.screen.blit(self.choice_chracters, (0, 0))
            self.draw_text(
                "Choose one character", self.font, self.TEXT_COL, 70, 0
            )

            if self.Back_selection_character.draw(self.screen):
                self.menu_state = "choice_characters_2"
            if self.character_1_button.draw(self.screen):
                self.character_3 = 1
                self.menu_state = "choice_characters_3"
            if self.character_2_button.draw(self.screen):
                self.character_3 = 2
                self.menu_state = "choice_characters_3"
            if self.character_3_button.draw(self.screen):
                self.character_3 = 3
                self.menu_state = "choice_characters_3"
            if self.character_4_button.draw(self.screen):
                self.character_3 = 4
                self.menu_state = "choice_characters_3"
            if self.character_5_button.draw(self.screen):
                self.character_3 = 5
                self.menu_state = "choice_characters_3"
            if self.character_6_button.draw(self.screen):
                self.character_3 = 6
                self.menu_state = "choice_characters_3"
            if self.character_7_button.draw(self.screen):
                self.character_3 = 7
                self.menu_state = "choice_characters_3"
            if self.character_8_button.draw(self.screen):
                self.character_3 = 8
                self.menu_state = "choice_characters_3"
            if self.character_9_button.draw(self.screen):
                self.character_3 = 9
                self.menu_state = "choice_characters_3"
            if self.character_10_button.draw(self.screen):
                self.character_3 = 10
                self.menu_state = "choice_characters_3"
            if self.character_11_button.draw(self.screen):
                self.character_3 = 11
                self.menu_state = "choice_characters_3"
            if self.character_12_button.draw(self.screen):
                self.character_3 = 12
                self.menu_state = "choice_characters_3"
            if self.character_13_button.draw(self.screen):
                self.character_3 = 13
                self.menu_state = "choice_characters_3"
            if self.character_14_button.draw(self.screen):
                self.character_3 = 14
                self.menu_state = "choice_characters_3"
            if self.character_15_button.draw(self.screen):
                self.character_3 = 15
                self.menu_state = "choice_characters_3"
            if self.character_16_button.draw(self.screen):
                self.character_3 = 16
                self.menu_state = "choice_characters_3"
            if self.character_17_button.draw(self.screen):
                self.character_3 = 17
                self.menu_state = "choice_characters_3"
            if self.character_18_button.draw(self.screen):
                self.character_3 = 18
                self.menu_state = "choice_characters_3"
            # Afficher l'aperçu du personnage sélectionné (si un indice est présent)
            try:
                idx3 = int(self.character_3)
            except Exception:
                idx3 = 0
            # Si le 3e est choisi -> grand aperçu du 3e
            if idx3 and 1 <= idx3 <= len(self.image_ch):
                sel_img = self.image_ch[idx3 - 1]
                s = max(1.0, float(self.char_preview_scale))
                scaled = pyg.transform.scale(
                    sel_img,
                    (
                        int(sel_img.get_width() * s),
                        int(sel_img.get_height() * s),
                    ),
                )
                self.screen.blit(scaled, (self.center_x(sel_img, 50), 127))
                # afficher premiers en petit
                if isinstance(
                    self.character_1, int
                ) and 1 <= self.character_1 <= len(self.image_ch):
                    prev1 = self.image_ch[self.character_1 - 1]
                    self.screen.blit(prev1, (self.center_x(prev1, 50), 345))
                if isinstance(
                    self.character_2, int
                ) and 1 <= self.character_2 <= len(self.image_ch):
                    prev2 = self.image_ch[self.character_2 - 1]
                    self.screen.blit(prev2, (self.center_x(prev2, 40), 345))
            else:
                # si pas encore de 3e choisi, afficher le 2e en grand (si présent)
                if isinstance(
                    self.character_2, int
                ) and 1 <= self.character_2 <= len(self.image_ch):
                    sel_img = self.image_ch[self.character_2 - 1]
                    s = max(1.0, float(self.char_preview_scale))
                    scaled = pyg.transform.scale(
                        sel_img,
                        (
                            int(sel_img.get_width() * s),
                            int(sel_img.get_height() * s),
                        ),
                    )
                    self.screen.blit(
                        scaled, (self.center_x(sel_img, 50), 127)
                    )
                    # afficher le 1er en petit
                    if isinstance(
                        self.character_1, int
                    ) and 1 <= self.character_1 <= len(self.image_ch):
                        prev1 = self.image_ch[self.character_1 - 1]
                        self.screen.blit(
                            prev1, (self.center_x(prev1, 50), 345)
                        )

        elif self.menu_state == "start game":
            self.etat = "game"
            # self.player = player_module.Le character choisis

        else:
            self.draw_text_center(
                "Press Space to start", self.font, self.TEXT_COL, 250
            )