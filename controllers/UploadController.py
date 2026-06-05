# ===== IMPORTS PYTHON STANDARD =====
from __future__ import annotations
import sys, os

# ===== IMPORTS UNIQUEMENT POUR PYLANCE (jamais exécutés) =====
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np
    from views.MainView import MainView
    from controllers.MainController import MainController

# ===== IMPORTS PYQT6 =====
from PyQt6.QtWidgets import QFileDialog

# ===== IMPORTS DES MODÈLES =====
from models.ImageConvertie import ImageConvertie


class UploadController:
    def __init__(self, main_controller: MainController):
        self.main_controller = main_controller

    @property
    def view(self):
        return self.main_controller.view

    @property
    def _current_array(self):
        return self.main_controller._current_array

    @_current_array.setter
    def _current_array(self, value):
        self.main_controller._current_array = value

    @property
    def _original_pixmap(self):
        return self.main_controller._original_pixmap

    @_original_pixmap.setter
    def _original_pixmap(self, value):
        self.main_controller._original_pixmap = value

    @property
    def _last_file_path(self):
        return self.main_controller._last_file_path

    @_last_file_path.setter
    def _last_file_path(self, value):
        self.main_controller._last_file_path = value

    def _display_numpy_array(self, array):
        self.main_controller._display_numpy_array(array)

    def handle_upload(self):
        """
        Ouvre l'explorateur de fichiers, affiche l'image dans la View
        et stocke sa matrice numpy normalisée pour les traitements ultérieurs.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self.view,
            "Sélectionner une radiographie",
            "",
            "Images (*.png *.jpg *.jpeg *.dcm)",
        )

        if file_path:
            self._original_pixmap = None
            self._last_file_path = file_path

            # Conversion en numpy array normalisé [0,1] pour les traitements ultérieurs
            self._current_array = ImageConvertie(file_path).convertirEnNumpyArray()

            # Pour les DICOM, afficher via numpy array plutôt que QPixmap directement
            if file_path.lower().endswith(".dcm"):
                self._display_numpy_array(self._current_array)
            else:
                # Pour PNG/JPG, afficher directement et mémoriser
                self.view.display_medical_image(file_path)

            # Mémoriser le pixmap d'origine chargé depuis le fichier
            if getattr(self.view, "current_pixmap", None) is not None:
                self._original_pixmap = self.view.current_pixmap.copy()
