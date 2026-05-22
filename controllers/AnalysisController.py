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
from TFD2D import TFD2D


class AnalysisController:
    # Ces attributs appartiennent à MainController.
    # On les déclare ici pour que Pylance sache qu'ils existent quand on y accède via self.
    view: MainView
    _current_array: np.ndarray | None
    _display_numpy_array: Callable

    def handle_tfd2d(self):
        """
        Applique la Transformée de Fourier Discrète 2D sur l'image courante
        et affiche le spectre fréquentiel dans la View.
        Le spectre est normalisé entre 0 et 1 avant affichage.
        Nécessite qu'une image soit chargée (_current_array != None).
        """
        # On ne fait rien si aucune image n'est chargée
        if self._current_array is None:
            return

        # Calcul du spectre fréquentiel via la TFD2D
        tfd2d = TFD2D(self._current_array)
        spectre = tfd2d.calculerTFDSpectre()

        # Normalisation [0,1] — on évite la division par zéro si le spectre est vide
        max_val = spectre.max()
        self._display_numpy_array(spectre / max_val if max_val > 0 else spectre)