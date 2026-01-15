"""
MAIN GAME MODULE - Main entry point for the multiplayer game

This module handles:
- Game initialization and window setup
- Main game loop and state management (menu/game)
- Player movement and animation
- Network communication with server
- Game shutdown and resource cleanup

Main Flow:
1. Initialize Game class with display settings
2. Load menu system and game assets
3. Connect to server and start communication threads
4. Run main game loop handling events and rendering
5. Properly shutdown on exit

Recommendations:
1. Consider separating game logic from rendering into different methods
2. Implement proper state machine pattern for game states
3. Add event handler method to reduce code duplication
4. Consider using a constants file for magic numbers (window size, host, port)
"""

import os
import queue
import socket
import threading
import time

import pygame as pyg

import game.characters as player_module
import ui.menu as menu
from game.map_laoder import MapLoader
from ui.console import (
    print_error,
    print_info,
    print_network,
    print_success,
    print_warning,
)
from ui.server import Serveur





class Game:
    """
    Main game class handling window, game loop, and server communication.
    
    Attributes:
        width (int): Window width in pixels
        height (int): Window height in pixels
        fullscreen (bool): Enable fullscreen mode
        screen (pygame.Surface): Main display surface
        player (Character): Current player character instance
        etat (str): Current game state ('menu' or 'game')
        running (bool): Game loop running flag
    """

    def __init__(self, width=1280, height=720, fullscreen=False):
        """
        Initialize game window, assets, and network configuration.
        
        Args:
            width (int): Window width (default 1280)
            height (int): Window height (default 720)
            fullscreen (bool): Enable fullscreen (default False)
        """
        
        # ====================================================================
        # WINDOW CONFIGURATION
        # ====================================================================
        self.width = width
        self.height = height
        self.fullscreen = fullscreen

        # ====================================================================
        # GAME STATE VARIABLES
        # ====================================================================
        self.etat = "menu"  # Current state: "menu" or "game"
        self.game_started = False  # Flag for menu launch
        
        # ====================================================================
        # LOAD MENU SYSTEM (Reuse display and resources)
        # ====================================================================
        self.Menu = menu.Menu(
            width=self.width,
            height=self.height,
            fullscreen=self.fullscreen
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

        # ====================================================================
        # LOAD GAME MAP
        # ====================================================================
        map_loader = MapLoader(None)
        background, foreground = map_loader.load_map()
        self.map_back = pyg.transform.scale(background, (self.width, self.height))
        self.map_front = pyg.transform.scale(foreground, (self.width, self.height))

        # ====================================================================
        # LOAD PLAYER CHARACTER
        # ====================================================================
        self.player = player_module.Water()
        self.running = False

        # ====================================================================
        # NETWORK CONFIGURATION
        # ====================================================================
        self.host = "127.0.0.1"
        self.port = 12345
        self._client_socket = None
        self._client_lock = threading.Lock()
        self._send_queue = queue.Queue()

    # ========================================================================
    # TEXT RENDERING METHODS
    # ========================================================================

    def draw_text(self, text, font, text_col, x, y):
        """
        Render text at specified position.
        
        Args:
            text (str): Text to render
            font (pygame.font.Font): Font to use
            text_col (tuple): RGB color tuple
            x (int): X coordinate
            y (int): Y coordinate
        """
        img = font.render(text, True, text_col)
        self.screen.blit(img, (x, y))

    def draw_text_center(self, text, font, text_col, y):
        """
        Render text centered horizontally at vertical position y.
        
        Args:
            text (str): Text to render
            font (pygame.font.Font): Font to use
            text_col (tuple): RGB color tuple
            y (int): Y coordinate
        """
        img = font.render(text, True, text_col)
        x = (self.width - img.get_width()) // 2
        self.screen.blit(img, (x, y))

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def center_x(self, image, scale=1):
        """
        Calculate X coordinate to center image horizontally on screen.
        
        Args:
            image (pygame.Surface): Image to center
            scale (float): Scale factor (default 1)
            
        Returns:
            int: Centered X coordinate
        """
        w = int(image.get_width() * scale)
        return (self.width - w) // 2

    # ========================================================================
    # NETWORK COMMUNICATION METHODS
    # ========================================================================

    def _connect_to_server(self):
        """
        Establish persistent connection to game server.
        Starts background threads for message sending and receiving.
        """
        try:
            # Close existing socket if any
            if self._client_socket:
                try:
                    self._client_socket.close()
                except:
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
        """
        Background thread handling incoming messages from server.
        Automatically reconnects on connection loss.
        """
        while self.running:
            if not self._client_socket:
                time.sleep(0.5)
                continue
            try:
                data = self._client_socket.recv(1024)
                if not data:
                    print_warning("Connexion fermée par le serveur")
                    # Trigger reconnection
                    try:
                        self._client_socket.close()
                    except Exception:
                        pass
                    self._client_socket = None
                    if self.running:
                        time.sleep(1.0)
                        self._connect_to_server()
                    break
                print_network(f"Message reçu: {data.decode('utf-8')}")
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
        """
        Background thread handling outgoing messages to server.
        Automatically reconnects on connection loss.
        """
        while self.running:
            try:
                message = self._send_queue.get(timeout=0.5)
            except queue.Empty:
                continue
            try:
                if self._client_socket:
                    self._client_socket.send(message.encode("utf-8"))
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
        """
        Queue a message for sending to server.
        
        Args:
            message (str): Message to send (default "Bonjour serveur")
        """
        self._send_queue.put(message)

    # ========================================================================
    # GAME STATE MANAGEMENT
    # ========================================================================

    def shutdown(self):
        """
        Gracefully shutdown game:
        - Stop network communication
        - Close socket connection
        - Quit pygame
        """
        print_info("Arrêt du jeu : fermeture connexion et threads")
        self.running = False
        
        # Close client socket safely
        with self._client_lock:
            try:
                if self._client_socket:
                    self._client_socket.shutdown(socket.SHUT_RDWR)
                    self._client_socket.close()
            except Exception:
                pass
            self._client_socket = None

        # Clear message queue
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

    # ========================================================================
    # GAME UPDATE AND RENDERING
    # ========================================================================

    def update(self):
        """
        Update game state each frame.
        Called during main game loop.
        """
        self.player.update()

    # ========================================================================
    # MAIN GAME LOOP
    # ========================================================================

    def run(self):
        """
        Main game loop:
        1. Initialize running state and connect to server
        2. Handle events (menu navigation, quit)
        3. Update and render based on current game state
        4. Shutdown properly on exit
        """
        # Initialize and connect to server
        self.running = True
        self._connect_to_server()

        screen = self.screen

        # ====================================================================
        # Temporary variables (for tests)
        # ====================================================================
        #self.etat = "game"  # Start directly in game for testing

        while self.running:
            # ================================================================
            # MENU STATE
            # ================================================================
            if self.etat == "menu":
                screen.blit(self.wallpaper, (0, 0))
                
                if self.game_started:
                    # Main menu display
                    self.Menu.method_menu()
                    # Check if menu state changed to game
                    if self.Menu.etat == "game":
                        self.etat = "game"
                else:
                    self.game_started = True

                # Handle menu events
                for event in pyg.event.get():
                    if event.type == pyg.QUIT:
                        self.running = False

                pyg.display.update()
                
            # ================================================================
            # GAME STATE - Actual gameplay
            # ================================================================
            if self.etat == "game":
                # Event handling
                for event in pyg.event.get():
                    if event.type == pyg.QUIT:
                        self.running = False
                    elif event.type == pyg.KEYDOWN:
                        if event.key == pyg.K_ESCAPE:
                            self.running = False
                            self.send_to_server(message="ESC appuyé")

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

                # Handle player movement
                if keys_pressed[pyg.K_UP]:
                    self.player.move("up")
                if keys_pressed[pyg.K_DOWN]:
                    self.player.move("down")
                if keys_pressed[pyg.K_LEFT]:
                    self.player.move("left")
                if keys_pressed[pyg.K_RIGHT]:
                    self.player.move("right")

                # Update player animation
                self.player.update_animation(delta_time, is_moving)

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

                # Update display
                pyg.display.update()
                pyg.display.flip()

        # Graceful shutdown
        self.shutdown()


if __name__ == "__main__":
    """
    Game entry point:
    1. Create Game instance with display configuration
    2. Start game loop
    """
    # Initialize and run game with fullscreen enabled
    game = Game(width=1280, height=720, fullscreen=True)
    game.run()
