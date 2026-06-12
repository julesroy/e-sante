import sys, os

def resource_path(relative_path: str) -> str:
    """
    Retourne le chemin absolu vers une ressource.
    Compatible mode dev ET exe PyInstaller.
    """
    if hasattr(sys, '_MEIPASS'):
        # Mode PyInstaller : les assests sont dans le dossier temporaire
        base = sys._MEIPASS
    else:
        # Mode dev
        base = os.path.dirname(os.path.abspath(__file__ + "/.."))
    return os.path.join(base ,relative_path)

def find_env_path():
    if hasattr(sys, '_MEIPASS'):
        # Exe PyInstaller : cherche .env à côté de l'exe
        return os.path.join(os.path.dirname(sys.executable), '.env')
    else:
        # Dev : .env à la racine du projet
        return os.path.join(os.path.dirname(__file__), '..', '.env')

