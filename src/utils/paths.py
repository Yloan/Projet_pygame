import os


def find_project_root(max_levels=6):
    """Remonte l'arborescence depuis `src/utils` pour trouver le dossier contenant `assets/`.
    Retourne le chemin du projet (répertoire parent où se trouve `assets`).
    """
    cur = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    for _ in range(max_levels):
        if os.path.isdir(os.path.join(cur, 'assets')):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    # fallback: two levels up
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def get_asset_path(*parts):
    """Construit un chemin absolu vers un fichier dans `assets/`.
    Ex: get_asset_path('maps', 'map-1-BACKGROUND-Sheet.png')
    """
    root = find_project_root()
    return os.path.join(root, 'assets', *parts)


def ensure_asset_exists(*parts):
    path = get_asset_path(*parts)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Asset introuvable: {path}")
    return path
