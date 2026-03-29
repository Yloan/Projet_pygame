import json
import queue
import random
import socket
import threading
import time

import pygame as pyg

import game.characters as player_module
import ui.menu as menu
import ui.Music as music_module
import utils.paths as __path__
from game.map_laoder import MapLoader
from ui.console import (
    print_error,
    print_info,
    print_network,
    print_success,
    print_warning,
)

MESSAGE_DELIMITER = "\n"


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

        # LOAD PLAYER CHARACTER
        self.player = player_module.Water()
        self.running = False

        # NETWORK CONFIGURATION
        # self.host = "127.0.0.1"
        # self.port = 12345

        # connexion online server
        self.host = "51.75.118.75"
        self.port = 20140

        self._client_socket = None
        self._client_lock = threading.Lock()
        self._send_queue = queue.Queue()
        self._recv_queue = queue.Queue()
        self.recv_buffer = ""

        self.recv_buffer = ""

        # SESSION JOIN
        self.current_joined_session = None
        self.position = self.Menu.slot_positions[1]

        # Map selection
        self.choose_map = False
        self.map_choosen = None
        self.bot_choose = False

        # MUSIC
        self.current_music = 0
        self.musics = []

        self.musics_names = ["Slower_blitzkrieg.mp3"]

        for music_file in self.musics_names:
            chemin_complet = __path__.ensure_asset_exists("musics", music_file)
            music = music_module.MusicPlayer(chemin_complet)
            self.musics.append(music)

    def switch_music(self, i=None):
        if i is not None:
            self.current_music = i

        else:
            self.current_music += 1

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

    def _process_network_messages(self):
        while not self._recv_queue.empty():
            message = self._recv_queue.get_nowait()

            if message.startswith("[SessionsList]:"):
                try:
                    self.Menu.update_sessions_from_server(message.split(":", 1)[1])
                except Exception as e:
                    print_error(f"Erreur traitement sessions: {e}")

            elif message.startswith("[YourPlayerID]:"):
                try:
                    player_id = int(message.split(":", 1)[1])
                    self.Menu.my_player_id = player_id
                    print_success(f"Je suis le joueur {player_id}")
                    if self.Menu.menu_state == "waiting_player_id":
                        self.Menu.menu_state = "character_selection_final"

                except Exception as e:
                    print_error(f"Erreur player ID: {e}")

            elif message.startswith("[CharacterUpdate]:"):
                try:
                    data = json.loads(message.split(":", 1)[1])
                    self.Menu.update_player_character(
                        data["player_id"],
                        data["character_1"],
                        data["character_2"],
                        data["character_3"],
                    )
                except Exception as e:
                    print_error(f"Erreur CharacterUpdate: {e}")

            elif message.startswith("[PlayerReady]:"):
                try:
                    data = json.loads(message.split(":", 1)[1])
                    self.Menu.update_player_ready(data["player_id"])
                except Exception as e:
                    print_error(f"Erreur PlayerReady: {e}")

            elif message.startswith("[PlayerUnready]:"):
                try:
                    player_id = int(message.split(":", 1)[1])
                    self.Menu.players_ready[player_id] = False
                except Exception as e:
                    print_error(f"Erreur PlayerUnready: {e}")

            elif message.startswith("[PlayerLeft]:"):
                try:
                    player_id = int(message.split(":", 1)[1])
                    self.Menu.players_characters[player_id] = [None, None, None]
                    self.Menu.players_ready[player_id] = False
                except Exception as e:
                    print_error(f"Erreur PlayerLeft: {e}")

            elif message.startswith("[MapVotesUpdate]:"):
                try:
                    votes = json.loads(message.split(":", 1)[1])
                    self.Menu.update_map_votes(votes)
                except Exception as e:
                    print_error(f"Erreur MapVotesUpdate: {e}")

            elif message.startswith("[StartGame]:"):
                self.Menu.map_player_votes = {}
                self.choose_map = False
                self.map_choosen = None
                try:
                    map = int(message.split(":")[1])
                    # LOAD GAME MAP
                    map_loader = MapLoader(None, map)
                    background, foreground = map_loader.load_map()
                    self.map_back = pyg.transform.scale(
                        background, (self.width, self.height)
                    )
                    self.map_front = pyg.transform.scale(
                        foreground, (self.width, self.height)
                    )
                    self.etat = "game"
                except Exception as e:
                    print_error(f"Error Starting game: {e}")

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
                chunk = self._client_socket.recv(4096).decode("utf-8")
                self.recv_buffer += chunk
                messages = self.recv_buffer.split("\n")
                self.recv_buffer = messages[-1]

                for message in messages[:-1]:
                    if not message:
                        continue
                    print_network(f"Message reçu: {message}")
                    self._recv_queue.put(message)

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
                    self._client_socket.send(
                        (message + MESSAGE_DELIMITER).encode("utf-8")
                    )
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

        if self.current_joined_session and self._client_socket:
            try:
                self._client_socket.send(
                    f"[LeaveSession]:{self.current_joined_session}\n".encode("utf-8")
                )
            except Exception:
                pass

            if self.choose_map:
                try:
                    self.send_to_server(message=f"[UnchooseMap]:{self.map_choosen}")
                except Exception as e:
                    print_error(f"Error shutdown : {e}")
            self.current_joined_session = None

        self.running = False

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

        # Init game's musics
        pyg.mixer.init()
        self.musics[self.current_music].play()

        while self.running:
            # Launch music

            self._process_network_messages()
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
                        if self.current_joined_session:
                            self.send_to_server(
                                f"[LeaveSession]:{self.current_joined_session}"
                            )
                            self.current_joined_session = None
                        self.running = False
                    elif event.type == pyg.KEYDOWN:
                        if event.key == pyg.K_ESCAPE:
                            if self.current_joined_session:
                                self.send_to_server(
                                    f"[LeaveSession]:{self.current_joined_session}"
                                )
                                self.current_joined_session = None
                            self.running = False
                        if event.key == pyg.K_F2:
                            self.dev_display_ = not self.dev_display_
                    elif event.type == pyg.MOUSEBUTTONDOWN:
                        if event.button == 4:  # MOUSE UP
                            self.Menu.scroll_y = max(0, self.Menu.scroll_y - 30)
                        if event.button == 5:  # MOUSE down
                            self.Menu.scroll_y += 30

                        if self.Menu.menu_state == "maps_selection":
                            if event.button == 1:
                                if self.choose_map:
                                    self.send_to_server(
                                        message=f"[UnchooseMap]:{self.map_choosen}"
                                    )
                                    self.Menu.map_player_votes.pop(self.Menu.my_player_id, None)

                                for (
                                    num_map,
                                    slot_map,
                                ) in self.Menu.rects_img_maps.items():
                                    if slot_map.collidepoint(event.pos):
                                        self.send_to_server(
                                            message=f"[ChooseMap]:{num_map}"
                                        )
                                        print_info(f"Clique on map number : {num_map}")
                                        self.Menu.map_player_votes[self.Menu.my_player_id] = num_map
                                        self.map_choosen = num_map
                                        self.choose_map = True
                                        break

                    if self.Menu.menu_state == "creation_parameters_session_menu":
                        self.Menu.input_box.handle_event(event)

            self.delta_time_sessions_send += 1
            # Send sessions to server

            # if self.Menu.menu_state == "maps_selection":
            #     nbots = self.Menu.number_bot
            #     for i in range(nbots):
            #         self.send_to_server(
            #             message=f"[BotChooseMap]:{random.randint(1, 6)}"
            #         )

            if self.Menu.pending_session is not None:
                self.send_to_server(
                    f"[CreateSession]:{json.dumps(self.Menu.pending_session)}"
                )
                self.current_joined_session = self.Menu.pending_session["titre"]
                # self.send_to_server(f"[JoinedSession]:{self.current_joined_session}")
                self.Menu.pending_session = None

                # self.Menu.menu_state = "waiting_player_id"

            if (
                hasattr(self.Menu, "pending_join_session")
                and self.Menu.pending_join_session is not None
            ):
                self.current_joined_session = self.Menu.pending_join_session
                self.send_to_server(f"[JoinedSession]:{self.current_joined_session}")
                self.Menu.pending_join_session = None

            if self.Menu.pending_character_update:
                update_data = {
                    "player_id": self.Menu.my_player_id,
                    "character_1": self.Menu.character_1,
                    "character_2": self.Menu.character_2,
                    "character_3": self.Menu.character_3,
                    "session_name": self.Menu.current_session_name,
                }
                self.send_to_server(f"[CharacterUpdate]:{json.dumps(update_data)}")
                self.Menu.pending_character_update = False

            if (
                hasattr(self.Menu, "pending_character_submission")
                and self.Menu.pending_character_submission is not None
            ):
                self.send_to_server(
                    f"[PlayerReady]:{json.dumps(self.Menu.pending_character_submission)}"
                )
                self.Menu.pending_character_submission = None

            if self.Menu.pending_leave_session is not None:
                self.send_to_server(f"[LeaveSession]:{self.Menu.pending_leave_session}")
                self.Menu.pending_leave_session = None

            if self.Menu.pending_unready:
                self.send_to_server(f"[PlayerUnready]:{self.Menu.my_player_id}")
                self.Menu.pending_unready = False

            # GAME STATE - Actual gameplay
            if self.etat == "game":
                self.Menu.menu_state = "main"
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
