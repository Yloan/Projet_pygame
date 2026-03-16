import json
import socket
import threading

from ui.console import (
    print_debug,
    print_error,
    print_event,
    print_info,
    print_network,
    print_success,
    print_warning,
)

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 12345
MAX_CLIENTS = 2

MESSAGE_BUFFER_SIZE = 4096
MSG_DELIMITER = "\n"


class Serveur:
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):

        self.Port = port
        self.Host = host
        # CONNECTION MANAGMENT
        self.clients = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.Host, self.Port))
        # GLOBALS VARIABLES
        self.sessions = []
        self.sessions_lock = threading.Lock()
        self.sessions_clients_joined = {}

        self.recv_buffers = {}
        self.sessions_characters = {}
        self.socket_player_ids = {}

    def start_server(self):
        self.server_socket.listen(MAX_CLIENTS)
        print_success(f"Serveur démarré sur {self.Host}:{self.Port}")
        accept_thread = threading.Thread(target=self.accept_clients, daemon=True)
        accept_thread.start()

    def accept_clients(self):
        while True:
            try:
                client_socket, addr = self.server_socket.accept()
                print_event(f"Client connecté depuis {addr}")

                self.clients.append(client_socket)
                self.recv_buffers[client_socket] = ""

                threading.Thread(
                    target=self.handle_client, args=(client_socket,), daemon=True
                ).start()

                self.broadcast_sessions()
                # self.start_game()

            except Exception as e:
                print_error(f"Erreur lors de l'acceptation d'un client: {e}")

    def _send(self, client_socket, message):
        try:
            client_socket.send((message + MSG_DELIMITER).encode("utf-8"))
        except Exception as e:
            print_error(f"Erreur envoi: {e}")

    def broadcast_raw(self, message, exclude_socket=None):
        """Diffuse un message brut à tous les clients (sauf exclude_socket)"""
        for client in self.clients:
            if client != exclude_socket:
                self._send(client, message)

    def handle_client(self, client_socket):
        while True:
            try:
                chunk = client_socket.recv(MESSAGE_BUFFER_SIZE).decode("utf-8")
                if not chunk:
                    break

                self.recv_buffers[client_socket] += chunk
                messages = self.recv_buffers[client_socket].split(MSG_DELIMITER)

                self.recv_buffers[client_socket] = messages[-1]
                complete_messages = messages[:-1]

                for data in complete_messages:
                    if not data:
                        continue
                    print_network(f"Reçu du client: {data}")
                    self._handle_message(data, client_socket)

            except Exception as e:
                print_error(f"Erreur lors de la réception: {e}")
                break

        try:
            client_socket.close()
        except:
            pass
        if client_socket in self.clients:
            self.clients.remove(client_socket)
        self.recv_buffers.pop(client_socket, None)
        print_error("Client déconnecté")

    def _handle_message(self, data, client_socket):

        if data.startswith("[Sessions]"):
            try:
                json_str = data.split(":", 1)[1]
                session_data = json.loads(json_str)
                with self.sessions_lock:
                    session_data["id"] = len(self.sessions)
                    self.sessions.append(session_data)
                    print_success(
                        f"Session créée: {session_data.get('titre', 'Sans titre')}"
                    )
                self.broadcast_sessions()
            except json.JSONDecodeError as e:
                print_error(f"Erreur JSON: {e}")
            except Exception as e:
                print_error(f"Erreur session: {e}")

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

                    current_players = len(self.sessions_clients_joined[session_name])

                    if current_players < max_humans:
                        self.sessions_clients_joined[session_name].append(client_socket)
                        for s in self.sessions:
                            if s["titre"] == session_name:
                                s["nb_players"] = s.get("nb_players", 0) + 1
                                break
                        player_id = current_players + 1

                        self.socket_player_ids[client_socket] = (
                            session_name,
                            player_id,
                        )
                        self._send(client_socket, f"[YourPlayerID]:{player_id}")
                        print_success(
                            f"Joueur assigné ID {player_id} dans {session_name} (Bots: {nb_bots})"
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
                        self._send(client_socket, "[Error]:Session pleine")
                        print_warning(
                            f"Session {session_name} pleine, connexion refusée pour ce joueur."
                        )

            self.broadcast_sessions()

        elif data.startswith("[CharacterUpdate]:"):
            try:
                update = json.loads(data.split(":", 1)[1])
                session_name = update.get("session_name")
                player_id = update.get("player_id")
                if session_name and player_id:
                    if session_name not in self.sessions_characters:
                        self.sessions_characters[session_name] = {}
                    self.sessions_characters[session_name][player_id] = [
                        update.get("character_1"),
                        update.get("character_2"),
                        update.get("character_3"),
                    ]
            except Exception as e:
                print_error(f"Erreur stockage CharacterUpdate: {e}")
            self.broadcast_raw(data, exclude_socket=client_socket)
            print_network("CharacterUpdate diffusé")

        elif data.startswith("[PlayerUnready]:"):
            self.broadcast_raw(data, exclude_socket=client_socket)
            print_network("PlayerUnready diffusé")
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
                    # Prévenir les autres que ce slot est vide
                    self.broadcast_raw(
                        f"[PlayerLeft]:{left_pid}", exclude_socket=client_socket
                    )

            self.broadcast_sessions()

        elif data.startswith("[PlayerReady]:"):
            self.broadcast_raw(data, exclude_socket=client_socket)
            print_network("PlayerReady diffusé")

    # SESSION MANAGEMENT

    def broadcast_sessions(self):
        """Envoie la liste des sessions à jour à TOUS les clients connectés."""
        try:
            with self.sessions_lock:
                message = f"[SessionsList]:{json.dumps(self.sessions)}"

            for client in list(self.clients):
                try:
                    self._send(client, message)
                except Exception as e:
                    print_error(f"Erreur envoi sessions: {e}")
                    try:
                        client.close()
                    except:
                        pass
                    if client in self.clients:
                        self.clients.remove(client)
        except Exception as e:
            print_error(f"Erreur broadcast sessions: {e}")

    # GAME STATE MANAGEMENT

    def start_game(self):
        start_message = "[GameStart]:Le jeu commence maintenant!"
        self.broadcast_raw(start_message)
        print_success(f"Le jeu a démarré avec {len(self.clients)} joueurs.")

    # SERVER SHUTDOWN

    def stop_server(self):
        print_info("Arrêt du serveur...")
        for client in self.clients:
            try:
                client.close()
            except:
                pass
        try:
            self.server_socket.close()
        except:
            pass
        print_success("Serveur arrêté.")
