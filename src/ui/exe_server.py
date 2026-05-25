import os
import sys
import time

from console import (
    print_debug,
    print_error,
    print_info,
    print_network,
    print_success,
    print_warning,
)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server import Serveur


def run_offline_server():
    # Initialize the server on localhost with the port given by blitzkrieg
    server = Serveur(host="0.0.0.0", port=20142)

    # Start the server
    server.start_server()

    print_success(">> Server is now listening for BLITZKRIEG connections.")
    print_info("Press Ctrl+C to shut down the server.")

    try:
        while 1:
            count = len(server.clients)
            if count > 0:
                print_info(f"Status: {count} client(s) connected.")
                print_info(f"Sessions: {server.sessions}")
                for session in server.sessions_clients_joined.items():
                    if session[1] != []:
                        print_info(f"{session[0]}:{session[1]}")
            time.sleep(5)

    except KeyboardInterrupt:
        server.stop_server()
        print_info("Server closed.")


if __name__ == "__main__":
    run_offline_server()
