import os
import sys
import ctypes
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase 

from models.MainModel import MainModel
from views.MainView import MainView
from controllers.MainController import MainController
from database.db import init_db, test_connexion

if sys.platform == "win32":
    appId = "pixelmed.version_1"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appId)

def main():
    """
    Point d'entrée du logiciel.
    """
    app = QApplication(sys.argv)
   
    # Initialisation de la BDD au démarrage (crée les tables si besoin)
    # test_connexion() # à retirer une fois que c'est stable
    # init_db()

    font_path = os.path.join(os.path.dirname(__file__), "assets", "styles", "fonts", "fontawesome-webfont.ttf")
    if os.path.exists(font_path):
        # On enregistre la police dans le système de PyQt
        QFontDatabase.addApplicationFont(font_path)
    else:
        print(f"Attention : Police FontAwesome introuvable à {font_path}")
    # chemin absolu vers le fichier QSS (évite les erreurs de chemin relatif)
    style_path = os.path.join(os.path.dirname(__file__), "assets", "styles", "style.qss")

    # lecture et application du style
    if os.path.exists(style_path):
        with open(style_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    else:
        print(f"Attention : Fichier de style introuvable à {style_path}")

    # initialisation du modèle, de la vue et du contrôleur
    model = MainModel()
    view = MainView()
    controller = MainController(model, view)

    view.controller = controller
    
    # affichage de la vue
    view.show()

    # boucle d'exécution de l'application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
