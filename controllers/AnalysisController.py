# ===== IMPORTS PYTHON STANDARD =====
from __future__ import annotations
import sys, os
import numpy as np
import scipy.ndimage as ndimage
import cv2

# ===== IMPORTS UNIQUEMENT POUR PYLANCE (jamais exécutés) =====
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from views.MainView import MainView
    from controllers.MainController import MainController

# ===== IMPORTS DES MODÈLES =====
from models.TFD2D import TFD2D
from models.CLAHE import CLAHE
from models.Seuillage import Seuillage
from models.MorphologieMathematique import MorphologieMathematique
from models.Watershed import SegmentationWatershed
from models.FiltrageGaussien import FiltrageGaussien
from views.FilterDialog import FilterDialog
from views.ClaheDialog import ClaheDialog
from views.WatershedDialog import WatershedDialog


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

    def handle_tfd2d(self, checked: bool):
        """
        Applique la Transformée de Fourier Discrète 2D sur l'image courante
        et l'affiche/masque sous forme de vignette (overlay) au-dessus des infos de l'image.
        Nécessite qu'une image soit chargée (_current_array != None).
        """
        try:
            if self._current_array is None:
                self.error_handler.show_error("Erreur", "Aucune image chargée")
                self.view.top_toolbar.btn_fft.setChecked(False)
                return

            if checked:
                # Désactiver l'histogramme si actif
                self.view.top_toolbar.btn_histo.setChecked(False)
                self.view.hide_histogram()

                # Calcul du spectre fréquentiel via la TFD2D
                tfd2d = TFD2D(self._current_array)
                spectre = tfd2d.calculerTFDSpectre()

                # Normalisation [0,1] — on évite la division par zéro si le spectre est vide
                max_val = spectre.max()
                norm_spectre = spectre / max_val if max_val > 0 else spectre

                # Conversion en QPixmap
                img_uint8 = (norm_spectre * 255).astype(np.uint8)
                h, w = img_uint8.shape
                from PyQt6.QtGui import QImage, QPixmap
                qimage = QImage(bytes(img_uint8.data), w, h, w, QImage.Format.Format_Grayscale8).copy()
                pixmap = QPixmap.fromImage(qimage)

                self.view.display_fft_spectrum(pixmap)
                print("Spectre FFT affiché dans l'overlay.")
            else:
                self.view.hide_fft_spectrum()
                print("Spectre FFT masqué.")

        except Exception as e:
            self.view.top_toolbar.btn_fft.setChecked(False)
            self.error_handler.handle_exception(e)
            return

    def handle_histogramme(self, checked: bool):
        """
        Affiche/masque le widget d'histogramme de l'image courante dans la zone d'overlay.
        Nécessite qu'une image soit chargée (_current_array != None).
        """
        try:
            if self._current_array is None:
                self.error_handler.show_error("Erreur", "Aucune image chargée")
                self.view.top_toolbar.btn_histo.setChecked(False)
                return

            if checked:
                # Désactiver la FFT si active
                self.view.top_toolbar.btn_fft.setChecked(False)
                self.view.hide_fft_spectrum()

                # Transmettre la matrice de l'image courante et le chemin du fichier d'origine
                original_file_path = self.main_controller._last_file_path
                self.view.display_histogram(self._current_array, original_file_path)
                print("Histogramme affiché dans l'overlay.")
            else:
                self.view.hide_histogram()
                print("Histogramme masqué.")

        except Exception as e:
            self.view.top_toolbar.btn_histo.setChecked(False)
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

            dialog = ClaheDialog(self.view)
            if dialog.exec():
                clip_limit, tile_grid = dialog.get_values()

                # Application du CLAHE avec les paramètres de la popup
                clahe = CLAHE(clip_limit, tile_grid, self._current_array)
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
        
    def handle_watershed(self, checked):
        """
        Applique la segmentation Watershed sur l'image courante.
        Nécessite qu'une image soit chargée (_current_array != None).
        """
        try:
            if self._current_array is None:
                self.error_handler.show_error("Erreur", "Aucune image chargée")
                self.view.left_toolbar.btn_watershed.setChecked(False)
                return
            if checked:
                self.main_controller.model.watershed_labels = None
                if hasattr(self.view, "watershed_area_label"):
                    self.view.watershed_area_label.hide()
                self.view.left_toolbar.btn_area.setChecked(False)
                default_seuil = getattr(self.main_controller, "last_pipette_threshold", None)
                dialog = WatershedDialog(self.view, default_seuil=default_seuil)
                if dialog.exec():
                    sigma, seuil_manuel, kernel_size, min_dist = dialog.get_values()

                    # 1. Filtrage Gaussien
                    image_filtree = FiltrageGaussien(sigma, self._current_array).filtrage()

                    # 2. Seuillage (manuel ou Otsu si seuil_manuel est None)
                    outil_seuillage = Seuillage(seuil_manuel)
                    masque, seuil_choisi = outil_seuillage.appliquer(image_filtree)

                    # 3. Masque des cavités internes
                    masque_rempli = ndimage.binary_fill_holes(masque > 0)
                    masque_rempli = ((masque_rempli * 255).astype(np.uint8) > 0) & (masque == 0)
                    masque_rempli = (masque_rempli * 255).astype(np.uint8) 

                    # 4. Nettoyage morphologique
                    masque_propre = MorphologieMathematique(kernel_size).ouverture(masque_rempli)

                    # 5. Segmentation Watershed
                    labels = SegmentationWatershed(min_dist).segmenter(masque_propre)

                    # 6. Rendu et superposition
                    image_affichage = cv2.normalize(labels, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
                    image_couleur = cv2.applyColorMap(image_affichage, cv2.COLORMAP_JET)

                    img_8bit = (self._current_array * 255).astype(np.uint8)
                    img_bgr = cv2.cvtColor(img_8bit, cv2.COLOR_GRAY2BGR)

                    # superposition transparente (overlay) sur les zones segmentées
                    mask_roi = labels > 0
                    overlay = img_bgr.copy()
                    blended = cv2.addWeighted(img_bgr, 0.6, image_couleur, 0.4, 0)
                    overlay[mask_roi] = blended[mask_roi]

                    self._display_numpy_array(overlay)
                    self.main_controller.model.watershed_labels = labels

                    print(f"Segmentation Watershed appliquée (sigma={sigma}, seuil={seuil_choisi}, noyau={kernel_size}, dist={min_dist})")
                else:
                    # Si l'utilisateur annule le dialogue, désélectionner le bouton
                    self.view.left_toolbar.btn_watershed.setChecked(False)

        except Exception as e:
            self.view.left_toolbar.btn_watershed.setChecked(False)
            self.error_handler.handle_exception(e)
            return