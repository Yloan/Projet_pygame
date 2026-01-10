# Point d'entrée du jeu : boucle principale et envoi d'informations au serveur

import os
import queue
import socket
import threading
import time

import pygame as pyg

import game.characters as player_module
import ui.menu as menu
from game.map_laoder import MapLoader
from ui.console import (
    print_error,
    print_info,
    print_network,
    print_success,
    print_warning,
)
from ui.server import Serveur


class Game:
    def __init__(self, width=1280, height=720, fullscreen=False):
        # Configuration de la fenêtre
        self.width = width
        self.height = height
        self.fullscreen = fullscreen

        # This are temporary variables for player
        self.player = player_module.Furnace()
        # état courant (menu / game)
        self.etat = "menu"
        # indicateur que l'utilisateur a lancé le menu (appuie sur espace)
        self.game_started = False

        # objet menu (réutilise la configuration d'affichage souhaitée)
        self.Menu = menu.Menu(width=self.width, height=self.height, fullscreen=self.fullscreen)
        # réutiliser l'affichage et les ressources initialisées par le menu
        try:
            self.screen = self.Menu.screen
            self.wallpaper = self.Menu.wallpaper
            self.clock = self.Menu.clock
            # reprendre police et couleurs du menu
            try:
                self.font = self.Menu.font
                self.TEXT_COL = self.Menu.TEXT_COL
                self.TEXT_COL2 = self.Menu.TEXT_COL2
            except Exception:
                # valeurs par défaut
                self.font = pyg.font.SysFont("arialblack", 40)
                self.TEXT_COL = (255, 255, 255)
                self.TEXT_COL2 = (255, 0, 0)
        except Exception:
            # fallback minimal si le Menu n'expose pas ces attributs
            flags = pyg.FULLSCREEN if self.fullscreen else 0
            self.screen = pyg.display.set_mode((self.width, self.height), flags)
            self.wallpaper = pyg.Surface((self.width, self.height))
            self.clock = pyg.time.Clock()

        # loader de map (résout correctement les chemins)
        map_loader = MapLoader(None)
        background, foreground = map_loader.load_map()
        self.map_back = pyg.transform.scale(background, (self.width, self.height))
        self.map_front = foreground

        # chargement des sprites du joueur (classe Furnace dans game/characters)
        self.player = player_module.Furnace()
        self.running = False

        # Configuration réseau
        self.host = "127.0.0.1"
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
                    print_warning("Connexion fermée par le serveur")
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
                    self._client_socket.send(message.encode("utf-8"))
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

    def send_to_server(self, message="Bonjour serveur"):
        """Ajoute un message à la file d'envoi."""
        self._send_queue.put(message)

    def shutdown(self):
        """Arrête proprement la logique réseau et ferme Pygame."""
        print_info("Arrêt du jeu : fermeture connexion et threads")
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

    # methode pour l'update du player
    def update(self):
        event = pyg.key.get_pressed()

        if event[pyg.K_RIGHT]:
            self.player.move("right")
        if event[pyg.K_LEFT]:
            self.player.move("left")
        if event[pyg.K_UP]:
            self.player.move("up")
        if event[pyg.K_DOWN]:
            self.player.move("down")

    def run(self):
        # Démarrer le jeu et établir la connexion réseau
        self.running = True

        # variables for the animations and the direction
        frame_IDLE = 0
        frame_WALK = 0
        tem_an_IDLE = 0
        tem_an_WALK = 0
        frame_walk_dir = "right"

        # environnement variables
        player_pos = self.player.get_status()["position"]

        # connexion server
        self._connect_to_server()

        screen = self.screen
        while self.running:
            if self.etat == "menu":
                screen.blit(self.wallpaper, (0, 0))
                if self.game_started:
                    # main menu
                    self.Menu.method_menu()
                else:
                    # afficher l'invite de démarrage avant que le menu ne soit ouvert
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
                for event in pyg.event.get():
                    if event.type == pyg.QUIT:
                        self.running = False
                    elif event.type == pyg.KEYDOWN:
                        if event.key == pyg.K_ESCAPE:
                            self.running = False
                            self.send_to_server(message="ESC appuyé")

                # chargement des assets dans le jeu
                self.screen.blit(self.map_back, (0, 0))

                # connexion au serveur et envoi des données
                self.send_to_server(
                    message=f"Position du joueur : x={player_pos[0]}, y={player_pos[1]}"
                )

                t = self.clock.tick(60)
                event = pyg.key.get_pressed()

                if not (
                    event[pyg.K_RIGHT]
                    or event[pyg.K_LEFT]
                    or event[pyg.K_UP]
                    or event[pyg.K_DOWN]
                ):
                    tem_an_IDLE += t

                    if frame_walk_dir == "right":
                        if tem_an_IDLE >= 50:
                            tem_an_IDLE = 0
                            if frame_IDLE >= len(self.frames_IDLE) - 1:
                                frame_IDLE = 0
                            else:
                                frame_IDLE += 1

                        self.screen.blit(
                            self.frames_IDLE[frame_IDLE],
                            (
                                player_pos[0],
                                player_pos[1],
                            ),
                        )
                    else:
                        if tem_an_IDLE >= 50:
                            tem_an_IDLE = 0
                            if frame_IDLE >= len(self.frame_IDLE_left) - 1:
                                frame_IDLE = 0
                            else:
                                frame_IDLE += 1

                        self.screen.blit(
                            self.frame_IDLE_left[frame_IDLE],
                            (
                                player_pos[0],
                                player_pos[1],
                            ),
                        )

                else:
                    self.update()

                    tem_an_WALK += t

                    if tem_an_WALK >= 100:
                        tem_an_WALK = 0
                        if frame_WALK >= len(self.fram_WALK) - 1:
                            frame_WALK = 0
                        else:
                            frame_WALK += 1

                    if event[pyg.K_LEFT]:
                        frame_walk_dir = "left"
                    elif event[pyg.K_RIGHT]:
                        frame_walk_dir = "right"
                    if frame_walk_dir == "left":
                        self.screen.blit(
                            self.frame_WALK_left[frame_WALK],
                            (
                                player_pos[0],
                                player_pos[1],
                            ),
                        )
                    else:
                        self.screen.blit(
                            self.fram_WALK[frame_WALK],
                            (
                                player_pos[0],
                                player_pos[1],
                            ),
                        )

                pyg.display.update()
                pyg.display.flip()
                self.clock.tick(60)

        self.shutdown()


if __name__ == "__main__":
    # Démarrage du serveur local et du jeu
    game = Game(width=1280, height=720, fullscreen=True)
    game.run()
