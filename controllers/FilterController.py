# ===== IMPORTS PYTHON STANDARD =====
from __future__ import annotations
import sys, os

# ===== IMPORTS UNIQUEMENT POUR PYLANCE (jamais exécutés) =====
from typing import TYPE_CHECKING
from collections.abc import Callable
if TYPE_CHECKING:
    import numpy as np
    from views.MainView import MainView

# ===== IMPORTS DES MODÈLES =====
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "models"))
from FiltrageGaussien import FiltrageGaussien


class FilterController:
    # Ces attributs appartiennent à MainController.
    # On les déclare ici pour que Pylance sache qu'ils existent quand on y accède via self.
    view: MainView
    _current_array: np.ndarray | None
    _display_numpy_array: Callable

    def handle_gaussian(self):
        """
        Applique le filtre gaussien sur l'image courante
        et affiche le résultat dans la View.
        Nécessite qu'une image soit chargée (_current_array != None).
        """
        # On ne fait rien si aucune image n'est chargée
        if self._current_array is None:
            return

        # Kernel 9×9 (noyau de convolution) — sigma=0 = auto calculé par OpenCV
        kernel_size = 9
        filtre = FiltrageGaussien((kernel_size, kernel_size), 0, self._current_array)

        # Application du filtre -> retourne un np.ndarray float32 [0,1]
        result_array = filtre.filtrage()

        # Affichage du résultat via la méthode centrale de rendu
        self._display_numpy_array(result_array)