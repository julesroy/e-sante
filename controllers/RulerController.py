# ===== IMPORTS UNIQUEMENT POUR PYLANCE (jamais exécutés) =====
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from views.MainView import MainView
    from controllers.MainController import MainController


class RulerController:
    def __init__(self, main_controller: MainController):
        self.main_controller = main_controller

    @property
    def view(self):
        return self.main_controller.view

    @property
    def error_controller(self):
        return self.main_controller.error_handler

    def handle_ruler_toggle(self, checked: bool):
        """Gère l'activation du mode règle depuis la LeftToolbar."""
        if self.view.current_pixmap is None:
            self.view.left_toolbar.btn_ruler.setChecked(False)
            return

        self.view.ruler_active = checked
        if checked:
            print("Mode Règle de mesure activé.")
            # Si on active la règle, on nettoie l'ancienne mesure pour être propre
            if hasattr(self.view.image_display, "ruler_overlay"):
                self.view.image_display.ruler_overlay.clear()
        else:
            print("Mode Règle de mesure désactivé.")

        self.view.image_display.update()
