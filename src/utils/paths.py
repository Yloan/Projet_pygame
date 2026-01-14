"""
PATHS MODULE - Asset path resolution utilities

This module provides utilities for resolving asset paths reliably:
- Finds project root by locating 'assets/' directory
- Constructs absolute paths to asset files
- Validates asset existence
- Handles Windows/Linux/Mac path differences via os.path

The module works from any location in the project and handles
complex directory hierarchies by searching upward for the 'assets' folder.

Example:
    from utils.paths import get_asset_path
    sprite_path = get_asset_path('sprites', 'player', 'idle.png')
"""

import os


# ============================================================================
# PROJECT ROOT DISCOVERY
# ============================================================================

def find_project_root(max_levels=6):
    """
    Find project root directory by locating 'assets/' folder.
    
    Searches upward through directory hierarchy from current file location
    until finding a directory containing 'assets/' folder. This allows the
    function to work correctly regardless of where code is executed from.
    
    Args:
        max_levels (int): Maximum directory levels to search up (default 6)
        
    Returns:
        str: Absolute path to project root directory containing 'assets/'
    """
    # Start from current utils directory
    cur = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Search upward for 'assets' directory
    for _ in range(max_levels):
        if os.path.isdir(os.path.join(cur, 'assets')):
            return cur
        
        # Move to parent directory
        parent = os.path.dirname(cur)
        
        # Stop if reached filesystem root
        if parent == cur:
            break
        cur = parent
    
    # Fallback: two levels up from utils directory
    # This is the typical structure: project_root/src/utils/paths.py
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


# ============================================================================
# ASSET PATH CONSTRUCTION
# ============================================================================

def get_asset_path(*parts):
    """
    Construct absolute path to asset file.
    
    Handles cross-platform path construction and resolves from any
    location in the project by finding project root dynamically.
    
    Args:
        *parts: Path components after 'assets' directory
        
    Returns:
        str: Absolute path to asset file
        
    Example:
        >>> sprite_path = get_asset_path('sprites', 'player', 'idle.png')
        '/full/path/to/project/assets/sprites/player/idle.png'
    """
    root = find_project_root()
    return os.path.join(root, 'assets', *parts)


# ============================================================================
# ASSET VALIDATION
# ============================================================================

def ensure_asset_exists(*parts):
    """
    Get asset path and verify it exists.
    
    Raises FileNotFoundError if asset file is not found.
    Useful for validating assets at startup or before use.
    
    Args:
        *parts: Path components after 'assets' directory
        
    Returns:
        str: Absolute path to asset file (guaranteed to exist)
        
    Raises:
        FileNotFoundError: If asset file does not exist
        
    Example:
        >>> music_path = ensure_asset_exists('sounds', 'bgm.mp3')
    """
    path = get_asset_path(*parts)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Asset introuvable: {path}")
    return path
