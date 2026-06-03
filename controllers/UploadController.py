# ===== IMPORTS PYTHON STANDARD =====
from __future__ import annotations  # permet d'utiliser les annotations de type avant leur définition
import sys, os

# ===== IMPORTS UNIQUEMENT POUR PYLANCE (jamais exécutés) =====
# Ces imports permettent à Pylance de connaître les types sans créer de dépendances circulaires
from typing import TYPE_CHECKING
from collections.abc import Callable
if TYPE_CHECKING:
    import numpy as np
    from views.MainView import MainView

# ===== IMPORTS PYQT6 =====
from PyQt6.QtWidgets import QFileDialog

# ===== IMPORTS DES MODÈLES =====
# On ajoute le dossier models au path car ce fichier est dans controllers/
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "models"))
from ImageConvertie import ImageConvertie


class UploadController:
    # Ces attributs appartiennent à MainController.
    # On les déclare ici pour que Pylance sache qu'ils existent quand on y accède via self.
    view: MainView
    _current_array: np.ndarray | None

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
            if file_path.lower().endswith('.dcm'):
                self._display_numpy_array(self._current_array)
            else:
                # Pour PNG/JPG, afficher directement et mémoriser
                self.view.display_medical_image(file_path)

            # Mémoriser le pixmap d'origine chargé depuis le fichier
            if getattr(self.view, "current_pixmap", None) is not None:
                self._original_pixmap = self.view.current_pixmap.copy()