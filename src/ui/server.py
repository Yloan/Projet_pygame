import json
import socket
import threading
from collections import Counter

from console import (
    print_debug,
    print_error,
    print_event,
    print_info,
    print_network,
    print_success,
    print_warning,
)

DEFAULTHOST = "0.0.0.0"
DEFAULTPORT = 12345

BUFFERMESSAGE = 4096  # 2^12 c'est deja bien assez
DELIMITEURMESSAGE = "\n"


class Serveur:
    def __init__(self, host=DEFAULTHOST, port=DEFAULTPORT):

        self.Port = port
        self.Host = host

        # CONNECTION MANAGMENT
        self.clients = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.Host, self.Port))

        self.recv_buffers = {}
        self.sessions_characters = {}
        self.socket_player_ids = {}

        # Game states
        self.game_states = {}
        self.game_states_lock = threading.Lock()

        # Map votes: {session_name: {player_id: map_num}}
        self.sessions_map_votes = {}

        # GLOBALS VARIABLES
        self.sessions = []
        self.sessions_lock = threading.Lock()
        self.sessions_clients_joined = {}

    def start_server(self):
        self.server_socket.listen()
        print_success(f"Serveur démarré sur host:{self.Host}; port:{self.Port}")
        accept_thread = threading.Thread(target=self.accept_clients, daemon=True)
        accept_thread.start()

    def accept_clients(self):
        while 1:
            client_socket, addr = self.server_socket.accept()
            print_event(f"Client connecté depuis {addr}")

            self.clients.append(client_socket)
            self.recv_buffers[client_socket] = ""

            threading.Thread(
                target=self.handle_client, args=(client_socket,), daemon=True
            ).start()

            self.broadcast_sessions()
            # self.start_game()

    def _send(self, client_socket, message):
        try:
            client_socket.send((message + DELIMITEURMESSAGE).encode("utf-8"))
            print_debug(message + DELIMITEURMESSAGE)
        except (BrokenPipeError, OSError):
            self._remove_dead_client(client_socket)
            raise

    def _remove_dead_client(self, client_socket):
        if client_socket in self.clients:
            self.clients.remove(client_socket)
        self.recv_buffers.pop(client_socket, None)
        if client_socket in self.socket_player_ids:
            left_session, left_pid = self.socket_player_ids.pop(client_socket)
            with self.sessions_lock:
                if left_session in self.sessions_clients_joined:
                    if client_socket in self.sessions_clients_joined[left_session]:
                        self.sessions_clients_joined[left_session].remove(client_socket)
                for s in self.sessions:
                    if s["titre"] == left_session:
                        s["nb_players"] = max(0, s.get("nb_players", 1) - 1)
                        break
                if left_session in self.sessions_characters:
                    self.sessions_characters[left_session].pop(left_pid, None)
            self.broadcast_except(
                f"[PlayerLeft]:{left_pid}", exclude_socket=client_socket
            )
            self.broadcast_sessions()
        try:
            client_socket.close()
        except Exception:
            pass

    def broadcast_except(self, message, exclude_socket=None):
        # Diffuse un message brut à tous les autres clients que le excluded
        for client in list(self.clients):
            if client != exclude_socket:
                try:
                    self._send(client, message)
                except (BrokenPipeError, OSError):
                    pass

    def handle_client(self, client_socket):
        while 1:
            chunk = client_socket.recv(BUFFERMESSAGE).decode("utf-8")
            if not chunk:
                break

            self.recv_buffers[client_socket] += chunk
            messages = self.recv_buffers[client_socket].split(DELIMITEURMESSAGE)

            self.recv_buffers[client_socket] = messages[-1]
            complete_messages = messages[:-1]

            for data in complete_messages:
                if data:
                    print_network(f"Reçu du client: {data}")
                    self._handle_message(data, client_socket)

        client_socket.close()
        if client_socket in self.clients:
            self.clients.remove(client_socket)

        self.recv_buffers.pop(client_socket, None)

        if client_socket in self.socket_player_ids:
            left_session, left_pid = self.socket_player_ids.pop(client_socket)

            with self.sessions_lock:
                if left_session in self.sessions_clients_joined:
                    if client_socket in self.sessions_clients_joined[left_session]:
                        self.sessions_clients_joined[left_session].remove(client_socket)

                for s in self.sessions:
                    if s["titre"] == left_session:
                        s["nb_players"] = max(0, s.get("nb_players", 1) - 1)
                        break

                if left_session in self.sessions_characters:
                    self.sessions_characters[left_session].pop(left_pid, None)

                remaining = self.sessions_clients_joined.get(left_session, [])
                if len(remaining) == 0:
                    self.sessions = [
                        s for s in self.sessions if s["titre"] != left_session
                    ]
                    self.sessions_clients_joined.pop(left_session, None)
                    self.sessions_characters.pop(left_session, None)
                    self.sessions_map_votes.pop(left_session, None)
                    print_success(
                        f"Session auto-supprimée (déconnexion) : {left_session}"
                    )

            self.broadcast_except(
                f"[PlayerLeft]:{left_pid}", exclude_socket=client_socket
            )
            self.broadcast_sessions()

        print_info("Client déconnecté")

    def _handle_message(self, data, client_socket):

        if data.startswith("[Sessions]"):
            json_str = data.split(":", 1)[1]
            session_data = json.loads(json_str)
            with self.sessions_lock:
                session_data["id"] = len(self.sessions)
                self.sessions.append(session_data)
                print_success(
                    f"Session créée: {session_data.get('titre', 'Without title')}"
                )
            self.broadcast_sessions()

        elif data.startswith("[CreateSession]:"):
            new_session_data = json.loads(data.split(":", 1)[1])
            new_session_data["nb_players"] = 0

            with self.sessions_lock:
                self.sessions.append(new_session_data)
                self.sessions_clients_joined[new_session_data["titre"]] = []
                self.sessions_characters[new_session_data["titre"]] = {}

            self.broadcast_sessions()

        elif data.startswith("[JoinedSession]:"):
            session_name = data.split(":", 1)[1]

            session_info = next(
                (s for s in self.sessions if s["titre"] == session_name), None
            )

            if session_info:
                nb_bots = session_info.get("nb_bots", 0)
                max_humans = 4 - nb_bots

                with self.sessions_lock:
                    if session_name not in self.sessions_clients_joined:
                        self.sessions_clients_joined[session_name] = []

                    if len(self.sessions_clients_joined[session_name]) < max_humans:
                        self.sessions_clients_joined[session_name].append(client_socket)
                        for s in self.sessions:
                            if s["titre"] == session_name:
                                s["nb_players"] = s.get("nb_players", 0) + 1
                                break
                        taken_ids = {
                            pid
                            for (sname, pid) in self.socket_player_ids.values()
                            if sname == session_name
                        }
                        player_id = next(i for i in range(1, 5) if i not in taken_ids)

                        self.socket_player_ids[client_socket] = (
                            session_name,
                            player_id,
                        )
                        self._send(client_socket, f"[YourPlayerID]:{player_id}")
                        print_success(
                            f"The player ID is {player_id} in {session_name} (Bots: {nb_bots})"
                        )
                        existing = self.sessions_characters.get(session_name, {})
                        for pid, chars in existing.items():
                            sync_data = {
                                "player_id": pid,
                                "character_1": chars[0],
                                "character_2": chars[1],
                                "character_3": chars[2],
                                "session_name": session_name,
                            }
                            self._send(
                                client_socket,
                                f"[CharacterUpdate]:{json.dumps(sync_data)}",
                            )
                    else:
                        self._send(client_socket, "[Error]:Session full")
                        print_warning(f"Session: {session_name} full.")

            self.broadcast_sessions()

        elif data.startswith("[HUDUpdate]:"):
            self.broadcast_except(data, exclude_socket=client_socket)

        elif data.startswith("[EntityState]:"):
            try:
                pl = json.loads(data.split(":", 1)[1])
                session_name = pl.get("session")
                player_id = pl.get("player_id")
                state = pl.get("state", {})

                if session_name and player_id is not None:
                    with self.game_states_lock:
                        if session_name not in self.game_states:
                            self.game_states[session_name] = {}
                        self.game_states[session_name][player_id] = state

                    # Diffuse l'état complet de la session aux players de la session
                    self._broadcast_game_state(session_name)

            except Exception as e:
                print_error(f"Erreur EntityState: {e}")

        elif data.startswith("[CharacterUpdate]:"):
            try:
                maj = json.loads(data.split(":", 1)[1])
                session_name = maj.get("session_name")
                player_id = maj.get("player_id")
                if session_name and player_id:
                    if session_name not in self.sessions_characters:
                        self.sessions_characters[session_name] = {}
                    self.sessions_characters[session_name][player_id] = [
                        maj.get("character_1"),
                        maj.get("character_2"),
                        maj.get("character_3"),
                    ]

            except Exception as e:
                print_error(f"Erreur CharacterUpdate: {e}")

            self.broadcast_except(data, exclude_socket=client_socket)
            print_network("CharacterUpdate spread")

        elif data.startswith("[PlayerUnready]:"):
            self.broadcast_except(data, exclude_socket=client_socket)
            print_network("PlayerUnready spread")

        elif data.startswith("[LeaveSession]:"):
            session_name = data.split(":", 1)[1]

            with self.sessions_lock:
                if session_name in self.sessions_clients_joined:
                    if client_socket in self.sessions_clients_joined[session_name]:
                        self.sessions_clients_joined[session_name].remove(client_socket)

                for s in self.sessions:
                    if s["titre"] == session_name:
                        s["nb_players"] = max(0, s.get("nb_players", 1) - 1)
                        break

                if client_socket in self.socket_player_ids:
                    left_session, left_pid = self.socket_player_ids.pop(client_socket)

                    if left_session in self.sessions_characters:
                        self.sessions_characters[left_session].pop(left_pid, None)
                    self.broadcast_except(
                        f"[PlayerLeft]:{left_pid}", exclude_socket=client_socket
                    )

                remaining = self.sessions_clients_joined.get(session_name, [])
                if len(remaining) == 0:
                    self.sessions = [
                        s for s in self.sessions if s["titre"] != session_name
                    ]
                    self.sessions_clients_joined.pop(session_name, None)
                    self.sessions_characters.pop(session_name, None)
                    self.sessions_map_votes.pop(session_name, None)
                    print_success(
                        f"Session auto-supprimée (plus de joueurs) : {session_name}"
                    )

            self.broadcast_sessions()

        elif data.startswith("[PlayerReady]:"):
            for client in self.clients:
                self._send(client, data)
            # self.broadcast_except(data, exclude_socket=client_socket)
            print_network("PlayerReady diffusé")

        elif data.startswith("[ChooseMap]:"):
            try:
                map_num = int(data.split(":", 1)[1])
                if client_socket in self.socket_player_ids:
                    session_name, player_id = self.socket_player_ids[client_socket]
                    if session_name not in self.sessions_map_votes:
                        self.sessions_map_votes[session_name] = {}
                    self.sessions_map_votes[session_name][player_id] = map_num
                    votes = self.sessions_map_votes[session_name]
                    vote_msg = f"[MapVotesUpdate]:{json.dumps(votes)}"
                    with self.sessions_lock:
                        clients_in = list(
                            self.sessions_clients_joined.get(session_name, [])
                        )
                    for c in clients_in:
                        self._send(c, vote_msg)
                    # Start game when every human player has voted
                    all_voted = len(clients_in) > 0 and all(
                        self.socket_player_ids.get(c, (None, None))[1] in votes
                        for c in clients_in
                    )
                    if all_voted:
                        winner = Counter(votes.values()).most_common(1)[0][0]
                        start_msg = f"[StartGame]:{winner}"
                        for c in clients_in:
                            self._send(c, start_msg)
                        self.sessions_map_votes.pop(session_name, None)
                        print_success(
                            f"StartGame envoyé: map {winner} pour {session_name}"
                        )
            except Exception as e:
                print_error(f"Erreur ChooseMap: {e}")

        elif data.startswith("[UnchooseMap]:"):
            try:
                if client_socket in self.socket_player_ids:
                    session_name, player_id = self.socket_player_ids[client_socket]
                    if session_name in self.sessions_map_votes:
                        self.sessions_map_votes[session_name].pop(player_id, None)
                    votes = self.sessions_map_votes.get(session_name, {})
                    vote_msg = f"[MapVotesUpdate]:{json.dumps(votes)}"
                    with self.sessions_lock:
                        clients_in = list(
                            self.sessions_clients_joined.get(session_name, [])
                        )
                    for c in clients_in:
                        self._send(c, vote_msg)
            except Exception as e:
                print_error(f"Erreur UnchooseMap: {e}")

        elif data.startswith("[DeleteSession]:"):
            session_name = data.split(":", 1)[1]

            with self.sessions_lock:
                clients_in_session = list(
                    self.sessions_clients_joined.get(session_name, [])
                )

            # broadcast for all clients in the session
            for client in clients_in_session:
                if client != client_socket:
                    try:
                        self._send(client, f"[SessionDeleted]:{session_name}")
                    except Exception:
                        pass

            # Supprimer la session
            with self.sessions_lock:
                self.sessions = [s for s in self.sessions if s["titre"] != session_name]
                self.sessions_clients_joined.pop(session_name, None)
                self.sessions_characters.pop(session_name, None)
                self.sessions_map_votes.pop(session_name, None)
                with self.game_states_lock:
                    self.game_states.pop(session_name, None)

            print_success(f"Session supprimée : {session_name}")
            self.broadcast_sessions()

        elif data.startswith("[ProjectileSpawned]:"):
            self.broadcast_except(data, exclude_socket=client_socket)

        elif data.startswith("[BubbleHit]:"):
            self.broadcast_except(data, exclude_socket=client_socket)

    # GAME STATE BROADCAST

    def _broadcast_game_state(self, sessionName):
        with self.game_states_lock:
            e = dict(self.game_states.get(sessionName, {}))

        p = {"session": sessionName, "entities": e}
        message = f"[GameState]:{json.dumps(p)}"

        with self.sessions_lock:
            clients_in_session = list(self.sessions_clients_joined.get(sessionName, []))

        for client in clients_in_session:
            try:
                self._send(client, message)
            except Exception as e:
                print_error(f"Erreur broadcast GameState a client: {e}")

    # SESSION MANAGEMENT

    def broadcast_sessions(self):
        # send the session's list to all clients
        try:
            with self.sessions_lock:
                message = f"[SessionsList]:{json.dumps(self.sessions)}"

            for client in list(self.clients):
                try:
                    self._send(client, message)
                except (BrokenPipeError, OSError):
                    pass  # _send already called _remove_dead_client

        except Exception as e:
            print_error(f"Erreur broadcast sessions: {e}")

    # GAME STATE MANAGEMENT

    def start_game(self):
        start_message = "[GameStart]: the game begin!!!!!"
        self.broadcast_except(start_message)
        print_success(f"Le jeu a démarré avec {len(self.clients)} joueurs.")

    # SERVER SHUTDOWN

    def stop_server(self):
        for client in self.clients:
            client.close()
        self.server_socket.close()
        print_success("Serveur arrêté.")
