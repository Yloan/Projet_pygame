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
    # 1. Initialize the server on localhost
    server = Serveur(host="0.0.0.0", port=20001)

    # 2. Start the server (this starts the accept_clients thread automatically)
    server.start_server()

    print_success(">>> Server is now listening for Katabump connections.")
    print_info("Press Ctrl+C to shut down the server.")

    try:
        # 3. Keep the main thread alive
        while True:
            # Periodically check client count
            count = len(server.clients)
            if count > 0:
                print_info(f"Status: {count} client(s) connected.")
            time.sleep(10)  # Check every 10 seconds

    except KeyboardInterrupt:
        server.stop_server()
        print_info("Server closed by user.")


if __name__ == "__main__":
    run_offline_server()
