import os
import sys

# Ensure project root is on sys.path so `ui` package imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.server import Serveur

server = Serveur()
server.start_server()