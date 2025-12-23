# Point d'entrée du jeu : boucle principale et envoi d'informations au serveur

import socket
import threading
import queue
import time
import pygame as pyg
from ui.server import Serveur
from ui.console import print_info, print_error, print_warning, print_network, print_success
from game.map_laoder import MapLoader
import os
import game.characters as player_module
import ui.button as button


class Game:
    def __init__(self, width=1280, height=720, fullscreen=False):

        self.x_temp = 270
        self.y_temp = 280
        self.vit_temp = 5

        # Configuration de la fenêtre
        self.width = width
        self.height = height
        self.fullscreen = fullscreen

        # Maps & ressources
        

        # Variables
        self.etat = "menu"
        # game variables
        self.game_started = False
        self.menu_state = "main"
        self.number_players = 0
        self.number_bot = 0
        self.character_1 = 0

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

        self.wallpaper = pyg.image.load("assets/wallpapers/wallpaper.png").convert_alpha()
        self.choice_chracters = pyg.image.load("assets/wallpapers/SELECT-SCREEN.png").convert_alpha()
        # Mettre à l'échelle l'image de sélection pour remplir la fenêtre
        self.choice_chracters = pyg.transform.scale(self.choice_chracters, (self.width, self.height))

        # load button images
        play_img = pyg.image.load("assets/buttons/button_play.png").convert_alpha()
        settings_img = pyg.image.load("assets/buttons/button_settings.png").convert_alpha()
        exit_img = pyg.image.load("assets/buttons/button_exit.png").convert_alpha()
        video_img = pyg.image.load("assets/buttons/button_video.png").convert_alpha()
        audio_img = pyg.image.load("assets/buttons/button_audio.png").convert_alpha()
        keys_img = pyg.image.load("assets/buttons/button_keys.png").convert_alpha()
        back_img = pyg.image.load("assets/buttons/button_back.png").convert_alpha()
        zero_player_img = pyg.image.load("assets/buttons/button_zero_player.png").convert_alpha()
        one_player_img = pyg.image.load("assets/buttons/button_one_player.png").convert_alpha()
        two_players_img = pyg.image.load("assets/buttons/button_two_players.png").convert_alpha()
        three_players_img = pyg.image.load("assets/buttons/button_trhee_players.png").convert_alpha()
        four_players_img = pyg.image.load("assets/buttons/button_four_players.png").convert_alpha()

        #character buttons
        Character_1_img = pyg.image.load("assets/characters_selection/Character_1.png").convert_alpha()
        Character_2_img = pyg.image.load("assets/characters_selection/Character_2.png").convert_alpha()
        Character_3_img = pyg.image.load("assets/characters_selection/Character_3.png").convert_alpha()
        Character_4_img = pyg.image.load("assets/characters_selection/Character_4.png").convert_alpha()
        Character_5_img = pyg.image.load("assets/characters_selection/Character_5.png").convert_alpha()
        Character_6_img = pyg.image.load("assets/characters_selection/Character_6.png").convert_alpha()
        Character_7_img = pyg.image.load("assets/characters_selection/Character_7.png").convert_alpha()
        Character_8_img = pyg.image.load("assets/characters_selection/Character_8.png").convert_alpha()
        Character_9_img = pyg.image.load("assets/characters_selection/Character_9.png").convert_alpha()
        Character_10_img = pyg.image.load("assets/characters_selection/Character_10.png").convert_alpha()
        Character_11_img = pyg.image.load("assets/characters_selection/Character_11.png").convert_alpha()
        Character_12_img = pyg.image.load("assets/characters_selection/Character_12.png").convert_alpha()
        Character_13_img = pyg.image.load("assets/characters_selection/Character_13.png").convert_alpha()
        Character_14_img = pyg.image.load("assets/characters_selection/Character_14.png").convert_alpha()
        Character_15_img = pyg.image.load("assets/characters_selection/Character_15.png").convert_alpha()
        Character_16_img = pyg.image.load("assets/characters_selection/Character_16.png").convert_alpha()
        Character_17_img = pyg.image.load("assets/characters_selection/Character_17.png").convert_alpha()
        Character_18_img = pyg.image.load("assets/characters_selection/Character_18.png").convert_alpha()


        # create button instances (centrés horizontalement)
        self.play_button = button.Button(self.center_x(play_img, 1), 200, play_img, 1.5)
        self.settings_button = button.Button(self.center_x(settings_img, 1), 350, settings_img, 1.5)
        self.exit_button = button.Button(self.center_x(exit_img, 1), 500, exit_img, 1.5)
        self.video_button = button.Button(self.center_x(video_img, 1), 200, video_img, 1)
        self.audio_button = button.Button(self.center_x(audio_img, 1), 350, audio_img, 1)
        self.keys_button = button.Button(self.center_x(keys_img, 1), 500, keys_img, 1)
        self.back_button = button.Button(self.center_x(back_img, 1), 700, back_img, 1)
        self.zero_player_button = button.Button(self.center_x(zero_player_img, 0.3), 500, zero_player_img, 0.3)
        self.one_player_button = button.Button(self.center_x(one_player_img, 2), 200, one_player_img, 1)
        self.two_players_button = button.Button(self.center_x(two_players_img, -0.5), 200, two_players_img, 1)
        self.three_players_button = button.Button(self.center_x(three_players_img, 2), 350, three_players_img, 1)
        self.four_players_button = button.Button(self.center_x(four_players_img, -0.5), 350, four_players_img, 1)
        
        # character buttons left
        self.character_1_button = button.Button(self.center_x(Character_1_img, 25), 125, Character_1_img, 4)
        self.character_2_button = button.Button(self.center_x(Character_2_img, 12), 125, Character_2_img, 4)
        self.character_3_button = button.Button(self.center_x(Character_3_img, 25), 240, Character_3_img, 4)
        self.character_4_button = button.Button(self.center_x(Character_4_img, 12.5), 240, Character_4_img, 4)
        self.character_5_button = button.Button(self.center_x(Character_5_img, 24.4), 355, Character_5_img, 4)
        self.character_6_button = button.Button(self.center_x(Character_6_img, 12.5), 355, Character_6_img, 4)
        self.character_7_button = button.Button(self.center_x(Character_7_img, 25), 470, Character_7_img, 4)
        self.character_8_button = button.Button(self.center_x(Character_8_img, 12.5), 470, Character_8_img, 4)
        self.character_9_button = button.Button(self.center_x(Character_9_img, 19), 582, Character_9_img, 4)

        # character buttons right
        self.character_10_button = button.Button(self.center_x(Character_10_img, -17), 125, Character_10_img, 4)
        self.character_11_button = button.Button(self.center_x(Character_11_img, -4), 125, Character_11_img, 4)
        self.character_12_button = button.Button(self.center_x(Character_12_img, -16), 240, Character_12_img, 4)
        self.character_13_button = button.Button(self.center_x(Character_13_img, -4), 240, Character_13_img, 4)
        self.character_14_button = button.Button(self.center_x(Character_14_img, -16.2), 355, Character_14_img, 4)
        self.character_15_button = button.Button(self.center_x(Character_15_img, -4.1), 355, Character_15_img, 4)
        self.character_16_button = button.Button(self.center_x(Character_16_img, -16.2), 470, Character_16_img, 4)
        self.character_17_button = button.Button(self.center_x(Character_17_img, -4.1), 470, Character_17_img, 4)
        self.character_18_button = button.Button(self.center_x(Character_18_img, -11), 582, Character_18_img, 4)

        # loader de map (résout correctement les chemins)
        map_loader = MapLoader(None)
        background, foreground = map_loader.load_map()
        self.map_back = pyg.transform.scale(background, (self.width, self.height))
        self.map_front = foreground

        # chargement des sprites du joueur (classe Furnace dans game/characters)
        self.player = player_module.Furnace()
        self.running = False

        # Configuration réseau
        self.host = '0.0.0.0'
        self.port = 12345
        self._client_socket = None
        self._client_lock = threading.Lock()
        self._send_queue = queue.Queue()

        # Copier les frames et dimensions du joueur pour accès direct
        try:
            self.frames_IDLE = self.player.frames_IDLE
            self.frame_IDLE_left = self.player.frame_IDLE_left
            self.fram_WALK = self.player.fram_WALK
            self.frame_WALK_left = self.player.frame_WALK_left
            self.frame_width = self.player.frame_width
            self.frame_height = self.player.frame_height
        except Exception:
            # fallback pour éviter crash si attributs manquants
            self.frames_IDLE = []
            self.frame_IDLE_left = []
            self.fram_WALK = []
            self.frame_WALK_left = []
            self.frame_width = 32
            self.frame_height = 32

    def draw_text(self, text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        self.screen.blit(img, (x, y))

    def draw_text_center(self, text, font, text_col, y):
        """Render text centered horizontally at vertical position `y`."""
        img = font.render(text, True, text_col)
        x = (self.width - img.get_width()) // 2
        self.screen.blit(img, (x, y))

    def center_x(self, image, scale=1):
        """Retourne la coordonnée x pour centrer `image` horizontalement dans la fenêtre.

        `scale` correspond au facteur passé au constructeur `Button` (par défaut 1).
        """
        w = int(image.get_width() * scale)
        return (self.width - w) // 2

    def _connect_to_server(self):
        """Établit une connexion persistante au serveur."""
        try:
            if self._client_socket:
                try:
                    self._client_socket.close()
                except:
                    pass
            
            self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._client_socket.settimeout(2.0)
            self._client_socket.connect((self.host, self.port))
            print_success(f"Connecté au serveur {self.host}:{self.port}")
            
            # Démarrer thread de réception et d'envoi
            threading.Thread(target=self._receive_loop, daemon=True).start()
            threading.Thread(target=self._send_loop, daemon=True).start()
            
        except Exception as e:
            print_error(f"Erreur de connexion au serveur: {e}")
            self._client_socket = None

    def _receive_loop(self):
        """Thread de réception des messages du serveur."""
        while self.running:
            if not self._client_socket:
                time.sleep(0.5)
                continue
            try:
                data = self._client_socket.recv(1024)
                if not data:
                    print_warning('Connexion fermée par le serveur')
                    # provoquer une reconnexion
                    try:
                        self._client_socket.close()
                    except Exception:
                        pass
                    self._client_socket = None
                    if self.running:
                        time.sleep(1.0)
                        self._connect_to_server()
                    break
                print_network(f"Message reçu: {data.decode('utf-8')}")
            except socket.timeout:
                continue
            except Exception as e:
                print_error(f"Erreur réception: {e}")
                try:
                    if self._client_socket:
                        self._client_socket.close()
                except Exception:
                    pass
                self._client_socket = None
                if self.running:
                    time.sleep(1.0)
                    self._connect_to_server()
                break

    def _send_loop(self):
        """Thread d'envoi des messages au serveur."""
        while self.running:
            try:
                message = self._send_queue.get(timeout=0.5)
            except queue.Empty:
                continue
            try:
                if self._client_socket:
                    self._client_socket.send(message.encode('utf-8'))
                else:
                    print_warning(f"Non connecté, message non envoyé: {message}")
                    try:
                        self._send_queue.put_nowait(message)
                    except Exception:
                        pass
                    if self.running:
                        time.sleep(1.0)
                        self._connect_to_server()
            except Exception as e:
                print_error(f"Erreur envoi: {e}")
                if self._client_socket:
                    try:
                        self._client_socket.close()
                    except Exception:
                        pass
                self._client_socket = None
                try:
                    self._send_queue.put_nowait(message)
                except Exception:
                    pass
                if self.running:
                    time.sleep(1.0)
                    self._connect_to_server()

    def send_to_server(self, message='Bonjour serveur'):
        """Ajoute un message à la file d'envoi."""
        self._send_queue.put(message)

    def shutdown(self):
        """Arrête proprement la logique réseau et ferme Pygame."""
        print_info('Arrêt du jeu : fermeture connexion et threads')
        self.running = False
        # fermer la socket client
        with self._client_lock:
            try:
                if self._client_socket:
                    self._client_socket.shutdown(socket.SHUT_RDWR)
                    self._client_socket.close()
            except Exception:
                pass
            self._client_socket = None

        try:
            while not self._send_queue.empty():
                self._send_queue.get_nowait()
        except Exception:
            pass

        try:
            pyg.quit()
        except Exception:
            pass

    def run(self):
        # Démarrer le jeu et établir la connexion réseau
        self.running = True
        frame_IDLE = 0
        frame_WALK = 0
        tem_an_IDLE = 0
        tem_an_WALK = 0
        frame_walk_dir = 'right'
        self._connect_to_server()
        screen = self.screen
        while self.running:
            if self.etat == "menu":
                screen.blit(self.wallpaper, (0, 0))
                if self.game_started:
                    # main menu
                    if self.menu_state == "main":
                        if self.play_button.draw(screen):
                            self.menu_state = "play"
                        if self.settings_button.draw(screen):
                            self.menu_state = "settings"
                        if self.exit_button.draw(screen):
                            break

                    # settings menu
                    elif self.menu_state == "settings":
                        if self.video_button.draw(screen):
                            print("Video Settings")
                        if self.audio_button.draw(screen):
                            print("Audio Settings")
                        if self.keys_button.draw(screen):
                            print("Keys Settings")
                        if self.back_button.draw(screen):
                            self.menu_state = "main"

                    # play -> choose number of players
                    elif self.menu_state == "play":
                        self.draw_text_center("Select the number of players", self.font, self.TEXT_COL2, 50)
                        if self.one_player_button.draw(screen):
                            self.menu_state = "one_player"
                            self.number_players = 1
                        if self.two_players_button.draw(screen):
                            self.menu_state = "two_players"
                            self.number_players = 2
                        if self.three_players_button.draw(screen):
                            self.menu_state = "three_players"
                            self.number_players = 3
                        if self.four_players_button.draw(screen):
                            self.menu_state = "choice_characters"
                            self.number_players = 4
                        if self.back_button.draw(screen):
                            self.menu_state = "main"

                    # one player -> choose number of bots
                    elif self.menu_state == "one_player":
                        self.draw_text_center("Select the number of bots", self.font, self.TEXT_COL2, 50)
                        if self.zero_player_button.draw(screen):
                            self.menu_state = "choice_characters"
                            self.number_bot = 0
                        if self.one_player_button.draw(screen):
                            self.menu_state = "choice_characters"
                            self.number_bot = 1
                        if self.two_players_button.draw(screen):
                            self.menu_state = "choice_characters"
                            self.number_bot = 2
                        if self.three_players_button.draw(screen):
                            self.menu_state = "choice_characters"
                            self.number_bot = 3
                        if self.back_button.draw(screen):
                            self.menu_state = "play"

                    # two players -> choose number of bots (example)
                    elif self.menu_state == "two_players":
                        self.draw_text_center("Select the number of bots", self.font, self.TEXT_COL2, 50)
                        if self.zero_player_button.draw(screen):
                            self.menu_state = "choice_characters"
                            self.number_bot = 0
                        if self.one_player_button.draw(screen):
                            self.menu_state = "choice_characters"
                            self.number_bot = 1
                        if self.two_players_button.draw(screen):
                            self.menu_state = "choice_characters"
                            self.number_bot = 2
                        if self.back_button.draw(screen):
                            self.menu_state = "play"

                    # three_players / four_players can be handled similarly if needed
                    elif self.menu_state == "three_players":
                        self.draw_text_center("Select the number of bots", self.font, self.TEXT_COL2, 50)
                        if self.zero_player_button.draw(screen):
                            self.menu_state = "choice_characters"
                            self.number_bot = 0
                        if self.one_player_button.draw(screen):
                            self.menu_state = "choice_characters"
                            self.number_bot = 1
                        if self.back_button.draw(screen):
                            self.menu_state = "play"

                    elif self.menu_state == "choice_characters":
                        screen.blit(self.choice_chracters, (0, 0))
                        self.draw_text("Choose three characters", self.font, self.TEXT_COL, 50, 0)
                        if self.character_1_button.draw(screen):
                            self.character_1 = 1
                        if self.character_2_button.draw(screen):
                            self.character_1 = 2
                        if self.character_3_button.draw(screen):
                            self.character_1 = 3
                        if self.character_4_button.draw(screen):
                            self.character_1 = 4
                        if self.character_5_button.draw(screen):
                            self.character_1 = 5
                        if self.character_6_button.draw(screen):
                            self.character_1 = 6
                        if self.character_7_button.draw(screen):
                            self.character_1 = 7
                        if self.character_8_button.draw(screen):
                            self.character_1 = 8
                        if self.character_9_button.draw(screen):
                            self.character_1 = 9
                        if self.character_10_button.draw(screen):
                            self.character_1 = 10
                        if self.character_11_button.draw(screen):
                            self.character_1 = 11
                        if self.character_12_button.draw(screen):
                            self.character_1 = 12
                        if self.character_13_button.draw(screen):
                            self.character_1 = 13
                        if self.character_14_button.draw(screen):
                            self.character_1 = 14
                        if self.character_15_button.draw(screen):
                            self.character_1 = 15
                        if self.character_16_button.draw(screen):
                            self.character_1 = 16
                        if self.character_17_button.draw(screen):
                            self.character_1 = 17
                        if self.character_18_button.draw(screen):
                            self.character_1 = 18
                        if self.back_button.draw(screen):
                            self.menu_state = "play"

                else:
                    self.draw_text_center("Press Space to start", self.font, self.TEXT_COL, 250)

                # event handler
                for event in pyg.event.get():
                    if event.type == pyg.KEYDOWN:
                        if event.key == pyg.K_SPACE:
                            self.game_started = True
                    if event.type == pyg.QUIT:
                        self.running = False

                pyg.display.update()
            if self.etat == "game":
                player_position = self.player.get_status()['position']
                for event in pyg.event.get():
                    if event.type == pyg.QUIT:
                        self.running = False
                    elif event.type == pyg.KEYDOWN:
                        if event.key == pyg.K_ESCAPE:
                            self.running = False
                            self.send_to_server(message='ESC appuyé')
                        """elif event.key == pyg.K_e:
                            self.send_to_server(message='E appuyé')"""

                #chargement des assets dans le jeu
                self.screen.blit(self.map_back, (0, 0))
                

                t = self.clock.tick(60)
                event = pyg.key.get_pressed()

                if not( event[pyg.K_RIGHT] or event[pyg.K_LEFT] or event[pyg.K_UP] or event[pyg.K_DOWN] ):
                    tem_an_IDLE += t

                    if frame_walk_dir == 'right':
                            
                        if tem_an_IDLE >= 50:
                            tem_an_IDLE = 0
                            if frame_IDLE >= len(self.frames_IDLE) - 1:
                                frame_IDLE = 0
                            else :
                                frame_IDLE += 1

                        self.screen.blit(self.frames_IDLE[frame_IDLE], (self.x_temp, self.y_temp))
                    else:

                        if tem_an_IDLE >= 50:
                            tem_an_IDLE = 0
                            if frame_IDLE >= len(self.frame_IDLE_left) - 1:
                                frame_IDLE = 0
                            else :
                                frame_IDLE += 1
                        
                        self.screen.blit(self.frame_IDLE_left[frame_IDLE], (self.x_temp, self.y_temp))


                    
                else:

                    if event[pyg.K_RIGHT]:
                        self.send_to_server(message=f'DROITE appuyé, x actuel : {self.x_temp} , y actuel {self.y_temp}')
                        self.x_temp += self.vit_temp
                    if event[pyg.K_LEFT]:
                        self.send_to_server(message=f'GAUCHE appuyé, x actuel : {self.x_temp} , y actuel {self.y_temp}')
                        self.x_temp -= self.vit_temp
                    if event[pyg.K_UP]:
                        self.send_to_server(message=f'HAUT appuyé, x actuel : {self.x_temp} , y actuel {self.y_temp}')
                        self.y_temp -= self.vit_temp
                    if event[pyg.K_DOWN]:
                        self.send_to_server(message=f'BAS appuyé, x actuel : {self.x_temp} , y actuel {self.y_temp}')
                        self.y_temp += self.vit_temp

                    # Limiter la position après déplacement
                    self.x_temp = max(0, min(self.x_temp, self.width - self.frame_width))
                    self.y_temp = max(0, min(self.y_temp, self.height - self.frame_height))

                    tem_an_WALK += t

                    if tem_an_WALK >= 100:
                        tem_an_WALK = 0
                        if frame_WALK >= len(self.fram_WALK) - 1:
                            frame_WALK = 0
                        else :
                            frame_WALK += 1

                    if event[pyg.K_LEFT]:
                        frame_walk_dir = 'left'
                    elif event[pyg.K_RIGHT]:
                        frame_walk_dir = 'right'
                    if frame_walk_dir == 'left':
                        self.screen.blit(self.frame_WALK_left[frame_WALK], (self.x_temp, self.y_temp))
                    else:
                        self.screen.blit(self.fram_WALK[frame_WALK], (self.x_temp, self.y_temp))



                

                """
                font = pyg.font.SysFont(None, 24)
                txt = font.render('E pour envoyer un message au serveur. Esc pour quitter.', True, (255, 255, 255))
                self.screen.blit(txt, (20, 20)) """        

                pyg.display.update()
                pyg.display.flip()
                self.clock.tick(60)

        self.shutdown()


if __name__ == '__main__':
    # Démarrage du serveur local et du jeu
    game = Game(width=1280, height=720, fullscreen=True)
    game.run()
