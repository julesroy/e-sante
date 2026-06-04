# ===== IMPORTS UNIQUEMENT POUR PYLANCE (jamais exécutés) =====
from typing import TYPE_CHECKING
from collections.abc import Callable
if TYPE_CHECKING:
    from views.MainView import MainView
    from controllers.ErrorController import ErrorController

class RulerController:
    def __init__(self, view: 'MainView', error_controller: 'ErrorController'):
        self.view = view
        self.error_controller = error_controller

    def handle_ruler_toggle(self, checked: bool):
        """Gère l'activation du mode règle depuis la LeftToolbar."""
        if self.view.current_pixmap is None:
            self.view.left_toolbar.btn_ruler.setChecked(False)
            return

        self.view.ruler_active = checked
        if checked:
            print("Mode Règle de mesure activé.")
            # Si on active la règle, on nettoie l'ancienne mesure pour être propre
            if hasattr(self.view.image_display, 'ruler_overlay'):
                self.view.image_display.ruler_overlay.clear()
        else:
            print("Mode Règle de mesure désactivé.")
            
        self.view.image_display.update()