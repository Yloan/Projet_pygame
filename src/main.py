import json
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


class Game:

    def __init__(self, width=1280, height=720, fullscreen=False):

        self.width = width
        self.height = height
        self.fullscreen = fullscreen
        self.etat = "menu"
        self.etat = "game"
        self.game_started = False
        self.dev_display_ = False
        self.delta_time_sessions_send = 0
        self.Menu = menu.Menu(
            width=self.width, height=self.height, fullscreen=self.fullscreen
        )

        try:
            # Reuse menu's pygame resources (screen, clock, font, colors)
            self.screen = self.Menu.screen
            self.wallpaper = self.Menu.wallpaper
            self.clock = self.Menu.clock
            try:
                self.font = self.Menu.font
                self.TEXT_COL = self.Menu.TEXT_COL
                self.TEXT_COL2 = self.Menu.TEXT_COL2
            except Exception:
                # Fallback to default values if menu doesn't expose them
                self.font = pyg.font.SysFont("arialblack", 40)
                self.TEXT_COL = (255, 255, 255)
                self.TEXT_COL2 = (255, 0, 0)
        except Exception:
            # Minimal fallback if Menu initialization fails
            flags = pyg.FULLSCREEN if self.fullscreen else 0
            self.screen = pyg.display.set_mode((self.width, self.height), flags)
            self.wallpaper = pyg.Surface((self.width, self.height))
            self.clock = pyg.time.Clock()

        # LOAD GAME MAP
        map_loader = MapLoader(None)
        background, foreground = map_loader.load_map()
        self.map_back = pyg.transform.scale(background, (self.width, self.height))
        self.map_front = pyg.transform.scale(foreground, (self.width, self.height))

        # LOAD PLAYER CHARACTER
        self.player = player_module.Water()
        self.running = False 

        # NETWORK CONFIGURATION
        # self.host = "127.0.0.1"
        # self.port = 12345

        # connexion online server
        self.host = "51.75.118.171"
        self.port = 20070

        self._client_socket = None
        self._client_lock = threading.Lock()
        self._send_queue = queue.Queue()

        # SESSION JOIN
        self.current_joined_session = None

    def draw_text(self, text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        self.screen.blit(img, (x, y))

    def draw_text_center(self, text, font, text_col, y):
        img = font.render(text, True, text_col)
        x = (self.width - img.get_width()) // 2
        self.screen.blit(img, (x, y))

    def center_x(self, image, scale=1):
        w = int(image.get_width() * scale)
        return (self.width - w) // 2

    def _connect_to_server(self):
        try:
            # Close existing socket if any
            if self._client_socket:
                try:
                    self._client_socket.close()
                except Exception:
                    pass

            # Create new socket connection
            self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._client_socket.settimeout(2.0)
            self._client_socket.connect((self.host, self.port))
            print_success(f"Connecté au serveur {self.host}:{self.port}")

            # Start background threads for message handling
            threading.Thread(target=self._receive_loop, daemon=True).start()
            threading.Thread(target=self._send_loop, daemon=True).start()

        except Exception as e:
            print_error(f"Erreur de connexion au serveur: {e}")
            self._client_socket = None

    def _receive_loop(self):
        while self.running:
            if not self._client_socket:
                time.sleep(0.5)
                continue
            try:
                data = self._client_socket.recv(1024)
                if not data:
                    print_warning("Connexion fermée par le serveur")
                    # Trigger reconnection
                    try:
                        self._client_socket.close()
                    except Exception:
                        pass
                    self._client_socket = None
                    if self.running:
                        time.sleep(1.0)
                        self._connect_to_server()
                    break
                message = data.decode("utf-8")
                print_network(f"Message reçu: {message}")

                # Handle session list updates from server
                if message.startswith("[SessionsList]:"):
                    try:
                        sessions_json = message.split(":", 1)[1]
                        self.Menu.update_sessions_from_server(sessions_json)
                    except Exception as e:
                        print_error(f"Erreur traitement sessions: {e}")

                # Broadcast sessions received from server to menu
                elif message.startswith("[Sessions]"):
                    try:
                        self.Menu.update_sessions_from_server(message.split(":", 1)[1])
                    except Exception as e:
                        print_error(f"Erreur mise à jour sessions: {e}")

                # À l'intérieur de ton _receive_loop, ajoute ce bloc :
                elif message.startswith("[YourPlayerID]:"):
                    try:
                        player_id = int(message.split(":", 1)[1])
                        self.Menu.my_player_id = player_id
                        print_success(f"Je suis le joueur {player_id} à l'écran !")
                    except Exception as e:
                        print_error(f"Erreur attribution Player ID: {e}")

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
        self._send_queue.put(message)

    # GAME STATE MANAGEMENT

    def shutdown(self):

        print_info("Arrêt du jeu : fermeture connexion et threads")
        self.running = False

        # Close client socket safely
        with self._client_lock:
            try:
                if self._client_socket:
                    self._client_socket.shutdown(socket.SHUT_RDWR)
                    self._client_socket.close()
            except Exception:
                pass
            self._client_socket = None

        # Clear message queue
        try:
            while not self._send_queue.empty():
                self._send_queue.get_nowait()
        except Exception:
            pass

        # Quit pygame
        try:
            pyg.quit()
        except Exception:
            pass

    # GAME UPDATE AND RENDERING

    def update(self):
        self.player.update()

    # Some dev display
    def dev_display(self, liste_image=None):
        x, y = pyg.mouse.get_pos()
        self.draw_text_center(
            f"pos mouse --> X: {x}, Y: {y}", self.font, self.TEXT_COL2, 10
        )


    # MAIN GAME LOOP

    def run(self):

        # Initialize and connect to server
        self.running = True
        self._connect_to_server()

        screen = self.screen

        # Temporary variables (for tests)

        self.etat = "menu"  # Start directly in menu
        # self.etat = "game"  # Start directly in game

        while self.running:
            # MENU STATE
            if self.etat == "menu":
                screen.blit(self.wallpaper, (0, 0))

                self.Menu.method_menu()
                if self.Menu.etat == "game":
                    self.etat = "game"
                if self.Menu.menu_state == "creation_parameters_session_menu":
                    for event in pyg.event.get():
                        self.Menu.input_box.handle_event(event)

                # Handle menu events
                for event in pyg.event.get():
                    if event.type == pyg.QUIT:
                        self.running = False
                    elif event.type == pyg.KEYDOWN:
                        if event.key == pyg.K_ESCAPE:
                            self.running = False
                        if event.key == pyg.K_F2:
                            self.dev_display_ = not self.dev_display_
                    elif event.type == pyg.MOUSEBUTTONDOWN:
                        if event.button == 4:  # MOUSE UP
                            self.Menu.scroll_y = max(0, self.Menu.scroll_y - 30)
                        if event.button == 5:  # MOUSE down
                            self.Menu.scroll_y += 30

                    if self.Menu.menu_state == "creation_parameters_session_menu":
                        self.Menu.input_box.handle_event(
                            event
                        )

            self.delta_time_sessions_send += 1
            # Send sessions to server
            if self.Menu.pending_session is not None:
                self.send_to_server(
                    f"[CreateSession]:{json.dumps(self.Menu.pending_session)}"
                )
                self.current_joined_session = self.Menu.pending_session["titre"]

                self.send_to_server(f"[JoinedSession]:{self.current_joined_session}")

                self.Menu.pending_session = None  # On vide après envoi

            # GAME STATE - Actual gameplay
            if self.etat == "game":
                # Event handling
                for event in pyg.event.get():
                    if event.type == pyg.QUIT:
                        self.running = False
                    elif event.type == pyg.KEYDOWN:
                        if event.key == pyg.K_ESCAPE:
                            self.running = False
                            self.send_to_server(message="ESC appuyé")
                        if event.key == pyg.K_F2:
                            self.dev_display_ = not self.dev_display_

                # Draw game background
                self.screen.blit(self.map_back, (0, 0))

                # Get frame time
                delta_time = self.clock.tick(60)

                # Get current key presses
                keys_pressed = pyg.key.get_pressed()

                # Check if any movement key is active
                is_moving = (
                    keys_pressed[pyg.K_RIGHT]
                    or keys_pressed[pyg.K_LEFT]
                    or keys_pressed[pyg.K_UP]
                    or keys_pressed[pyg.K_DOWN]
                )

                if keys_pressed[pyg.K_q] and not self.player.is_attacking_skill1:
                    self.player.is_attacking_skill1 = True
                    self.player.frame_character_skill1 = 0

                if keys_pressed[pyg.K_s] and not self.player.is_attacking_skill2:
                    self.player.is_attacking_skill2 = True
                    self.player.frame_character_skill2 = 0

                if keys_pressed[pyg.K_d] and not self.player.is_attacking_skill3:
                    self.player.is_attacking_skill3 = True
                    self.player.frame_character_skill3 = 0

                # Handle player movement
                if keys_pressed[pyg.K_UP]:
                    self.player.move("up")
                if keys_pressed[pyg.K_DOWN]:
                    self.player.move("down")
                if keys_pressed[pyg.K_LEFT]:
                    self.player.move("left")
                if keys_pressed[pyg.K_RIGHT]:
                    self.player.move("right")

                self.player.update_animation(
                    delta_time,
                    is_moving,
                    self.player.is_attacking_skill1,
                    self.player.is_attacking_skill2,
                    self.player.is_attacking_skill3,
                )

                # Get and draw current player sprite
                current_sprite = self.player.get_current_sprite()
                player_pos = self.player.position
                self.screen.blit(current_sprite, player_pos)

                # Draw foreground on top of player
                self.screen.blit(self.map_front, (0, 0))

                # Send player position to server
                self.send_to_server(
                    message=f"Position du joueur : x={player_pos[0]}, y={player_pos[1]}"
                )

            if self.dev_display_:
                try:
                    self.dev_display()
                except Exception as e:
                    print(f"Error dev display| Error --> {e}")

            # Update display
            pyg.display.update()
            pyg.display.flip()

        # Graceful shutdown
        self.shutdown()


if __name__ == "__main__":
    # Initialize and run game with fullscreen enabled
    game = Game(width=1280, height=720, fullscreen=True)
    game.run()
