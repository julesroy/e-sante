# ===== IMPORTS UNIQUEMENT POUR PYLANCE (jamais exécutés) =====
from __future__ import annotations
from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt

if TYPE_CHECKING:
    from views.MainView import MainView
    from controllers.MainController import MainController

class AnnotationController:
    def __init__(self, main_controller: MainController):
        self.main_controller = main_controller

    @property
    def view(self):
        return self.main_controller.view

    def deactivate_all_modes(self):
        """Désactive proprement tous les outils de cette section (Stylo, Texte)."""
        if getattr(self.view, "pen_active", False):
            self.view.left_toolbar.btn_pen.setChecked(False)
            self.view.pen_active = False
            if hasattr(self.view.image_display, "annotations_overlay"):
                self.view.image_display.annotations_overlay.clear()

        if getattr(self.view, "text_anno_active", False):
            self.view.left_toolbar.btn_text.setChecked(False)
            self.view.text_anno_active = False
            if hasattr(self.view.image_display, "annotations_overlay"):
                self.view.image_display.annotations_overlay.clear()

    def handle_pen_toggle(self, checked: bool):
        """Gère l'activation du mode Stylo depuis la LeftToolbar."""
        if self.view.current_pixmap is None:
            self.view.left_toolbar.btn_pen.setChecked(False)
            return

        self.view.pen_active = checked
        if checked:
            print("Mode Stylo d'annotation activé.")
            # Désactiver les outils de mesure (RulerController)
            if hasattr(self.main_controller, "ruler_ctrl"):
                self.main_controller.ruler_ctrl.deactivate_all_modes()
            
            # Désactiver l'autre outil d'annotation (Texte)
            if getattr(self.view, "text_anno_active", False):
                self.view.left_toolbar.btn_text.setChecked(False)
                self.view.text_anno_active = False
            
            if hasattr(self.view.image_display, "annotations_overlay"):
                self.view.image_display.annotations_overlay.clear()
            self.view.image_display.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            print("Mode Stylo d'annotation désactivé.")
            self.view.image_display.setCursor(Qt.CursorShape.ArrowCursor)

        self.view.image_display.update()

    def handle_text_anno_toggle(self, checked: bool):
        """Gère l'activation du mode Texte depuis la LeftToolbar."""
        if self.view.current_pixmap is None:
            self.view.left_toolbar.btn_text.setChecked(False)
            return

        self.view.text_anno_active = checked
        if checked:
            print("Mode Texte d'annotation activé.")
            # Désactiver les outils de mesure (RulerController)
            if hasattr(self.main_controller, "ruler_ctrl"):
                self.main_controller.ruler_ctrl.deactivate_all_modes()
            
            # Désactiver l'autre outil d'annotation (Stylo)
            if getattr(self.view, "pen_active", False):
                self.view.left_toolbar.btn_pen.setChecked(False)
                self.view.pen_active = False
            
            if hasattr(self.view.image_display, "annotations_overlay"):
                self.view.image_display.annotations_overlay.clear()
            self.view.image_display.setCursor(Qt.CursorShape.CrossCursor)
        else:
            print("Mode Texte d'annotation désactivé.")
            self.view.image_display.setCursor(Qt.CursorShape.ArrowCursor)

        self.view.image_display.update()

    def handle_color_dialog(self):
        """Ouvre une boîte de dialogue pour choisir la couleur des annotations."""
        from PyQt6.QtWidgets import QColorDialog
        if not hasattr(self.view.image_display, "annotations_overlay"):
            return
            
        current_color = self.view.image_display.annotations_overlay.current_color
        color = QColorDialog.getColor(current_color, self.view, "Couleur d'annotation")
        if color.isValid():
            self.view.image_display.annotations_overlay.current_color = color
            # Mettre à jour visuellement le bouton avec la couleur sélectionnée
            self.view.left_toolbar.btn_color.setStyleSheet(
                f"background-color: {color.name()}; border: 2px solid white; border-radius: 4px; color: white;"
            )

    def handle_clear_annotations(self):
        """Efface toutes les annotations."""
        if hasattr(self.view.image_display, "annotations_overlay"):
            self.view.image_display.annotations_overlay.clear_all()
            self.view.image_display.update()
            print("Toutes les annotations ont été effacées.")
