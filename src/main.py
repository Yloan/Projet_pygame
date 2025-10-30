# Point d'entrée du jeu : boucle principale et envoi d'informations au serveur

import socket
import threading
import queue
import pygame as pyg
from ui.server import Serveur


class Game:
    def __init__(self, width=1280, height=720, fullscreen=False, start_local_server=True):
        # Démarrage du serveur local par défaut
        if start_local_server:
            self.server = Serveur()
            self.server.start_server()
            print("Serveur local démarr�sur le port :12345")

        self.width = width
        self.height = height
        self.fullscreen = fullscreen

        pyg.init()
        flags = pyg.FULLSCREEN if self.fullscreen else 0
        self.screen = pyg.display.set_mode((self.width, self.height), flags)
        pyg.display.set_caption("Jeu Multijoueur")
        self.clock = pyg.time.Clock()
        self.running = False

        # Configuration réseau
        self.host = '192.168.1.244'
        self.port = 12345
        self._client_socket = None
        self._client_lock = threading.Lock()
        self._send_queue = queue.Queue()
        self._connect_to_server()

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
            print(f"Connecté au serveur {self.host}:{self.port}")
            
            # Démarrer thread de réception
            threading.Thread(target=self._receive_loop, daemon=True).start()
            # Démarrer thread d'envoi
            threading.Thread(target=self._send_loop, daemon=True).start()
            
        except Exception as e:
            print(f"Erreur de connexion au serveur: {e}")
            self._client_socket = None

    def _receive_loop(self):
        """Thread de réception des messages du serveur."""
        while True:
            if not self._client_socket:
                break
            try:
                data = self._client_socket.recv(1024)
                if not data:
                    break
                print('Message reçu:', data.decode('utf-8'))
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Erreur réception: {e}")
                break
        self._connect_to_server()  # Tente de se reconnecter

    def _send_loop(self):
        """Thread d'envoi des messages au serveur."""
        while True:
            try:
                message = self._send_queue.get()
                if self._client_socket:
                    self._client_socket.send(message.encode('utf-8'))
                else:
                    print("Non connecté, message non envoyé:", message)
                    self._connect_to_server()
            except Exception as e:
                print(f"Erreur envoi: {e}")
                self._connect_to_server()

    def send_to_server(self, message='Bonjour serveur'):
        """Ajoute un message à la file d'envoi."""
        self._send_queue.put(message)

    def run(self):
        self.running = True
        while self.running:
            for event in pyg.event.get():
                if event.type == pyg.QUIT:
                    self.running = False
                elif event.type == pyg.KEYDOWN:
                    if event.key == pyg.K_ESCAPE:
                        self.running = False
                    elif event.key == pyg.K_e:
                        self.send_to_server(message='E appuyé')

            # Update game logic ici

            # Draw (nettoyage)
            self.screen.fill((0, 0, 0))

            font = pyg.font.SysFont(None, 24)
            txt = font.render('E pour envoyer un message au serveur. Esc pour quitter.', True, (255, 255, 255))
            self.screen.blit(txt, (20, 20))

            pyg.display.flip()
            self.clock.tick(60)


if __name__ == '__main__':
    # Démarrage du serveur local et du jeu
    game = Game(width=1280, height=720, fullscreen=False, start_local_server=True)
    game.run()


