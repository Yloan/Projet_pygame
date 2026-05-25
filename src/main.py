import json
import os
import queue
import random as r
import socket
import sys
import threading
import time

import pygame as pyg

import game.characters as player_module
import game.ia as bot_module
import game.map_laoder as _map_mod
import ui.menu as menu
import ui.Music as music_module
import utils.paths as __path__
from game.characters import (
    BUBBLE_EFFECT_DATA,
    FRAME_SIZE,
    PROJECTILES_INFOS,
    Character,
    Projectile,
    SubProjectile,
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
from ui.HUD import HUD, _draw_char4_hud, _draw_char5_hud, _load_spec_hud_sheets
from ui.menu_in_game import InGameMenu

# Gloabl variables
MESSAGE_DELIMITER = "\n"
HUD_POSITIONS = {1: (10, 10), 2: (993, 10), 3: (10, 530), 4: (993, 530)}

TIME_BEFORE_PROJECTILE = {1: {"s1": 4, "s2": 4}, 5: {"s1": 4}}

COLLISION_THICKNESS = 10
# This will be changed when we will implement the other map (spawn slot by map)
SPAWN_POSITIONS = {
    1: (150, 320),
    2: (1050, 320),
    3: (260, 320),
    4: (1050, 350),
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

BOTS_ENABLED: bool = True


class Game:
    def __init__(self, width=1280, height=720, fullscreen=False):

        self.width = width
        self.height = height
        self.fullscreen = fullscreen
        self.etat = "menu"
        self.game_started = False
        self.dev_display_ = False
        self.delta_time_sessions_send = 0
        self.Menu = menu.Menu(
            width=self.width, height=self.height, fullscreen=self.fullscreen
        )

        #    init sound
        pyg.mixer.pre_init(44100, -16, 2, 512)
        pyg.init()
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

        self.music_play = False

        # LOAD GAME MAP (surfaces vides par défaut, chargées à la sélection de map)
        self.map_back = pyg.Surface((self.width, self.height))
        self.map_front = pyg.Surface((self.width, self.height), pyg.SRCALPHA)

        self.active_char = None
        self.support_1 = None
        self.support_2 = None
        self.player = None
        self._game_initialized = False
        self._retreat_cooldown = 0
        self.running = False

        # In-game pause menu
        self._paused = False
        self._frozen_frame = None
        self._in_game_menu = InGameMenu(self.width, self.height)

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

        self.musics_names = [
            "Slower_blitzkrieg.mp3",
            "howling_hound_music-retro-egyptian-theme-187380.mp3",
            "NewForestmusicBlitzkrieg.mp3",
        ]

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

        self._chrg_frms = None
        self._wtr_frms = None
        self._sda_frms = None
        self._spec_hud_loaded = False

        self.bots = []

        self.choose_map = False
        self.map_choosen = None

        # Game-over state
        self._game_over_timer = 0
        self._game_over_result = None

        # Camera shake
        self._shake_timer = 0
        self._shake_strength = 0

    def switch_music(self, i=None):
        try:
            self.musics[self.current_music].stop()
        except Exception:
            pass

        if i is not None:
            self.current_music = i
        else:
            self.current_music = (self.current_music + 1) % len(self.musics)

        # Lancer la nouvelle piste
        try:
            self.musics[self.current_music].play()
            self.musics[self.current_music].volume(0.01)
        except Exception:
            pass

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
        max_humans = 4 - (session_info.nb_bots if session_info else 0)

        human_present = {self.Menu.CurrentPlayer_id}
        for p_id in range(1, max_humans + 1):
            if any(c is not None for c in self.Menu.players_characters[p_id]):
                human_present.add(p_id)

        if not human_present:
            return False

        ready_count = sum(1 for p_id in human_present if self.Menu.players_ready[p_id])
        return ready_count == len(human_present) and ready_count > 0

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

                except Exception as e:
                    print_error(f"Erreur player ID: {e}")

            elif message.startswith("[SessionDeleted]:"):
                if self.game_started and self._game_over_result is None:
                    self._game_over_result = "win"
                    self._game_over_timer = 0

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
                        if self.Menu.menu_state not in ("maps_selection", "start game"):
                            self.Menu.menu_state = "maps_selection"
                except Exception as e:
                    print_error(f"Erreur PlayerReady: {e}")

            elif message.startswith("[MapVotesUpdate]:"):
                try:
                    votes = json.loads(message.split(":", 1)[1])
                    self.Menu.update_map_votes(votes)
                except Exception as e:
                    print_error(f"Erreur MapVotesUpdate: {e}")

            elif message.startswith("[StartGame]:"):
                try:
                    self.Menu.map_player_votes = {}
                    self.choose_map = False
                    self.map_choosen = None
                    map_index = int(message.split(":", 1)[1])
                    map_loader = MapLoader(None, map_index)
                    background, foreground = map_loader.load_map()
                    self.map_back = pyg.transform.scale(
                        background, (self.width, self.height)
                    )
                    self.map_front = pyg.transform.scale(
                        foreground, (self.width, self.height)
                    )
                    self.game_started = True
                except Exception as e:
                    print_error(f"Erreur StartGame: {e}")
                    self.game_started = True

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
                    if self.game_started and self._game_over_result is None:
                        leaving = self.remote_players.pop(player_id, None)
                        # Ignorer si ce joueur n'était pas dans notre partie
                        if leaving is not None and len(self.remote_players) == 0:
                            if not leaving.is_dead:
                                self._game_over_result = "win"
                                self._game_over_timer = 0
                except Exception as e:
                    print_error(f"Erreur PlayerLeft: {e}")

            elif message.startswith("[HUDUpdate]:"):
                if not self.game_started:
                    continue
                data = json.loads(message.split(":", 1)[1])
                pid = data["player_id"]
                my_id = self.Menu.CurrentPlayer_id
                if my_id is not None and pid != my_id:
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
                                if pid in self.other_huds:
                                    self.other_huds[pid].set_portrait(char_num)
                            except Exception as e:
                                print_error(
                                    f"Impossible de créer remote Character-{char_num}: {e}"
                                )
                                continue

                        elif self.remote_players[pid].char_num != char_num:
                            old_pos = list(self.remote_players[pid].position)
                            try:
                                self.remote_players[pid] = make_character(char_num)
                                self.remote_players[pid].is_remote = True
                                self.remote_players[pid].position = old_pos
                                if pid in self.other_huds:
                                    self.other_huds[pid].set_portrait(char_num)
                            except Exception as e:
                                print_error(
                                    f"Impossible de recréer remote Character-{char_num}: {e}"
                                )
                                continue

                        self.remote_players[pid].apply_network_state(state)

                except Exception as e:
                    print_error(f"Erreur GameState: {e}")

            elif message.startswith("[BubbleHit]:"):
                try:
                    data = json.loads(message.split(":", 1)[1])
                    if (
                        data.get("victim_id") == self.Menu.CurrentPlayer_id
                        and self.active_char
                    ):
                        self.active_char.is_hidden = True
                        self.active_char.bubble_source_char = data["caster"]
                        effect_data = BUBBLE_EFFECT_DATA.get(int(data["caster"]))
                        if effect_data and not self.active_char.bubble_effect:
                            self.active_char.bubble_effect = SubProjectile(
                                self.active_char.position[0],
                                self.active_char.position[1],
                                effect_data,
                            )
                        self.active_char.status.apply_disabled(
                            data.get("direction", "right")
                        )
                        self.active_char.status.apply_wet()
                except Exception as e:
                    print_error(f"Erreur BubbleHit: {e}")

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
                        f"[DeleteSession]:{self.current_joined_session}\n".encode(
                            "utf-8"
                        )
                    )
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
        self.other_huds = {}

        c1 = self.Menu.character_1 or 1
        c2 = self.Menu.character_2 or 1
        c3 = self.Menu.character_3 or 1

        if c1 in (4, 5) or c2 in (4, 5) or c3 in (4, 5):
            _load_spec_hud_sheets(self)

        spawn = list(SPAWN_POSITIONS.get(self.Menu.CurrentPlayer_id, (150, 320)))

        self.active_char = player_module.make_character(c1)
        self.support_1 = player_module.make_character(c2)
        self.support_2 = player_module.make_character(c3)

        if self.hud:
            self.hud.set_portrait(c1)

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
        for wall in _map_mod.ACTIVE_COLLISIONS:
            pyg.draw.rect(self.screen, (255, 0, 255), wall, 2)

    def _broadcast_hud_state(self):
        if not hasattr(self, "hud") or self.hud is None:
            return
        payload = {
            "player_id": self.Menu.CurrentPlayer_id,
            "hud": self.hud.toNetworkData(),
        }
        self.send_to_server(f"[HUDUpdate]:{json.dumps(payload)}")

    _STATUS_ICON_FILES = {
        "burn":     "status-icone-1.png",
        "grabbed":  "status-icone-2.png",
        "disabled": "status-icone-3.png",
        "wet":      "status-icone-4.png",
        "weakened": "status-icone-5.png",
        "oiled":    "status-icone-6.png",
        "pushed":   {"right": "status-icone-7-1.png", "left": "status-icone-7-2.png"},
        "stun":     "status-icone-13.png",
    }
    _ICON_SIZE = 32
    _HUD_H = 192

    def _load_status_icons(self):
        self._status_icon_imgs = {}
        sz = self._ICON_SIZE
        for key, val in self._STATUS_ICON_FILES.items():
            try:
                if isinstance(val, dict):
                    self._status_icon_imgs[key] = {
                        d: pyg.transform.scale(
                            pyg.image.load(
                                __path__.get_asset_path("status", fname)
                            ).convert_alpha(),
                            (sz, sz),
                        )
                        for d, fname in val.items()
                    }
                else:
                    self._status_icon_imgs[key] = pyg.transform.scale(
                        pyg.image.load(
                            __path__.get_asset_path("status", val)
                        ).convert_alpha(),
                        (sz, sz),
                    )
            except Exception as e:
                print_warning(f"[STATUS ICON] impossible de charger '{val}': {e}")

    def _draw_status_icons(self, surface, status_manager, hud_x, hud_y, player_id):
        if not hasattr(self, "_status_icon_imgs"):
            self._load_status_icons()

        active = []
        for key in self._STATUS_ICON_FILES:
            eff = status_manager.effects.get(key)
            if eff and eff.is_active:
                imgs = self._status_icon_imgs.get(key)
                if imgs is None:
                    continue
                if isinstance(imgs, dict):
                    direction = getattr(eff, "direction", "right")
                    img = imgs.get(direction, next(iter(imgs.values())))
                else:
                    img = imgs
                active.append(img)

        if not active:
            return

        sz = self._ICON_SIZE
        gap = 4

        if player_id in (1, 2):
            ix = hud_x
            iy = hud_y + self._HUD_H + 4
        else:
            ix = hud_x
            iy = hud_y - sz - 4

        for idx, img in enumerate(active):
            surface.blit(img, (ix + idx * (sz + gap), iy))

    def _draw_game_over_overlay(self, surface, result):
        overlay = pyg.Surface((self.width, self.height), pyg.SRCALPHA)
        overlay.fill((0, 0, 0, 130))
        surface.blit(overlay, (0, 0))

        if result == "win":
            text = "You won !!"
            color = (80, 255, 80)
        else:
            text = "You loose..."
            color = (255, 60, 60)

        big_font = pyg.font.SysFont("arialblack", 72)
        img = big_font.render(text, True, color)
        cx = (self.width - img.get_width()) // 2
        cy = (self.height - img.get_height()) // 2
        surface.blit(img, (cx, cy))

    def _reset_to_menu(self):
        if self.current_joined_session:
            session_name = self.current_joined_session
            try:
                if self._client_socket:
                    self._client_socket.send(
                        f"[DeleteSession]:{session_name}\n".encode("utf-8")
                    )
                    self._client_socket.send(
                        f"[LeaveSession]:{session_name}\n".encode("utf-8")
                    )
            except Exception:
                pass
            self.Menu.sessions = [
                s for s in self.Menu.sessions if s.titre != session_name
            ]
            self.current_joined_session = None
        self.game_started = False
        self._game_initialized = False
        self._game_over_result = None
        self._game_over_timer = 0
        self.bots = []
        self.active_char = None
        self.support_1 = None
        self.support_2 = None
        self.player = None
        self.hud = None
        self.other_huds = {}
        self.remote_players = {}
        self.Menu.CurrentPlayer_id = None
        self.choose_map = False
        self.map_choosen = None

        # Reset music
        self.music_play = False
        self.switch_music(0)

        # Reset pause state
        self._paused = False

        # Reset menu state
        self.etat = "menu"
        self.Menu.etat = "menu"
        self.Menu.menu_state = "main"
        self.Menu.players_ready = {1: False, 2: False, 3: False, 4: False}
        self.Menu.map_player_votes = {}

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

    def run(self):

        # Initialize and connect to server
        self.running = True
        self._connect_to_server()

        screen = self.screen

        self.etat = "menu"
        # self.etat = "game"

        # When starting directly in game initialise characters with defaults
        self.musics[self.current_music].play()
        self.musics[self.current_music].volume(0.01)
        while self.running:
            # Launch music

            self._process_network_messages()
            # MENU STATE
            if self.etat == "menu":
                self.music_play = False
                screen.blit(self.wallpaper, (0, 0))

                self.Menu.method_menu()
                if self.game_started and not self._game_initialized:
                    self._init_game_characters()
                    self._game_initialized = True
                    self.etat = "game"
                    self.Menu.etat = "game"

                    if BOTS_ENABLED:
                        session_info = next(
                            (
                                s
                                for s in self.Menu.sessions
                                if s.titre == self.current_joined_session
                            ),
                            None,
                        )
                        nb_bots = session_info.nb_bots if session_info else 1
                        nb_players = session_info.nb_players if session_info else 1
                        for i in range(nb_bots):
                            bot_id = 4 - i
                            spawn = SPAWN_POSITIONS.get(bot_id, (640, 360))
                            bot = bot_module.Bot(
                                char_num=r.randint(1, 5),
                                nb_players=nb_players,
                                position=spawn,
                            )
                            bot.bot_id = bot_id
                            bot.health = bot.char.health
                            self.other_huds[bot_id] = HUD(bot_id)
                            self.other_huds[bot_id].set_portrait(bot.char.char_num)
                            self.bots.append(bot)

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
                            pyg.quit()
                            import sys

                            sys.exit(0)
                        if event.key == pyg.K_F2:
                            self.dev_display_ = not self.dev_display_
                            Character.switch_TMP__GET_SURFACE_HITBOX_ATTACKS_()
                    elif event.type == pyg.MOUSEBUTTONDOWN:
                        if event.button == 4:
                            self.Menu.scroll_y = max(0, self.Menu.scroll_y - 30)
                        if event.button == 5:
                            self.Menu.scroll_y += 30
                        if (
                            event.button == 1
                            and self.Menu.menu_state == "maps_selection"
                        ):
                            for num_map, slot_map in self.Menu.rects_img_maps.items():
                                if not slot_map.collidepoint(event.pos):
                                    continue
                                if self.current_joined_session:
                                    # Session : envoyer le vote au serveur
                                    if self.choose_map:
                                        self.send_to_server(
                                            f"[UnchooseMap]:{self.map_choosen}"
                                        )
                                        self.Menu.map_player_votes.pop(
                                            self.Menu.CurrentPlayer_id, None
                                        )
                                        self.choose_map = False
                                        self.map_choosen = None
                                    self.send_to_server(f"[ChooseMap]:{num_map}")
                                    self.Menu.map_player_votes[
                                        self.Menu.CurrentPlayer_id
                                    ] = num_map
                                    self.map_choosen = num_map
                                    self.choose_map = True

                                    human_ready = [
                                        pid
                                        for pid, rdy in self.Menu.players_ready.items()
                                        if rdy
                                    ]
                                    if len(human_ready) <= 1:
                                        try:
                                            map_loader = MapLoader(None, num_map)
                                            background, foreground = (
                                                map_loader.load_map()
                                            )
                                            self.map_back = pyg.transform.scale(
                                                background, (self.width, self.height)
                                            )
                                            self.map_front = pyg.transform.scale(
                                                foreground, (self.width, self.height)
                                            )
                                        except Exception as e:
                                            print_error(
                                                f"Erreur chargement map {num_map}: {e}"
                                            )
                                        self.game_started = True
                                else:
                                    try:
                                        map_loader = MapLoader(None, num_map)
                                        background, foreground = map_loader.load_map()
                                        self.map_back = pyg.transform.scale(
                                            background, (self.width, self.height)
                                        )
                                        self.map_front = pyg.transform.scale(
                                            foreground, (self.width, self.height)
                                        )
                                    except Exception as e:
                                        print_error(
                                            f"Erreur chargement map {num_map}: {e}"
                                        )
                                    self.game_started = True
                                break

                    if self.Menu.menu_state == "creation_parameters_session_menu":
                        self.Menu.input_box.handle_event(event)

            self.delta_time_sessions_send += 1
            # Send sessions to server

            if self.Menu.sessionPending is not None:
                self.send_to_server(
                    f"[CreateSession]:{json.dumps(self.Menu.sessionPending)}"
                )
                self.current_joined_session = self.Menu.sessionPending["titre"]
                self.Menu.sessionPending = None

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
                    if self.Menu.menu_state not in ("maps_selection", "start game"):
                        self.Menu.menu_state = "maps_selection"

            if self.Menu.p_leave_session is not None:
                self.send_to_server(f"[LeaveSession]:{self.Menu.p_leave_session}")
                self.Menu.p_leave_session = None

            if self.Menu.p_unready:
                self.send_to_server(f"[PlayerUnready]:{self.Menu.CurrentPlayer_id}")
                self.Menu.p_unready = False

            delta_time = 0

            # GAME STATE - Actual gameplay
            if self.etat == "game":
                if not self.music_play:
                    self.music_play = True
                    map_id = self.map_choosen if self.map_choosen is not None else 1
                    self.switch_music(1 if map_id == 2 else 2)

                dt = self.clock.tick(60) / 1000
                delta_time = int(dt * 1000)

                for event in pyg.event.get():
                    if event.type == pyg.QUIT:
                        self.running = False
                    elif event.type == pyg.KEYDOWN:
                        if event.key == pyg.K_ESCAPE:
                            self._paused = not self._paused
                            if self._paused:
                                self._frozen_frame = self.screen.copy()
                        if event.key == pyg.K_F2:
                            self.dev_display_ = not self.dev_display_
                            Character.switch_TMP__GET_SURFACE_HITBOX_ATTACKS_()

                        keys_now = pyg.key.get_pressed()
                        if (
                            self.active_char.is_dead
                            or self._game_over_result is not None
                        ):
                            continue
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
                                            self.hud.set_portrait(
                                                self.active_char.char_num
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
                                            self.hud.set_portrait(
                                                self.active_char.char_num
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

                if self._paused:
                    # Blit the frozen frame then overlay the menu
                    if self._frozen_frame:
                        self.screen.blit(self._frozen_frame, (0, 0))
                    # Redraw HUDs on top of the frozen frame
                    if self.hud:
                        hx, hy = HUD_POSITIONS.get(self.Menu.CurrentPlayer_id, (10, 10))
                        self.hud.draw(self.screen, hx, hy)
                    for pid, other_hud in self.other_huds.items():
                        ox, oy = HUD_POSITIONS.get(pid, (10, 10))
                        other_hud.draw(self.screen, ox, oy)
                    pause_action = self._in_game_menu.draw(self.screen)
                    if pause_action == "resume":
                        self._paused = False
                    elif pause_action == "quit":
                        self._paused = False
                        self._reset_to_menu()
                    pyg.display.flip()
                    continue

                # draw background
                self.screen.blit(self.map_back, (0, 0))

                keys_pressed = pyg.key.get_pressed()
                is_moving = False

                if self._game_over_result is None and not self.active_char.is_dead:
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

                for skill_num, proj in self.active_char._just_spawned_projectiles:
                    base = {
                        "player_id": self.Menu.CurrentPlayer_id,
                        "session": self.current_joined_session,
                        "char_num": self.active_char.char_num,
                        "skill_num": skill_num,
                        "x": self.active_char.position[0],
                        "y": self.active_char.position[1],
                        "direction": self.active_char.direction,
                    }
                    self.send_to_server(f"[ProjectileSpawned]:{json.dumps(base)}")
                self.active_char._just_spawned_projectiles.clear()

                # Draw active character
                if self._game_over_result is None:
                    current_sprite = self.active_char.get_current_sprite()
                    player_pos = self.active_char.position
                    if current_sprite is not None:
                        dx, dy = self.active_char.get_blit_offset(current_sprite)
                        self.screen.blit(
                            current_sprite, (player_pos[0] + dx, player_pos[1] + dy)
                        )

                if self._game_over_result is None:
                    char = self.active_char
                    if hasattr(char, "bubble_effect") and char.bubble_effect:
                        char.bubble_effect.x = char.position[0]
                        char.bubble_effect.y = char.position[1]
                        char.bubble_effect.draw(self.screen)

                if not BOTS_ENABLED:
                    targets = [
                        rc for rc in self.remote_players.values() if not rc.is_dead
                    ]
                    self.active_char.update_projectiles(delta_time, targets)
                    self.active_char.check_hits(targets)
                    self.active_char.draw_projectiles(self.screen)

                if BOTS_ENABLED:
                    bot_chars = [bot.char for bot in self.bots]
                    for i, bot in enumerate(self.bots):
                        if bot.char.is_dead:
                            sprite = bot.char.get_current_sprite()
                            if sprite:
                                dx, dy = bot.char.get_blit_offset(sprite)
                                pos = bot.current_position
                                self.screen.blit(sprite, (pos[0] + dx, pos[1] + dy))
                            continue

                        bot.update_player_position(
                            self.Menu.CurrentPlayer_id, list(self.active_char.position)
                        )

                        if hasattr(bot, "bot_id") and bot.bot_id in self.other_huds:
                            delta = bot.health - bot.char.health
                            if delta > 0:
                                hud_dmg = max(1, round(delta * 54 / 100))
                                self.other_huds[bot.bot_id].DealsDamage(hud_dmg)
                            bot.health = bot.char.health

                        for pid, remote_char in self.remote_players.items():
                            bot.update_player_position(pid, list(remote_char.position))

                        for j, other_bot in enumerate(self.bots):
                            if j != i:
                                bot.update_player_position(
                                    -(j + 1),
                                    list(other_bot.current_position),
                                )

                        if self._game_over_result is None:
                            bot.update(delta_time)

                        if (
                            self._game_over_result is None
                            and not self.active_char.is_dead
                        ):
                            bot.char.check_hits([self.active_char])

                        live_targets = [self.active_char] + [
                            rc for rc in self.remote_players.values() if not rc.is_dead
                        ]
                        bot.char.update_projectiles(delta_time, live_targets)
                        bot.char.draw_projectiles(self.screen)

                        sprite = bot.char.get_current_sprite()
                        if sprite:
                            dx, dy = bot.char.get_blit_offset(sprite)
                            pos = bot.current_position
                            self.screen.blit(sprite, (pos[0] + dx, pos[1] + dy))

                        if (
                            hasattr(bot.char, "bubble_effect")
                            and bot.char.bubble_effect
                        ):
                            bot.char.bubble_effect.x = bot.current_position[0]
                            bot.char.bubble_effect.y = bot.current_position[1]
                            bot.char.bubble_effect.draw(self.screen)

                    live_targets = list(self.remote_players.values()) + [
                        b.char for b in self.bots if not b.char.is_dead
                    ]
                    self.active_char.update_projectiles(delta_time, live_targets)
                    _prev_s3_hit = self.active_char.s3_hit
                    self.active_char.check_hits(live_targets)
                    if (
                        not _prev_s3_hit
                        and self.active_char.s3_hit
                        and self.active_char.char_num == 2
                        and self.current_joined_session
                    ):
                        for pid, rchar in self.remote_players.items():
                            if rchar.is_hidden and rchar.bubble_source_char == 2:
                                self.send_to_server(
                                    f"[BubbleHit]:{json.dumps({'session': self.current_joined_session, 'victim_id': pid, 'caster': 2, 'direction': self.active_char.direction})}"
                                )
                                break
                    self.active_char.draw_projectiles(self.screen)
                    # Remplacer le bloc actuel (autour de "if self.active_char.is_dead") par :

                    if self.active_char.is_dead:
                        if not self.support_1.is_dead:
                            current_pos = list(self.active_char.position)
                            self.active_char, self.support_1 = (
                                self.support_1,
                                self.active_char,
                            )
                            self.active_char.position = current_pos
                            self.player = self.active_char
                            self._last_char_health = self.active_char.health
                            if self.hud:
                                pct = self.active_char.health / max(
                                    1, self.active_char.max_health
                                )
                                self.hud.setHealth(round(pct * 17))
                                self.hud.set_portrait(self.active_char.char_num)
                        elif not self.support_2.is_dead:
                            current_pos = list(self.active_char.position)
                            self.active_char, self.support_2 = (
                                self.support_2,
                                self.active_char,
                            )
                            self.active_char.position = current_pos
                            self.player = self.active_char
                            self._last_char_health = self.active_char.health
                            if self.hud:
                                pct = self.active_char.health / max(
                                    1, self.active_char.max_health
                                )
                                self.hud.setHealth(round(pct * 17))
                                self.hud.set_portrait(self.active_char.char_num)

                    # ── Mise à jour HUD AVANT la vérification game over ──────────────────
                    if self.hud and self.active_char:
                        delta = self._last_char_health - self.active_char.health
                        if delta > 0:
                            hud_dmg = max(1, round(delta * 54 / 100))
                            self.hud.DealsDamage(hud_dmg)
                            self._shake_timer = 350
                            self._shake_strength = min(10, 4 + delta // 5)
                        if self.active_char.health <= 0 and self.hud.currentHealth > 0:
                            self.hud.setHealth(0)
                        self._last_char_health = self.active_char.health

                    # ── Vérification game over APRÈS la mise à jour HUD ──────────────────
                    if self._game_over_result is None:
                        all_bots_dead = (
                            BOTS_ENABLED
                            and bool(self.bots)
                            and all(b.char.is_dead for b in self.bots)
                        )
                        all_players_dead = (
                            self.active_char.is_dead
                            and self.support_1.is_dead
                            and self.support_2.is_dead
                        )
                        all_remotes_dead = bool(self.remote_players) and all(
                            rc.is_dead for rc in self.remote_players.values()
                        )
                        if all_bots_dead or all_remotes_dead:
                            self._game_over_result = "win"
                            self._game_over_timer = 0
                        elif all_players_dead:
                            self._game_over_result = "lose"
                            self._game_over_timer = 0
                if self._game_over_result is not None:
                    self._game_over_timer += delta_time
                    if self._game_over_timer >= 3000:
                        self._reset_to_menu()
                        continue  # skip the rest of the draw pipeline

                # DRaw remote player
                if self._game_over_result is None:
                    for pid, remote_char in self.remote_players.items():
                        remote_char.check_hits(
                            [self.active_char]
                        )  # Probablement un bug reste a voir apres
                        remote_char.update_projectiles(delta_time, [self.active_char])
                        remote_char.draw_projectiles(self.screen)

                        remote_sprite = remote_char.get_current_sprite()
                        if remote_sprite:
                            dx, dy = remote_char.get_blit_offset(remote_sprite)
                            rpos = remote_char.position
                            self.screen.blit(
                                remote_sprite, (rpos[0] + dx, rpos[1] + dy)
                            )

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
                if self._spec_hud_loaded:
                    cnum = self.active_char.char_num
                    if cnum == 4:
                        _draw_char4_hud(self, self.screen, self.Menu.CurrentPlayer_id)
                    elif cnum == 5:
                        _draw_char5_hud(self, self.screen, self.Menu.CurrentPlayer_id)

                self.delta_time_entity_send += 1
                if self.delta_time_entity_send >= self.SENT_INTERVAL:
                    self.delta_time_entity_send = 0
                    if self.current_joined_session and self.Menu.CurrentPlayer_id:
                        entity_state = {
                            "char_number": self.active_char.char_num,
                            "direction": self.active_char.direction,
                            "health": self.active_char.health,
                            "pos": list(player_pos),
                            "bubble_caster": getattr(
                                self.active_char, "bubble_source_char", None
                            ),
                            "is_hidden": self.active_char.is_hidden,
                            "is_moving": bool(is_moving),
                            "s3_hit": self.active_char.s3_hit,
                            "frame_s3_2": self.active_char.frame_S3_2,
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
                            "char_state": self.active_char.get_network_state(),
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

                if self.active_char and hasattr(self.active_char, "status"):
                    hx, hy = HUD_POSITIONS.get(self.Menu.CurrentPlayer_id, (10, 10))
                    self._draw_status_icons(
                        self.screen,
                        self.active_char.status,
                        hx,
                        hy,
                        self.Menu.CurrentPlayer_id,
                    )

                if BOTS_ENABLED:
                    for bot in self.bots:
                        if hasattr(bot, "bot_id") and hasattr(bot.char, "status"):
                            bx, by = HUD_POSITIONS.get(bot.bot_id, (10, 10))
                            self._draw_status_icons(
                                self.screen, bot.char.status, bx, by, bot.bot_id
                            )

                for pid, rchar in self.remote_players.items():
                    if hasattr(rchar, "status"):
                        rx, ry = HUD_POSITIONS.get(pid, (10, 10))
                        self._draw_status_icons(self.screen, rchar.status, rx, ry, pid)

                if self._game_over_result is not None:
                    self._draw_game_over_overlay(self.screen, self._game_over_result)

            if self.dev_display_:
                try:
                    self.dev_display()
                except Exception as e:
                    print(f"Error dev display| Error --> {e}")

            # Camera shake
            if self._shake_timer > 0 and self.etat == "game":
                ox = r.randint(-self._shake_strength, self._shake_strength)
                oy = r.randint(-self._shake_strength, self._shake_strength)
                frame = self.screen.copy()
                self.screen.fill((0, 0, 0))
                self.screen.blit(frame, (ox, oy))
                self._shake_timer = max(0, self._shake_timer - delta_time)
                if self._shake_timer == 0:
                    self._shake_strength = 0

            # Update display
            pyg.display.flip()

        # Graceful shutdown
        self.shutdown()


if __name__ == "__main__":
    if hasattr(sys, '_MEIPASS'):
        os.chdir(sys._MEIPASS)
    elif getattr(sys, 'frozen', False):
        os.chdir(os.path.dirname(sys.executable))
    game = Game(width=1280, height=720, fullscreen=False)
    game.run()
