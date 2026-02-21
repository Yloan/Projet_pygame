"""
CONSOLE MODULE - Color-coded console output system

This module provides colored console output functions for different message types:
- INFO: General information (cyan)
- ERROR: Error messages (red)
- SUCCESS: Successful operations (green)
- WARNING: Warning messages (yellow)
- DEBUG: Debug information (magenta)
- EVENT: Game events (blue)
- NETWORK: Network communication (light cyan)

Uses colorama library for cross-platform color support.

Example:
    from ui.console import print_success, print_error
    print_success("Game started!")
    print_error("Connection failed!")
"""

import colorama
from colorama import Fore, Style

# Initialize colorama for cross-platform color support
colorama.init()


# ============================================================================
# COLORED CONSOLE OUTPUT FUNCTIONS
# ============================================================================


def print_info(message):
    """
    Print informational message in cyan.

    Args:
        message (str): Message to print
    """
    print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} {message}")


def print_error(message):
    """
    Print error message in red.

    Args:
        message (str): Error message to print
    """
    print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {message}")


def print_success(message):
    """
    Print success message in green.

    Args:
        message (str): Success message to print
    """
    print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} {message}")


def print_warning(message):
    """
    Print warning message in yellow.

    Args:
        message (str): Warning message to print
    """
    print(f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL} {message}")


def print_debug(message):
    """
    Print debug message in magenta.

    Args:
        message (str): Debug message to print
    """
    print(f"{Fore.MAGENTA}[DEBUG]{Style.RESET_ALL} {message}")


def print_event(message):
    """
    Print game event message in blue.

    Args:
        message (str): Event message to print
    """
    print(f"{Fore.BLUE}[EVENT]{Style.RESET_ALL} {message}")


def print_network(message):
    """
    Print network communication message in light cyan.

    Args:
        message (str): Network message to print
    """
    print(f"{Fore.LIGHTCYAN_EX}[NETWORK]{Style.RESET_ALL} {message}")


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    "print_info",
    "print_error",
    "print_success",
    "print_warning",
    "print_debug",
    "print_event",
    "print_network",
]
