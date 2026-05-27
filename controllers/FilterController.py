# ===== IMPORTS PYTHON STANDARD =====
from __future__ import annotations
import sys, os
from PyQt6.QtWidgets import QDialog

# ===== IMPORTS UNIQUEMENT POUR PYLANCE (jamais exécutés) =====
from typing import TYPE_CHECKING
from collections.abc import Callable
if TYPE_CHECKING:
    import numpy as np
    from views.MainView import MainView

# ===== IMPORTS DES MODÈLES =====
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "models"))
from FiltrageGaussien import FiltrageGaussien
from views.PopupFFT import FilterDialog


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

    def handle_passe_bas(self):
        """
        Ouvre simplement la popup et permet de choisir une fréquence
        via le slider
        """
        if self._current_array is None:
            return

        dialog = FilterDialog(self.view)
        dialog.setWindowTitle("Filtre Passe-Bas")

        if dialog.exec():
            valeur_choisie = dialog.slider.value()
            print(f"Popup Passe-Bas fermée. Fréquence sélectionnée : {valeur_choisie}")

    def handle_passe_haut(self):
        """
        Ouvre la popup pour le filtre Passe-Haut et permet de choisir 
        une fréquence via le slider
        """
        # Sécurité : image chargée obligatoire
        if self._current_array is None:
            return

        dialog = FilterDialog(self.view)
        dialog.setWindowTitle("Filtre Passe-Haut")

        if dialog.exec():
            valeur_choisie = dialog.slider.value()
            print(f"Popup Passe-Haut fermée. Fréquence sélectionnée : {valeur_choisie}")