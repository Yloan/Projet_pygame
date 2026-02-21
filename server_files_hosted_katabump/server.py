"""
SERVER MODULE - Multiplayer game server implementation

This module provides the server for multiplayer game coordination:
- Client connection management
- Message broadcasting between clients
- Game state synchronization
- Player connection/disconnection handling

Current Features:
- Accepts up to 2 clients
- Broadcasts messages to all connected clients except sender
- Notifies clients when game starts

Recommendations:
1. Implement proper message protocol (JSON/binary format)
2. Add player state synchronization
3. Implement game state management on server
4. Add player authentication/lobbies
5. Implement graceful client disconnection handling
6. Add error recovery and reconnection support
7. Implement player timeout detection
"""

import socket
import threading

from console import (
    print_debug,
    print_error,
    print_event,
    print_info,
    print_network,
    print_success,
    print_warning,
)

# ============================================================================
# CONSTANTS - Server configuration
# ============================================================================
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 12345
MAX_CLIENTS = 2
MESSAGE_BUFFER_SIZE = 1024


class Serveur:
    """
    Game server for managing multiplayer connections and communications.

    Attributes:
        Port (int): Server port number
        Host (str): Server host address
        clients (list): List of connected client sockets
        server_socket (socket.socket): Main server socket
    """

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        """
        Initialize game server.

        Args:
            host (str): Server address (default 127.0.0.1)
            port (int): Server port (default 12345)
        """

        # ====================================================================
        # SERVER CONFIGURATION
        # ====================================================================
        self.Port = port
        self.Host = host

        # ====================================================================
        # CONNECTION MANAGEMENT
        # ====================================================================
        self.clients = []  # List of connected client sockets

        # ====================================================================
        # SERVER SOCKET SETUP
        # ====================================================================
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.Host, self.Port))

    # ========================================================================
    # SERVER LIFECYCLE METHODS
    # ========================================================================

    def start_server(self):
        """
        Start server and begin accepting client connections.
        Listens for incoming connections in a background thread.
        """
        self.server_socket.listen(MAX_CLIENTS)
        print_success(f"Serveur démarré sur {self.Host}:{self.Port}")

        # Start accepting clients in background thread
        accept_thread = threading.Thread(target=self.accept_clients, daemon=True)
        accept_thread.start()

    # ========================================================================
    # CLIENT CONNECTION HANDLING
    # ========================================================================

    def accept_clients(self):
        """
        Accept incoming client connections.
        Runs in background thread continuously listening for new clients.
        """
        while True:
            try:
                # Accept new client connection
                client_socket, addr = self.server_socket.accept()
                print_event(f"Client connecté depuis {addr}")

                # Add to client list
                self.clients.append(client_socket)

                # Handle client in separate thread
                threading.Thread(
                    target=self.handle_client, args=(client_socket,), daemon=True
                ).start()

                # Notify other clients of new player
                self.start_game()
            except Exception as e:
                print_error(f"Erreur lors de l'acceptation d'un client: {e}")

    def handle_client(self, client_socket):
        """
        Handle communication with individual client.
        Receives messages from client and broadcasts to others.

        Args:
            client_socket (socket.socket): Connected client socket
        """
        while True:
            try:
                # Receive message from client
                data = client_socket.recv(MESSAGE_BUFFER_SIZE).decode("utf-8")

                if data:
                    print_network(f"Reçu du client: {data}")
                    # Broadcast message to other clients
                    self.broadcast(data, client_socket)
                else:
                    # Empty data means client disconnected
                    break
            except Exception as e:
                print_error(f"Erreur lors de la réception: {e}")
                break

        # Cleanup after client disconnects
        try:
            client_socket.close()
        except:
            pass

        if client_socket in self.clients:
            self.clients.remove(client_socket)

        print_error("Client déconnecté")

    # ========================================================================
    # MESSAGE BROADCASTING
    # ========================================================================

    def broadcast(self, message, sender_socket):
        """
        Broadcast message to all clients except sender.

        Args:
            message (str): Message to broadcast
            sender_socket (socket.socket): Socket of sending client (excluded from broadcast)
        """
        for client in self.clients:
            if client != sender_socket:
                try:
                    client.send(message.encode("utf-8"))
                except Exception as e:
                    print_error(f"Erreur lors de l'envoi du message: {e}")
                    if client in self.clients:
                        try:
                            client.close()
                        except:
                            pass
                        self.clients.remove(client)

    # ========================================================================
    # GAME STATE MANAGEMENT
    # ========================================================================

    def start_game(self):
        """
        Notify all clients that game has started.
        Called when appropriate number of players are connected.
        """
        start_message = "Le jeu commence maintenant!"
        self.broadcast(start_message, None)
        print_success(f"Le jeu a démarré avec {len(self.clients)} joueurs.")

    # ========================================================================
    # SERVER SHUTDOWN
    # ========================================================================

    def stop_server(self):
        """
        Gracefully shutdown server and close all connections.
        """
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
