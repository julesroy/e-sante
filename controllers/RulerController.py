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
            # Désactiver les autres modes
            if getattr(self.view, "angle_active", False):
                self.view.left_toolbar.btn_angle.setChecked(False)
                self.view.angle_active = False
            if getattr(self.view, "height_comp_active", False):
                self.view.left_toolbar.btn_height_comp.setChecked(False)
                self.view.height_comp_active = False

            if hasattr(self.view.image_display, "ruler_overlay"):
                self.view.image_display.ruler_overlay.clear()
            if hasattr(self.view.image_display, "angle_overlay"):
                self.view.image_display.angle_overlay.clear()
            if hasattr(self.view.image_display, "height_comp_overlay"):
                self.view.image_display.height_comp_overlay.clear()
        else:
            print("Mode Règle de mesure désactivé.")

        self.view.image_display.update()

    def handle_angle_toggle(self, checked: bool):
        """Gère l'activation du mode angle depuis la LeftToolbar."""
        if self.view.current_pixmap is None:
            self.view.left_toolbar.btn_angle.setChecked(False)
            return

        self.view.angle_active = checked
        if checked:
            print("Mode Angle de mesure activé.")
            # Désactiver les autres modes
            if getattr(self.view, "ruler_active", False):
                self.view.left_toolbar.btn_ruler.setChecked(False)
                self.view.ruler_active = False
            if getattr(self.view, "height_comp_active", False):
                self.view.left_toolbar.btn_height_comp.setChecked(False)
                self.view.height_comp_active = False

            if hasattr(self.view.image_display, "angle_overlay"):
                self.view.image_display.angle_overlay.clear()
            if hasattr(self.view.image_display, "ruler_overlay"):
                self.view.image_display.ruler_overlay.clear()
            if hasattr(self.view.image_display, "height_comp_overlay"):
                self.view.image_display.height_comp_overlay.clear()
        else:
            print("Mode Angle de mesure désactivé.")

        self.view.image_display.update()

    def handle_height_comp_toggle(self, checked: bool):
        """Gère l'activation du mode comparateur de hauteur depuis la LeftToolbar."""
        if self.view.current_pixmap is None:
            self.view.left_toolbar.btn_height_comp.setChecked(False)
            return

        self.view.height_comp_active = checked
        if checked:
            print("Mode Comparateur de hauteur activé.")
            # Désactiver les autres modes
            if getattr(self.view, "ruler_active", False):
                self.view.left_toolbar.btn_ruler.setChecked(False)
                self.view.ruler_active = False
            if getattr(self.view, "angle_active", False):
                self.view.left_toolbar.btn_angle.setChecked(False)
                self.view.angle_active = False

            if hasattr(self.view.image_display, "height_comp_overlay"):
                self.view.image_display.height_comp_overlay.clear()
            if hasattr(self.view.image_display, "ruler_overlay"):
                self.view.image_display.ruler_overlay.clear()
            if hasattr(self.view.image_display, "angle_overlay"):
                self.view.image_display.angle_overlay.clear()
        else:
            print("Mode Comparateur de hauteur désactivé.")

        self.view.image_display.update()
