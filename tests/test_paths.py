# test_paths.py — à supprimer après vérification
from utils.paths import resource_path, find_env_path
import os

chemins = {
    "Style QSS":      resource_path(os.path.join("assets", "styles", "style.qss")),
    "Font Awesome":   resource_path(os.path.join("assets", "styles", "fonts", "fontawesome-webfont.ttf")),
    "App icon":       resource_path(os.path.join("assets", "icons", "app_icon.png")),
    "Ruler icon":     resource_path(os.path.join("assets", "icons", "ruler-icon.svg")),
    "Angle icon":     resource_path(os.path.join("assets", "icons", "angle-icon.svg")),
    "Manuel HTML":    resource_path(os.path.join("manuel", "manuel.html")),
    "Fichier .env":   find_env_path(),
}

print("\n=== TEST resource_path ===\n")
all_ok = True
for nom, chemin in chemins.items():
    existe = os.path.exists(chemin)
    statut = "✅" if existe else "❌ INTROUVABLE"
    print(f"{statut}  {nom}\n      → {chemin}\n")
    if not existe:
        all_ok = False

print("=== RÉSULTAT :", "TOUT OK ✅" if all_ok else "DES FICHIERS MANQUENT ❌", "===\n")