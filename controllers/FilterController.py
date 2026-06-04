# ===== IMPORTS PYTHON STANDARD =====
from __future__ import annotations
import sys, os
from PyQt6.QtWidgets import QDialog
import numpy as np

# ===== IMPORTS UNIQUEMENT POUR PYLANCE (jamais exécutés) =====
from typing import TYPE_CHECKING
from collections.abc import Callable
if TYPE_CHECKING:
    from views.MainView import MainView
    from controllers.ErrorController import ErrorController

# ===== IMPORTS DES MODÈLES =====
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "models"))
from FiltrageGaussien import FiltrageGaussien
from views.PopupFFT import FilterDialog
from TFD2D import TFD2D
from FiltrageSobel import FiltrageSobel

class FilterController:
    # Ces attributs appartiennent à MainController.
    # On les déclare ici pour que Pylance sache qu'ils existent quand on y accède via self.
    view: MainView
    _current_array: np.ndarray | None
    _display_numpy_array: Callable
    error_handler: ErrorController

    def handle_gaussian(self):
        """
        Applique le filtre gaussien sur l'image courante
        et affiche le résultat dans la View.
        Nécessite qu'une image soit chargée (_current_array != None).
        """
        # On ne fait rien si aucune image n'est chargée
        try:
            if self._current_array is None:
                self.error_handler.show_error(
                    "Erreur",
                    "Aucune image chargée"
                )
                return
                
            filtre = FiltrageGaussien(8, self._current_array)
            result_array = filtre.filtrage()
            # print(result_array)  # Affiche la matrice filtrée dans la console pour vérification

            # Affichage du résultat via la méthode centrale de rendu
            # result = (result_array / 255.0).astype(np.float32)  # Normaliser en [0,1]
            self._display_numpy_array(result_array)

        except Exception as e:
            self.error_handler.handle_exception(e)
            return

    def handle_sobel(self):
        """
        Applique le filtre de Sobel sur l'image courante
        et affiche le résultat dans la View.
        Nécessite qu'une image soit chargée (_current_array != None).
        """
        # On ne fait rien si aucune image n'est chargée
        try:
            if self._current_array is None:
                self.error_handler.show_error(
                    "Erreur",
                    "Aucune image chargée"
                )
                return

            # on applique le filtre
            filtreGauss = FiltrageGaussien(2, self._current_array)
            image_gaussienne = filtreGauss.filtrage()
            filtre = FiltrageSobel(image_gaussienne)
            result_array = filtre.filtrage()  # uint8 [0,255]

            # Affichage du résultat via la méthode centrale de rendu
            # result = (result_array / 255.0).astype(np.float32)  # Normaliser en [0,1]
            self._display_numpy_array(result_array)

        except Exception as e:
            self.error_handler.handle_exception(e)
            return

    def handle_passe_bas(self):
        """
        Ouvre simplement la popup et permet de choisir une fréquence
        via le slider
        """
        try:
            if self._current_array is None:
                self.error_handler.show_error(
                    "Erreur",
                    "Aucune image chargée"
                )
                return

            dialog = FilterDialog(self.view)
            dialog.setWindowTitle("Filtre Passe-Bas")

            if dialog.exec():
                rayon = dialog.slider.value()

                # Calcul TFD + application du masque passe-bas
                tfd = TFD2D(self._current_array)
                tfd.calculerTFDSpectre()
                tfd.filtragePasseBas(rayon)

                # Reconstruction de l'image depuis la TFD filtree
                image_reconstruite = tfd.calculerTFDInverse()

                # Normalisation [0,1] avant affichage
                max_val = image_reconstruite.max()
                result = (image_reconstruite / max_val).astype(np.float32) if max_val > 0 else image_reconstruite
                self._display_numpy_array(result)

                print(f"Popup Passe-Bas fermée. Fréquence sélectionnée : {rayon}")


        except Exception as e:
            self.error_handler.handle_exception(e)
            return

    def handle_passe_haut(self):
        """
        Ouvre la popup pour le filtre Passe-Haut et permet de choisir 
        une fréquence via le slider
        """
        # Sécurité : image chargée obligatoire
        try:
            if self._current_array is None:
                self.error_handler.show_error(
                    "Erreur",
                    "Aucune image chargée"
                )
                return

            dialog = FilterDialog(self.view)
            dialog.setWindowTitle("Filtre Passe-Haut")

            if dialog.exec():
                rayon = dialog.slider.value()

                # Calcul TFD + application du masque passe-haut
                tfd = TFD2D(self._current_array)
                tfd.calculerTFDSpectre()
                tfd.filtragePasseHaut(rayon)

                # Reconstruction de l'image depuis la TFD filtrée
                image_reconstruite = tfd.calculerTFDInverse()

                # Normalisation [0,1] avant affichage
                max_val = image_reconstruite.max()
                result = (image_reconstruite / max_val).astype(np.float32) if max_val > 0 else image_reconstruite
                self._display_numpy_array(result)

                print(f"Popup Passe-Haut fermée. Fréquence sélectionnée : {rayon}")

        except Exception as e:
            self.error_handler.handle_exception(e)
            return