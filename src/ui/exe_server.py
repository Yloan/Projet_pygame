import os
import sys

from console import (
    print_debug,
    print_error,
    print_info,
    print_network,
    print_success,
    print_warning,
)
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ui.server import Serveur

def run_offline_server():
    # Initialize the server on localhost
    server = Serveur(host='127.0.0.1', port=12345)
    
    # Start the server (this starts the accept_clients thread automatically)
    server.start_server()
    
    print_success(">>> Server is now listening for Katabump connections.")
    print_info("Press Ctrl+C to shut down the server.")

    try:
        # Keep the main thread alive
        while True:
            # Periodically check client count
            count = len(server.clients)
            if count > 0:
                print_info(f"Status: {count} client(s) connected.")
            time.sleep(10) # Check every 10 seconds
            
    except KeyboardInterrupt:
        server.stop_server()
        print_info("Server closed by user.")

if __name__ == "__main__":
    run_offline_server()
