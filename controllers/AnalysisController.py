# ===== IMPORTS PYTHON STANDARD =====
from __future__ import annotations
import sys, os
import numpy as np

# ===== IMPORTS UNIQUEMENT POUR PYLANCE (jamais exécutés) =====
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from views.MainView import MainView
    from controllers.MainController import MainController

# ===== IMPORTS DES MODÈLES =====
from models.TFD2D import TFD2D
from models.CLAHE import CLAHE
from models.Seuillage import Seuillage
from views.PopupFFT import FilterDialog


class AnalysisController:
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
    def _contrast_base_array(self):
        return self.main_controller._contrast_base_array

    @_contrast_base_array.setter
    def _contrast_base_array(self, value):
        self.main_controller._contrast_base_array = value

    @property
    def error_handler(self):
        return self.main_controller.error_handler

    def _display_numpy_array(self, array):
        self.main_controller._display_numpy_array(array)

    def handle_tfd2d(self):
        """
        Applique la Transformée de Fourier Discrète 2D sur l'image courante
        et affiche le spectre fréquentiel dans la View.
        Le spectre est normalisé entre 0 et 1 avant affichage.
        Nécessite qu'une image soit chargée (_current_array != None).
        """
        try:
            if self._current_array is None:
                self.error_handler.show_error("Erreur", "Aucune image chargée")
                return

            # Calcul du spectre fréquentiel via la TFD2D
            tfd2d = TFD2D(self._current_array)
            spectre = tfd2d.calculerTFDSpectre()

            # Normalisation [0,1] — on évite la division par zéro si le spectre est vide
            max_val = spectre.max()
            self._display_numpy_array(spectre / max_val if max_val > 0 else spectre)

        except Exception as e:
            self.error_handler.handle_exception(e)
            return

    def handle_clahe(self):
        """
        Applique le CLAHE (Contrast Limited Adaptive Histogram Equalization)
        sur l'image courante et affiche le résultat dans la View.
        Nécessite qu'une image soit chargée (_current_array != None).
        """
        try:
            if self._current_array is None:
                self.error_handler.show_error("Erreur", "Aucune image chargée")
                return

            # Application du CLAHE
            clahe = CLAHE(5.0, (16, 16), self._current_array)
            result = clahe.appliquer()

            # Affichage du résultat
            self._display_numpy_array(result)

        except Exception as e:
            self.error_handler.handle_exception(e)
            return

    def handle_contrast_slider(self, checked):
        """
        Initialise le slider de contraste en bas à gauche de l'image.
        Le slider met à jour l'image en temps réel quand on le bouge.
        Nécessite qu'une image soit chargée (_current_array != None).

        :param checked: True pour activer, False pour désactiver
        """
        try:
            if self._current_array is None:
                self.error_handler.show_error("Erreur", "Aucune image chargée")
                return

            if checked:
                # Sauvegarder l'image courante comme référence pour les calculs de contraste
                self._contrast_base_array = self._current_array.copy()
                print("Slider de contraste activé - Image de base sauvegardée")
            else:
                # Réinitialiser
                self._contrast_base_array = None
                print("Slider de contraste désactivé")

        except Exception as e:
            self.error_handler.handle_exception(e)
            return

    def apply_contrast_realtime(self, facteur_contraste):
        """
        Applique le contraste en temps réel à partir de l'image de base.
        Cette méthode est appelée à chaque mouvement du slider.

        :param facteur_contraste: Valeur du slider (1-10)
        """
        try:
            if self._contrast_base_array is None:
                return

            # Application de l'ajustement de contraste sur l'image de base
            # new_pixel = 0.5 + facteur * (old_pixel - 0.5)
            result = 0.5 + facteur_contraste * (self._contrast_base_array - 0.5)
            result = np.clip(result, 0, 1).astype(np.float32)

            # Mettre à jour _current_array pour que l'affichage reflète les modifications
            self._current_array = result

            # Affichage
            self._display_numpy_array(result)

        except Exception as e:
            self.error_handler.handle_exception(e)
            return

    def handle_seuillage(self):
        """
        Ouvre la popup pour le seuillage et applique le masque
        Slider a 0 -> Otsu automatique, sinon seuil manuel [1-255]
        """
        try:
            if self._current_array is None:
                self.error_handler.show_error("Erreur", "Aucune image chargee")
                return

            dialog = FilterDialog(self.view)
            dialog.setWindowTitle("Seuillage (0 = Otsu auto)")
            dialog.slider.setMinimum(0)
            dialog.slider.setMaximum(255)
            dialog.slider.setValue(0)  # Otsu par defaut

            if dialog.exec():
                valeur = dialog.slider.value()

                # 0 -> Otsu automatique, sinon seuil automatique
                seuil_manuel = None if valeur == 0 else valeur
                outil = Seuillage(seuil_manuel=seuil_manuel)
                masque, seuil_calcule = outil.appliquer(self._current_array)

                # masque est uint8 [0,255], on normalise en [0,1] pour l'affichage
                result = (masque / 255.0).astype(np.float32)
                self._display_numpy_array(result)

                mode = f"Otsu (seuil calculé: {int(seuil_calcule)})" if seuil_manuel is None else f"Manuel: {seuil_manuel}"
                print(f"Seuillage appliqué - {mode}")

        except Exception as e:
            self.error_handler.handle_exception(e)
            return
