# ===== IMPORTS PYTHON STANDARD =====
from __future__ import annotations
import sys, os
from PyQt6.QtWidgets import QDialog
import numpy as np

# ===== IMPORTS UNIQUEMENT POUR PYLANCE (jamais exécutés) =====
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from views.MainView import MainView
    from controllers.MainController import MainController

# ===== IMPORTS DES MODÈLES =====
from models.FiltrageGaussien import FiltrageGaussien
from models.FiltrageSobel import FiltrageSobel
from models.TFD2D import TFD2D
from views.FilterDialog import FilterDialog
from views.GaussianDialog import GaussianDialog


class FilterController:
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
    def error_handler(self):
        return self.main_controller.error_handler

    def _display_numpy_array(self, array):
        self.main_controller._display_numpy_array(array)

    def handle_gaussian(self):
        """
        Applique le filtre gaussien sur l'image courante
        et affiche le résultat dans la View.
        Nécessite qu'une image soit chargée (_current_array != None).
        """
        try:
            if self._current_array is None:
                self.error_handler.show_error("Erreur", "Aucune image chargée")
                return

            dialog = GaussianDialog(self.view)
            if dialog.exec():
                sigma = dialog.get_value()
                filtre = FiltrageGaussien(sigma, self._current_array)
                result_array = filtre.filtrage()
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
        try:
            if self._current_array is None:
                self.error_handler.show_error("Erreur", "Aucune image chargée")
                return

            # on applique le filtre
            filtreGauss = FiltrageGaussien(2, self._current_array)
            image_gaussienne = filtreGauss.filtrage()
            filtre = FiltrageSobel(image_gaussienne)
            result_array = filtre.filtrage()  # uint8 [0,255]

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
                self.error_handler.show_error("Erreur", "Aucune image chargée")
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
        try:
            if self._current_array is None:
                self.error_handler.show_error("Erreur", "Aucune image chargée")
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
