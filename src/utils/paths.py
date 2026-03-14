import os


def find_project_root(max_levels=6):
    """
    Find project root directory by locating 'assets/' folder.
    
    Searches upward through directory hierarchy from current file location
    until finding a directory containing 'assets/' folder.
    
    Args:
        max_levels (int): Maximum directory levels to search up (default 6)
        
    Returns:
        str: Absolute path to project root directory containing 'assets/'
    """
    cur = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    for _ in range(max_levels):
        if os.path.isdir(os.path.join(cur, 'assets')):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def get_asset_path(*parts):
    """
    Construct absolute path to asset file.
    
    Handles cross-platform path construction and resolves from any
    location in the project by finding project root dynamically.
    
    Args:
        *parts: Path components after 'assets' directory
        
    Returns:
        str: Absolute path to asset file
    """
    root = find_project_root()
    return os.path.join(root, 'assets', *parts)


def ensure_asset_exists(*parts):
    """
    Get asset path and verify it exists.
    
    Args:
        *parts: Path components after 'assets' directory
        
    Returns:
        str: Absolute path to asset file (guaranteed to exist)
        
    Raises:
        FileNotFoundError: If asset file does not exist
    """
    path = get_asset_path(*parts)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Asset introuvable: {path}")
    return path
