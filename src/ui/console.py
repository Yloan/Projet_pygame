import colorama
from colorama import Fore, Style

colorama.init()

def print_info(message):
    print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} {message}")

def print_error(message):
    print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {message}")

def print_success(message):
    print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} {message}")

def print_warning(message):
    print(f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL} {message}")

def print_debug(message):
    print(f"{Fore.MAGENTA}[DEBUG]{Style.RESET_ALL} {message}")

def print_event(message):
    print(f"{Fore.BLUE}[EVENT]{Style.RESET_ALL} {message}")

def print_network(message):
    print(f"{Fore.LIGHTCYAN_EX}[NETWORK]{Style.RESET_ALL} {message}")

__all__ = [
    'print_info', 'print_error', 'print_success', 'print_warning',
    'print_debug', 'print_event', 'print_network'
]
