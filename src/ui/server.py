import socket
import threading
from ui.console import (
    print_info,
    print_error,
    print_success,
    print_warning,
    print_debug,
    print_event,
    print_network,
)


class Serveur:
    def __init__(self):
        self.Port = 12345
        self.Host = '127.0.0.1'

        self.clients = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.Host, self.Port))

    def start_server(self):
        self.server_socket.listen(2)
        print_success(f"Serveur démarré sur {self.Host}:{self.Port}")
        accept_thread = threading.Thread(target=self.accept_clients)
        accept_thread.start()
        
    def accept_clients(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            print_event(f"Client connecté depuis {addr}")
            self.clients.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()
            self.start_game()
        
    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if data:
                    print_network(f"Reçu du client: {data}")
                    self.broadcast(data, client_socket)
                else:
                    break
            except:
                break
        client_socket.close()
        self.clients.remove(client_socket)
        print_error("Client déconnecté")
    
    def broadcast(self, message, sender_socket):
        for client in self.clients:
            if client != sender_socket:
                try:
                    client.send(message.encode('utf-8'))
                except:
                    client.close()
                    self.clients.remove(client)

    def start_game(self):
        start_message = "Le jeu commence maintenant!"
        self.broadcast(start_message, None)
        print_success(f"Le jeu a démarré avec {len(self.clients)} joueurs.")



