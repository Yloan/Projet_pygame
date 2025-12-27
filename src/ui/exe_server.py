import os
import sys

from console import (
    print_debug,
    # print_error,
    # print_info,
    # print_network,
    # print_success,
    # print_warning,
)

# Ensure project root is on sys.path so `ui` package imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ui.server import Serveur

server = Serveur()
server.start_server()
for client in server.clients:
    server.handle_client(client)
    print_debug("Handling client in exe_server")

server.accept_clients()
server.broadcast("Test message", None)
