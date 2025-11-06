# Point d'entrée du jeu : boucle principale et envoi d'informations au serveur

import socket
import threading
import queue
import time
import pygame as pyg
from ui.server import Serveur
import os


class Game:
    def __init__(self, width=1280, height=720, fullscreen=False):

        # Configuration de la fenêtre
        self.width = width
        self.height = height
        self.fullscreen = fullscreen

        # Maps & ressources
        base_path = os.path.dirname(os.path.abspath('FOREST-BACKGROUND.png'))
        print(f"Base path: {base_path}")

        map_path_back = os.path.join(base_path, 'assets', 'maps', 'FOREST-BACKGROUND.png')
        map_path_fore = os.path.join(base_path, 'assets', 'maps', 'FOREST-FOREGROUND.png')

        sprite_path = os.path.join(base_path, 'assets', 'sprites' , 'FIRE-WALK-Sheet.png')


        self.map_back = pyg.image.load(map_path_back)
        self.map_front = pyg.image.load(map_path_fore)

        self.player_spritesheet = pyg.image.load(sprite_path)

        # Initialisation Pygame
        pyg.init()
        flags = pyg.FULLSCREEN if self.fullscreen else 0
        self.screen = pyg.display.set_mode((self.width, self.height), flags)
        pyg.display.set_caption("Jeu Multijoueur")
        self.clock = pyg.time.Clock()
        self.running = False

        # Configuration réseau
        self.host = '192.168.1.130'
        self.port = 12345
        self._client_socket = None
        self._client_lock = threading.Lock()
        self._send_queue = queue.Queue()
        # Ne pas se connecter automatiquement ici : on démarre la connexion
        # quand la boucle principale démarre (pour permettre un arrêt propre)

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
            
            # Démarrer thread de réception et d'envoi
            threading.Thread(target=self._receive_loop, daemon=True).start()
            threading.Thread(target=self._send_loop, daemon=True).start()
            
        except Exception as e:
            print(f"Erreur de connexion au serveur: {e}")
            self._client_socket = None

    def _receive_loop(self):
        """Thread de réception des messages du serveur."""
        while self.running:
            if not self._client_socket:
                # Attendre un peu avant d'essayer de se reconnecter si on est encore running
                time.sleep(0.5)
                continue
            try:
                data = self._client_socket.recv(1024)
                if not data:
                    print('Connexion fermée par le serveur')
                    # provoquer une reconnexion
                    self._client_socket.close()
                    self._client_socket = None
                    if self.running:
                        time.sleep(1.0)
                        self._connect_to_server()
                    break
                print('Message reçu:', data.decode('utf-8'))
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Erreur réception: {e}")
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
        """Thread d'envoi des messages au serveur."""
        while self.running:
            try:
                # utiliser un timeout pour pouvoir sortir proprement quand on arrête
                message = self._send_queue.get(timeout=0.5)
            except queue.Empty:
                continue
            try:
                if self._client_socket:
                    self._client_socket.send(message.encode('utf-8'))
                else:
                    print("Non connecté, message non envoyé:", message)
                    # remettre le message en file pour tenter plus tard
                    try:
                        self._send_queue.put_nowait(message)
                    except Exception:
                        pass
                    # essayer de se reconnecter
                    if self.running:
                        time.sleep(1.0)
                        self._connect_to_server()
            except Exception as e:
                print(f"Erreur envoi: {e}")
                if self._client_socket:
                    try:
                        self._client_socket.close()
                    except Exception:
                        pass
                self._client_socket = None
                # remettre le message en file
                try:
                    self._send_queue.put_nowait(message)
                except Exception:
                    pass
                if self.running:
                    time.sleep(1.0)
                    self._connect_to_server()

    def send_to_server(self, message='Bonjour serveur'):
        """Ajoute un message à la file d'envoi."""
        self._send_queue.put(message)

    def shutdown(self):
        """Arrête proprement la logique réseau et ferme Pygame."""
        print('Arrêt du jeu : fermeture connexion et threads')
        self.running = False
        # fermer la socket client
        with self._client_lock:
            try:
                if self._client_socket:
                    self._client_socket.shutdown(socket.SHUT_RDWR)
                    self._client_socket.close()
            except Exception:
                pass
            self._client_socket = None
        # vider la file d'envoi
        try:
            while not self._send_queue.empty():
                self._send_queue.get_nowait()
        except Exception:
            pass
        # fermer Pygame
        try:
            pyg.quit()
        except Exception:
            pass

    def run(self):
        # Démarrer le jeu et établir la connexion réseau
        self.running = True
        self._connect_to_server()
        while self.running:
            for event in pyg.event.get():
                if event.type == pyg.QUIT:
                    self.running = False
                elif event.type == pyg.KEYDOWN:
                    if event.key == pyg.K_ESCAPE:
                        self.running = False
                        self.send_to_server(message='ESC appuyé')
                    """elif event.key == pyg.K_e:
                        self.send_to_server(message='E appuyé')"""

            #chargement des assets dans le jeu
            self.screen.blit(self.map_back, (0, 0))



            # Draw (nettoyage)
            self.screen.fill((0, 0, 0))

            """
            font = pyg.font.SysFont(None, 24)
            txt = font.render('E pour envoyer un message au serveur. Esc pour quitter.', True, (255, 255, 255))
            self.screen.blit(txt, (20, 20)) """        

            pyg.display.update()
            pyg.display.flip()
            self.clock.tick(60)

        # Quand la boucle se termine, faire un arrêt propre
        self.shutdown()


if __name__ == '__main__':
    # Démarrage du serveur local et du jeu
    game = Game(width=1280, height=720, fullscreen=False)
    game.run()
