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
MESSAGE_BUFFER_SIZE = 1024


class Serveur:

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):

        self.Port = port
        self.Host = host
        # CONNECTION MANAGEMENT
        self.clients = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.Host, self.Port))
        # GLOBALS VARIABLES
        self.sessions = []
        self.sessions_lock = threading.Lock()

        self.sessions_clients_joined = {}

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

                # Add to client list
                self.clients.append(client_socket)
                threading.Thread(
                    target=self.handle_client, args=(client_socket,), daemon=True
                ).start()
                self.start_game()
            except Exception as e:
                print_error(f"Erreur lors de l'acceptation d'un client: {e}")
        
    def broadcast_raw(self, message, exclude_socket=None):
        for client in self.clients:
            if client != exclude_socket:
                try:
                    client.send(message.encode("utf-8"))
                except Exception as e:
                    print_error(f"Erreur broadcast_raw: {e}")

    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(MESSAGE_BUFFER_SIZE).decode("utf-8")
                if data:
                    print_network(f"Reçu du client: {data}")
                    self.broadcast(data, client_socket)

                    # Handle messages
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

                            # Envoyer la liste complète à tous
                            self.broadcast_sessions()
                        except json.JSONDecodeError as e:
                            print_error(f"Erreur JSON: {e}")
                        except Exception as e:
                            print_error(f"Erreur session: {e}")

                    if data.startswith("[CreateSession]:"):
                        new_session_data = json.loads(data.split(":", 1)[1])
                        with self.sessions_lock:
                            self.sessions.append(new_session_data)
                            self.sessions_clients_joined[new_session_data["titre"]] = []
                        self.broadcast_sessions()  # On prévient tout le monde

                    if data.startswith("[JoinedSession]:"):
                        session_name = data.split(":", 1)[1]

                        # Trouver les infos de la session pour connaître le nombre de bots
                        session_info = next(
                            (s for s in self.sessions if s["titre"] == session_name),
                            None,
                        )

                        if session_info:
                            # Calcul du nombre max de joueurs humains
                            nb_bots = session_info.get("nb_bots", 0)
                            max_humans = 4 - nb_bots

                            with self.sessions_lock:
                                if session_name not in self.sessions_clients_joined:
                                    self.sessions_clients_joined[session_name] = []

                                current_players = len(
                                    self.sessions_clients_joined[session_name]
                                )

                                # Vérifier s'il reste de la place
                                if current_players < max_humans:
                                    self.sessions_clients_joined[session_name].append(
                                        client_socket
                                    )
                                    for s in self.sessions:
                                        if s["titre"] == session_name:
                                            s["nb_players"] = s.get("nb_players", 0) + 1
                                            break

                                    player_id = (
                                        current_players + 1
                                    )  # Donne 1, 2, 3 ou 4

                                    # On prévient le client de son numéro
                                    client_socket.send(
                                        f"[YourPlayerID]:{player_id}".encode("utf-8")
                                    )
                                    print_success(
                                        f"Joueur assigné ID {player_id} dans {session_name} (Bots: {nb_bots})"
                                    )
                                else:
                                    # La session est pleine (pour les humains)
                                    client_socket.send(b"[Error]:Session pleine")
                                    print_warning(
                                        f"Session {session_name} pleine, connexion refusée pour ce joueur."
                                    )
                        self.broadcast_sessions()
                    if data.startswith("[CharacterUpdate]:"):
                        try:
                            self.broadcast_raw(data, exclude_socket=client_socket)
                            print_network("CharacterUpdate diffusé")
                        except Exception as e:
                            print_error(f"Erreur broadcast CharacterUpdate: {e}")

                    if data.startswith("[LeaveSession]:"):
                        session_name = data.split(":", 1)[1]
                        with self.sessions_lock:
                            if session_name in self.sessions_clients_joined:
                                if client_socket in self.sessions_clients_joined[session_name]:
                                    self.sessions_clients_joined[session_name].remove(client_socket)
                            for s in self.sessions:
                                if s["titre"] == session_name:
                                    s["nb_players"] = max(0, s.get("nb_players", 1) - 1)
                                    break
                        self.broadcast_sessions()
                        
                    if data.startswith("[PlayerReady]:"):
                        try:
                            self.broadcast_raw(data, exclude_socket=client_socket)
                            print_network("PlayerReady diffusé")
                        except Exception as e:
                            print_error(f"Erreur broadcast PlayerReady: {e}")

                else:
                    break
            except Exception as e:
                print_error(f"Erreur lors de la réception: {e}")
                break
        try:
            client_socket.close()
        except:
            pass
        if client_socket in self.clients:
            self.clients.remove(client_socket)
        print_error("Client déconnecté")

    def broadcast(self, message, sender_socket):
        with self.sessions_lock:
            sessions_json = json.dumps(self.sessions)
            message = f"[SessionsList]:{sessions_json}"
            for client in self.clients:
                try:
                    client.send(message.encode("utf-8"))
                except:
                    pass

    # SESSION MANAGEMENT

    def broadcast_sessions(self):
        """Envoie la liste des sessions à tous les clients"""
        try:
            with self.sessions_lock:
                message = f"[SessionsList]:{json.dumps(self.sessions)}"

            for client in self.clients:
                try:
                    client.send(message.encode("utf-8"))
                except Exception as e:
                    print_error(f"Erreur envoi sessions: {e}")
                    if client in self.clients:
                        try:
                            client.close()
                        except:
                            pass
                        self.clients.remove(client)
        except Exception as e:
            print_error(f"Erreur broadcast sessions: {e}")

    # GAME STATE MANAGEMENT

    def start_game(self):
        start_message = "Le jeu commence maintenant!"
        self.broadcast(start_message, None)
        print_success(f"Le jeu a démarré avec {len(self.clients)} joueurs.")

    # SERVER SHUTDOWN

    def stop_server(self):
        print_info("Arrêt du serveur...")

        # Close all client connections
        for client in self.clients:
            try:
                client.close()
            except:
                pass

        # Close server socket
        try:
            self.server_socket.close()
        except:
            pass

        print_success("Serveur arrêté.")
