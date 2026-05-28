# ===== IMPORTS PYTHON STANDARD =====
from __future__ import annotations
import sys, os
import numpy as np

# ===== IMPORTS UNIQUEMENT POUR PYLANCE (jamais exécutés) =====
from typing import TYPE_CHECKING
from collections.abc import Callable
if TYPE_CHECKING:
    from views.MainView import MainView
    from controllers.ErrorController import ErrorController

# ===== IMPORTS DES MODÈLES =====
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "models"))
from views.PopupFFT import FilterDialog
from TFD2D import TFD2D
from CLAHE import CLAHE
from Seuillage import Seuillage

class AnalysisController:
    # Ces attributs appartiennent à MainController.
    # On les déclare ici pour que Pylance sache qu'ils existent quand on y accède via self.
    view: MainView
    _current_array: np.ndarray | None
    _display_numpy_array: Callable
    error_handler: ErrorController
    def handle_tfd2d(self):
        """
        Applique la Transformée de Fourier Discrète 2D sur l'image courante
        et affiche le spectre fréquentiel dans la View.
        Le spectre est normalisé entre 0 et 1 avant affichage.
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
        # On ne fait rien si aucune image n'est chargée
        try:
            if self._current_array is None:
                self.error_handler.show_error(
                    "Erreur",
                    "Aucune image chargée"
                )
                return

            # Application du CLAHE
            clahe = CLAHE(5.0, (16, 16), self._current_array)
            result = clahe.appliquer()

            # Affichage du résultat
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
                self.error_handler.show_error(
                    "Erreur", "Aucune image chargee"
                )
                return
            
            dialog = FilterDialog(self.view)
            dialog.setWindowTitle("Seuillage (0 = Otsu auto)")
            dialog.slider.setMinimum(0)
            dialog.slider.setMaximum(255)
            dialog.slider.setValue(0) #Otsu par defaut

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
        