import json
import queue
import socket
import threading
import time

import pygame as pyg

import game.characters as player_module
import ui.menu as menu
import ui.Music as music_module
import utils.paths as __path__
from game.characters import (
    FRAME_SIZE,
    PROJECTILES_INFOS,
    Character,
    Projectile,
    make_character,
)
from game.map_laoder import MapLoader
from ui.console import (
    print_debug,
    print_error,
    print_info,
    print_network,
    print_success,
    print_warning,
)
from ui.HUD import HUD

# Gloabl variables
MESSAGE_DELIMITER = "\n"
HUD_POSITIONS = {1: (10, 10), 2: (993, 10), 3: (10, 530), 4: (993, 530)}

TIME_BEFORE_PROJECTILE = {1: {"s1": 4, "s2": 4}, 5: {"s1": 4}}

# This will be changed when we will implement the other map (spawn slot by map)
SPAWN_POSITIONS = {
    1: (150, 320),
    2: (1050, 320),
    3: (150, 320),
    4: (1050, 320),
}

SKILL_COOLDOWNS = {
    # duree in secs
    1: {"S1": 2, "S2": 4, "S3": 7},
    2: {"S1": 2, "S2": 4, "S3": 8},
    3: {"S1": 2, "S2": 4, "S3": 7},
    4: {"S1": 1.5, "S2": 5, "S3": 8},
    5: {"S1": 2, "S2": 4, "S3": 6},
}
RETREAT_COOLDOWN_DURATION = 4  # secs aussi


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
            # Reuse menu's pygame resources
            self.screen = self.Menu.screen
            self.wallpaper = self.Menu.wallpaper
            self.clock = self.Menu.c
            try:
                self.font = self.Menu.font
                self.TEXT_COL = self.Menu.TEXT_COL
                self.TEXT_COL2 = self.Menu.TEXT_COL2
            except Exception:
                # Default values if menu doesn't expose them
                self.font = pyg.font.SysFont("arialblack", 40)
                self.TEXT_COL = (255, 255, 255)
                self.TEXT_COL2 = (255, 0, 0)
        except Exception:
            # Minimal if Menu initialization fails
            flags = pyg.FULLSCREEN if self.fullscreen else 0
            self.screen = pyg.display.set_mode((self.width, self.height), flags)
            self.wallpaper = pyg.Surface((self.width, self.height))
            self.clock = pyg.time.Clock()

        # LOAD GAME MAP
        map_loader = MapLoader(None)
        background, foreground = map_loader.load_map()
        self.map_back = pyg.transform.scale(background, (self.width, self.height))
        self.map_front = pyg.transform.scale(foreground, (self.width, self.height))

        self.active_char = None
        self.support_1 = None
        self.support_2 = None
        self.player = None
        self._game_initialized = False
        self._retreat_cooldown = 0
        self.running = False

        # NETWORK CONFIGURATION
        # self.host = "127.0.0.1"
        # self.port = 12345

        # connexion online server
        self.host = "51.75.118.17"
        self.port = 20041

        self._client_socket = None
        self._client_lock = threading.Lock()
        self._send_queue = queue.Queue()
        self._r_queue = queue.Queue()
        self.r_buffer = ""

        # SESSION JOIN
        self.current_joined_session = None
        self.position = self.Menu.slot_positions[1]

        # MUSIC
        self.current_music = 0
        self.musics = []

        self.musics_names = ["Slower_blitzkrieg.mp3"]

        for music_file in self.musics_names:
            chemin_complet = __path__.ensure_asset_exists("musics", music_file)
            music = music_module.MusicPlayer(chemin_complet)
            self.musics.append(music)

        # Variables HUD
        self.other_huds = {}
        self.hud = None

        self.remote_players = {}

        self.delta_time_entity_send = 0
        self.SENT_INTERVAL = 2

        self._char6_wtr_frames = None
        self._char6_soda_frames = None
        self._char6_cans_loaded = False

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

    def _all_players_ready(self):
        session_info = next(
            (s for s in self.Menu.sessions if s.titre == self.current_joined_session),
            None,
        )
        if not session_info:
            return False
        max_humans = 4 - session_info.nb_bots
        if session_info.nb_players < max_humans:
            return False
        ready_count = sum(1 for v in self.Menu.players_ready.values() if v)
        return ready_count >= max_humans

    def _process_network_messages(self):
        while not self._r_queue.empty():
            message = self._r_queue.get_nowait()

            if message.startswith("[SessionsList]:"):
                try:
                    self.Menu.update_sessions_from_server(message.split(":", 1)[1])
                except Exception as e:
                    print_error(f"Erreur traitement sessions: {e}")

            elif message.startswith("[YourPlayerID]:"):
                try:
                    player_id = int(message.split(":", 1)[1])
                    self.Menu.CurrentPlayer_id = player_id
                    self.hud = HUD(player_id)
                    # print_success(f"Je suis le joueur {player_id}")
                    if self.Menu.menu_state == "waiting_player_id":
                        self.Menu.menu_state = "character_selection_final"

                    session_info = next(
                        (
                            s
                            for s in self.Menu.sessions
                            if s.titre == self.current_joined_session
                        ),
                        None,
                    )
                    if session_info:
                        nb_bots = session_info.nb_bots
                        for i in range(nb_bots):
                            bot_id = 4 - i
                            self.other_huds[bot_id] = HUD(bot_id)

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
                    print_debug(f"Player ready recu: {message}")
                    data = json.loads(message.split(":", 1)[1])
                    self.Menu.update_player_ready(data["player_id"])
                    if self._all_players_ready():
                        self.game_started = True
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

            elif message.startswith("[HUDUpdate]:"):
                data = json.loads(message.split(":", 1)[1])
                pid = data["player_id"]
                if pid != self.Menu.CurrentPlayer_id:
                    if pid not in self.other_huds:
                        self.other_huds[pid] = HUD(pid)
                    self.other_huds[pid].updateFromServer(data["hud"])

            elif message.startswith("[GameState]:"):
                try:
                    payload = json.loads(message.split(":", 1)[1])
                    entities = payload.get("entities", {})
                    my_id = self.Menu.CurrentPlayer_id

                    for pid_str, state in entities.items():
                        pid = int(pid_str)
                        if pid == my_id:
                            continue

                        char_num = state.get("char_number", 1)
                        if pid not in self.remote_players:
                            try:
                                self.remote_players[pid] = make_character(char_num)
                            except Exception as e:
                                print_error(
                                    f"Impossible de créer remote Character-{char_num}: {e}"
                                )
                                continue

                        elif self.remote_players[pid].char_num != char_num:
                            old_pos = list(self.remote_players[pid].position)
                            try:
                                self.remote_players[pid] = make_character(char_num)
                                self.remote_players[pid].position = old_pos
                            except Exception as e:
                                print_error(
                                    f"Impossible de recréer remote Character-{char_num}: {e}"
                                )
                                continue

                        self.remote_players[pid].apply_network_state(state)

                except Exception as e:
                    print_error(f"Erreur GameState: {e}")

            elif message.startswith("[ProjectileSpawned]:"):
                try:
                    data = json.loads(message.split(":", 1)[1])
                    pid = data["player_id"]
                    if pid == self.Menu.CurrentPlayer_id:
                        continue
                    if pid not in self.remote_players:
                        continue

                    char_num = data["char_num"]
                    skill_num = data["skill_num"]
                    direction = data["direction"]
                    pos = (data["x"], data["y"])

                    proj_data = PROJECTILES_INFOS.get(char_num, {}).get(f"s{skill_num}")
                    if proj_data:
                        self.remote_players[pid].projectiles.append(
                            Projectile(char_num, skill_num, pos, direction, proj_data)
                        )
                except Exception as e:
                    print_error(f"Erreur ProjectileSpawned: {e}")

    def _connect_to_server(self):
        try:
            if self._client_socket:
                try:
                    self._client_socket.close()
                except Exception:
                    pass

            self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._client_socket.settimeout(2)
            self._client_socket.connect((self.host, self.port))

            threading.Thread(target=self._receive_loop, daemon=True).start()
            threading.Thread(target=self._send_loop, daemon=True).start()

        except Exception as e:
            print_error(f"Erreur de connexion au serveur: {e}")
            self._client_socket = None

    def _reconnect_socket(self):
        with self._client_lock:
            if self._client_socket:
                try:
                    self._client_socket.close()
                except Exception:
                    pass
            self._client_socket = None

        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)

                sock.connect((self.host, self.port))
                with self._client_lock:
                    self._client_socket = sock
                return
            except Exception as e:
                print_error(f"Erreur de connexion au serveur: {e}")
                time.sleep(1)

    def _receive_loop(self):
        while self.running:
            if not self._client_socket:
                time.sleep(0.5)
                continue
            try:
                chunk = self._client_socket.recv(4096).decode("utf-8")
                self.r_buffer += chunk
                messages = self.r_buffer.split("\n")
                self.r_buffer = messages[-1]
                for message in messages[:-1]:
                    if message:
                        self._r_queue.put(message)
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
                    self._reconnect_socket()

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
                    time.sleep(0.1)
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

    def shutdown(self):
        print_info("Arrêt du jeu : fermeture connexion et threads")
        self.running = False

        if self.current_joined_session:
            try:
                if self._client_socket:
                    self._client_socket.send(
                        f"[LeaveSession]:{self.current_joined_session}\n".encode(
                            "utf-8"
                        )
                    )
            except Exception:
                pass
            self.current_joined_session = None

        with self._client_lock:
            if self._client_socket:
                try:
                    self._client_socket.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                try:
                    self._client_socket.close()
                except Exception:
                    pass
            self._client_socket = None

        while not self._send_queue.empty():
            try:
                self._send_queue.get_nowait()
            except Exception:
                break

        try:
            pyg.quit()
        except Exception:
            pass

    def _load_char6_hud(self):
        try:
            import pygame as pyg

            sheet_wtr = pyg.image.load(
                "assets/sprites/Character-5/HUD-SPEC-6-WTR-Sheet.png"
            ).convert_alpha()
            frame_w = sheet_wtr.get_width() // 4
            frame_h = sheet_wtr.get_height()
            self._char6_wtr_frames = [
                sheet_wtr.subsurface((i * frame_w, 0, frame_w, frame_h))
                for i in range(4)
            ]
            self._char6_soda_frames = self._char6_wtr_frames
            self._char6_cans_loaded = True
        except Exception as e:
            print_error(f"Erreur chargement HUD char6: {e}")

    def _draw_char6_hud(self, surface, player_id, water_cans=4, soda_cans=4):
        if not self._char6_cans_loaded or not self._char6_wtr_frames:
            return

        pos = CHAR6_CANS_HUD_POSITIONS.get(player_id)
        if not pos:
            return

        x, y = pos
        frame = self._char6_wtr_frames[0]
        fw = frame.get_width()
        fh = frame.get_height()
        gap = 4

        for i in range(4):
            alpha = 255 if i < water_cans else 80
            f = frame.copy()
            f.set_alpha(alpha)
            surface.blit(f, (x + i * (fw + gap), y))

        if self._char6_soda_frames:
            sf = self._char6_soda_frames[0]
            for i in range(4):
                alpha = 255 if i < soda_cans else 80
                f = sf.copy()
                f.set_alpha(alpha)
                surface.blit(f, (x + i * (fw + gap), y + CHAR6_CANS_GAP))

    def _init_game_characters(self):
        c1 = self.Menu.character_1 or 1
        c2 = self.Menu.character_2 or 1
        c3 = self.Menu.character_3 or 1

        if c1 == 6 or c2 == 6 or c3 == 6:
            self._load_char6_hud()

        spawn = list(SPAWN_POSITIONS.get(self.Menu.CurrentPlayer_id, (150, 320)))

        self.active_char = player_module.make_character(c1)
        self.support_1 = player_module.make_character(c2)
        self.support_2 = player_module.make_character(c3)

        self.active_char.position = spawn[:]
        self.support_1.position = spawn[:]
        self.support_2.position = spawn[:]

        self._last_char_health = self.active_char.health

        self.player = self.active_char
        print_success(
            f"Jeu lancé | actif: perso {c1} | "
            f"support 1: perso {c2} | support 2: perso {c3}"
        )

    # GAME UPDATE AND RENDERING

    def update(self):
        if self.active_char:
            self.active_char.update()

    def send_to_server(self, message="Bonjour serveur"):
        self._send_queue.put(message)

    # Some dev display
    def dev_display(self, liste_image=None):
        x, y = pyg.mouse.get_pos()
        self.draw_text_center(
            f"pos mouse --> X: {x}, Y: {y}", self.font, self.TEXT_COL2, 10
        )
        Character.switch_TMP__GET_SURFACE_HITBOX_ATTACKS_()

    def _broadcast_hud_state(self):
        if not hasattr(self, "hud") or self.hud is None:
            return
        payload = {
            "player_id": self.Menu.CurrentPlayer_id,
            "hud": self.hud.toNetworkData(),
        }
        self.send_to_server(f"[HUDUpdate]:{json.dumps(payload)}")

    # MAIN GAME LOOP

    def _send_skill(self, skill_num):
        skill_key = f"S{skill_num}"

        if self.hud and not self.hud.isSkillReady(skill_key):
            return

        if not self.active_char.use_skill(skill_num):
            return

        if self.hud:
            duration = SKILL_COOLDOWNS.get(self.active_char.char_num, {}).get(
                skill_key, 3.0
            )
            self.hud.startCooldown(skill_key, duration)

        base = {
            "player_id": self.Menu.CurrentPlayer_id,
            "session": self.current_joined_session,
            "char_num": self.active_char.char_num,
            "skill_num": skill_num,
            "x": self.active_char.position[0],
            "y": self.active_char.position[1],
            "direction": self.active_char.direction,
        }
        self.send_to_server(f"[SkillUsed]:{json.dumps(base)}")

        if PROJECTILES_INFOS.get(self.active_char.char_num, {}).get(f"s{skill_num}"):
            self.send_to_server(f"[ProjectileSpawned]:{json.dumps(base)}")

    def run(self):

        # Initialize and connect to server
        self.running = True
        self._connect_to_server()

        screen = self.screen

        self.etat = "menu"
        # self.etat = "game"

        # When starting directly in game initialise characters with defaults
        if self.etat == "game" and not self._game_initialized:
            self.Menu.character_1 = self.Menu.character_1 or 2
            self.Menu.character_2 = self.Menu.character_2 or 1
            self.Menu.character_3 = self.Menu.character_3 or 2
            self._init_game_characters()
            self._game_initialized = True

        pyg.mixer.init()
        self.musics[self.current_music].play()
        self.musics[self.current_music].volume(0.01)
        while self.running:
            # Launch music

            self._process_network_messages()
            # MENU STATE
            if self.etat == "menu":
                screen.blit(self.wallpaper, (0, 0))

                self.Menu.method_menu()
                if self.game_started and not self._game_initialized:
                    self._init_game_characters()
                    self._game_initialized = True
                    self.etat = "game"
                    self.Menu.etat = "game"
                elif self.game_started:
                    self.etat = "game"
                    self.Menu.etat = "game"

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

                    if self.Menu.menu_state == "creation_parameters_session_menu":
                        self.Menu.input_box.handle_event(event)

            self.delta_time_sessions_send += 1
            # Send sessions to server

            if self.Menu.sessionPending is not None:
                self.send_to_server(
                    f"[CreateSession]:{json.dumps(self.Menu.sessionPending)}"
                )
                self.current_joined_session = self.Menu.sessionPending["titre"]
                # self.send_to_server(f"[JoinedSession]:{self.current_joined_session}")
                self.Menu.sessionPending = None

                # self.Menu.menu_state = "waiting_player_id"

            if self.Menu.p_join_session is not None:
                self.current_joined_session = self.Menu.p_join_session
                self.send_to_server(f"[JoinedSession]:{self.current_joined_session}")
                self.Menu.p_join_session = None

            if self.Menu.p_character_update:
                update_data = {
                    "player_id": self.Menu.CurrentPlayer_id,
                    "character_1": self.Menu.character_1,
                    "character_2": self.Menu.character_2,
                    "character_3": self.Menu.character_3,
                    "session_name": self.Menu.current_session_name,
                }
                self.send_to_server(f"[CharacterUpdate]:{json.dumps(update_data)}")
                self.Menu.p_character_update = False

            if self.Menu.p_character_submission is not None:
                self.send_to_server(
                    f"[PlayerReady]:{json.dumps(self.Menu.p_character_submission)}"
                )
                self.Menu.p_character_submission = None

                self.Menu.update_player_ready(self.Menu.CurrentPlayer_id)
                if self._all_players_ready():
                    self.game_started = True

            if self.Menu.p_leave_session is not None:
                self.send_to_server(f"[LeaveSession]:{self.Menu.p_leave_session}")
                self.Menu.p_leave_session = None

            if self.Menu.p_unready:
                self.send_to_server(f"[PlayerUnready]:{self.Menu.CurrentPlayer_id}")
                self.Menu.p_unready = False

            # GAME STATE - Actual gameplay
            if self.etat == "game":
                dt = self.clock.tick(60) / 1000
                delta_time = int(dt * 1000)

                for event in pyg.event.get():
                    if event.type == pyg.QUIT:
                        self.running = False
                    elif event.type == pyg.KEYDOWN:
                        if event.key == pyg.K_ESCAPE:
                            self.running = False
                            self.send_to_server(message="ESC appuyé")
                        if event.key == pyg.K_F2:
                            self.dev_display_ = not self.dev_display_

                        keys_now = pyg.key.get_pressed()
                        if event.key == pyg.K_q:
                            if keys_now[pyg.K_e]:
                                if (
                                    self._retreat_cooldown == 0
                                    and not self.support_1.is_dead
                                ):
                                    if self.hud and not self.hud.isAssReady():
                                        pass
                                    else:
                                        current_pos = list(self.active_char.position)
                                        self.active_char, self.support_1 = (
                                            self.support_1,
                                            self.active_char,
                                        )
                                        self.active_char.position = current_pos
                                        self.player = self.active_char
                                        self._retreat_cooldown = 60
                                        if self.hud:
                                            self.hud.startAssCooldown(
                                                RETREAT_COOLDOWN_DURATION
                                            )
                                        self.send_to_server(
                                            f"[Retreat]:{json.dumps({'player_id': self.Menu.CurrentPlayer_id, 'slot': 1, 'active_char': self.active_char.char_num})}"
                                        )
                            else:
                                if (
                                    not self.support_1.is_dead
                                    and self.support_1.use_skill(1)
                                ):
                                    self.send_to_server(
                                        f"[SupportSkill]:{json.dumps({'player_id': self.Menu.CurrentPlayer_id, 'slot': 1, 'char_num': self.support_1.char_num, 'skill': 1})}"
                                    )

                        if event.key == pyg.K_w:
                            if keys_now[pyg.K_e]:
                                if (
                                    self._retreat_cooldown == 0
                                    and not self.support_2.is_dead
                                ):
                                    if self.hud and not self.hud.isAssReady():
                                        pass
                                    else:
                                        current_pos = list(self.active_char.position)
                                        self.active_char, self.support_2 = (
                                            self.support_2,
                                            self.active_char,
                                        )
                                        self.active_char.position = current_pos
                                        self.player = self.active_char
                                        self._retreat_cooldown = 60
                                        if self.hud:
                                            self.hud.startAssCooldown(
                                                RETREAT_COOLDOWN_DURATION
                                            )
                                        self.send_to_server(
                                            f"[Retreat]:{json.dumps({'player_id': self.Menu.CurrentPlayer_id, 'slot': 2, 'active_char': self.active_char.char_num})}"
                                        )
                            else:
                                if (
                                    not self.support_2.is_dead
                                    and self.support_2.use_skill(1)
                                ):
                                    self.send_to_server(
                                        f"[SupportSkill]:{json.dumps({'player_id': self.Menu.CurrentPlayer_id, 'slot': 2, 'char_num': self.support_2.char_num, 'skill': 1})}"
                                    )

                        if event.key == pyg.K_a:
                            self._send_skill(1)
                        if event.key == pyg.K_s:
                            self._send_skill(2)
                        if event.key == pyg.K_d:
                            self._send_skill(3)

                if self._retreat_cooldown > 0:
                    self._retreat_cooldown -= 1

                # draw background
                self.screen.blit(self.map_back, (0, 0))

                # movement
                keys_pressed = pyg.key.get_pressed()
                is_moving = (
                    keys_pressed[pyg.K_RIGHT]
                    or keys_pressed[pyg.K_LEFT]
                    or keys_pressed[pyg.K_UP]
                    or keys_pressed[pyg.K_DOWN]
                )

                if keys_pressed[pyg.K_UP]:
                    self.active_char.move("up")
                if keys_pressed[pyg.K_DOWN]:
                    self.active_char.move("down")
                if keys_pressed[pyg.K_LEFT]:
                    self.active_char.move("left")
                if keys_pressed[pyg.K_RIGHT]:
                    self.active_char.move("right")

                self.active_char.update_animation(delta_time, is_moving)

                # Draw active character
                current_sprite = self.active_char.get_current_sprite()
                player_pos = self.active_char.position
                if current_sprite is not None:
                    dx, dy = self.active_char.get_blit_offset(current_sprite)
                    self.screen.blit(
                        current_sprite, (player_pos[0] + dx, player_pos[1] + dy)
                    )

                char = self.active_char
                if hasattr(char, "bubble_effect") and char.bubble_effect:
                    char.bubble_effect.x = char.position[0]
                    char.bubble_effect.y = char.position[1]
                    char.bubble_effect.draw(self.screen)

                targets = list(self.remote_players.values())
                self.active_char.update_projectiles(delta_time, targets)
                self.active_char.check_hits(targets)
                self.active_char.draw_projectiles(self.screen)

                if self.hud and self.active_char:
                    delta = self._last_char_health - self.active_char.health
                    if delta > 0:
                        # Conversion : health 0-100 → HUD 54 points visuels
                        hud_dmg = max(1, round(delta * 54 / 100))
                        self.hud.DealsDamage(hud_dmg)
                    self._last_char_health = self.active_char.health

                # DRaw remote player
                for pid, remote_char in self.remote_players.items():
                    remote_char.check_hits([self.active_char])
                    remote_char.update_projectiles(delta_time, [self.active_char])
                    remote_char.draw_projectiles(self.screen)

                    remote_sprite = remote_char.get_current_sprite()
                    if remote_sprite:
                        dx, dy = remote_char.get_blit_offset(remote_sprite)
                        rpos = remote_char.position
                        self.screen.blit(remote_sprite, (rpos[0] + dx, rpos[1] + dy))

                    if (
                        hasattr(remote_char, "bubble_effect")
                        and remote_char.bubble_effect
                    ):
                        remote_char.bubble_effect.x = remote_char.position[0]
                        remote_char.bubble_effect.y = remote_char.position[1]
                        remote_char.bubble_effect.update(delta_time)
                        remote_char.bubble_effect.draw(self.screen)
                        if not remote_char.status.is_disabled:
                            remote_char.bubble_effect = None
                            remote_char.is_hidden = False

                    effect_sprite = remote_char.get_effect_sprite()
                    if effect_sprite:
                        ex = remote_char.position[0]
                        ey = remote_char.position[1]
                        if remote_char.direction == "right":
                            ex += FRAME_SIZE
                        else:
                            ex -= FRAME_SIZE
                        self.screen.blit(effect_sprite, (ex, ey))

                # Foreground
                self.screen.blit(self.map_front, (0, 0))

                # Broadcast HUD
                self._broadcast_hud_state()

                # Draw char 6 special HUD
                if self._char6_cans_loaded and self.active_char.char_num == 6:
                    water = getattr(self.active_char, "water_cans", 4)
                    soda = getattr(self.active_char, "soda_cans", 4)
                    self._draw_char6_hud(
                        self.screen, self.Menu.CurrentPlayer_id, water, soda
                    )

                self.delta_time_entity_send += 1
                if self.delta_time_entity_send >= self.SENT_INTERVAL:
                    self.delta_time_entity_send = 0
                    if self.current_joined_session and self.Menu.CurrentPlayer_id:
                        entity_state = {
                            "char_number": self.active_char.char_num,
                            "direction": self.active_char.direction,
                            "health": self.active_char.health,
                            "pos": list(player_pos),
                            "is_hidden": self.active_char.is_hidden,
                            "is_moving": bool(is_moving),
                            "is_attacking": {
                                "1": self.active_char.is_attacking_s1,
                                "2": self.active_char.is_attacking_s2,
                                "3": self.active_char.is_attacking_s3,
                            },
                            "is_dead": self.active_char.is_dead,
                            "is_hurt": self.active_char.is_hurt,
                            "anim_indices": {
                                "idle": self.active_char.frame_IDLE,
                                "move": self.active_char.frame_MOVE,
                                "dead": 0,
                                "effect1": 0,
                                "hurt": self.active_char.frame_HURT,
                                "effect2": 0,
                                "effect3": 0,
                                "skill1": self.active_char.frame_S1,
                                "skill2": self.active_char.frame_S2,
                                "skill3": self.active_char.frame_S3,
                            },
                            "attack_hitboxes": {},
                        }
                        payload = {
                            "session": self.current_joined_session,
                            "player_id": self.Menu.CurrentPlayer_id,
                            "state": entity_state,
                        }
                        self.send_to_server(f"[EntityState]:{json.dumps(payload)}")

                self.active_char.draw_hitbox(self.screen)
                # draw HUD
                if self.hud:
                    self.hud.update(dt)
                    x, y = HUD_POSITIONS.get(self.Menu.CurrentPlayer_id, (10, 10))
                    self.hud.draw(self.screen, x, y)

                for pid, other_hud in self.other_huds.items():
                    other_hud.update(dt)
                    ox, oy = HUD_POSITIONS.get(pid, (10, 10))
                    other_hud.draw(self.screen, ox, oy)

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
