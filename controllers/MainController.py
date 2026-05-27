# ===== IMPORTS PYTHON STANDARD =====
from __future__ import annotations
import numpy as np

# ===== IMPORTS UNIQUEMENT POUR PYLANCE (jamais exécutés) =====
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from views.MainView import MainView

# ===== IMPORTS PYQT6 =====
from PyQt6.QtGui import QImage, QPixmap

# ===== IMPORTS DES SOUS-CONTROLLERS =====
from controllers.UploadController import UploadController
from controllers.FilterController import FilterController
from controllers.AnalysisController import AnalysisController
from controllers.ErrorController import ErrorController


class MainController(UploadController, FilterController, AnalysisController):

    # --------------------- Initialisation ------------------------
    def __init__(self, model, view: MainView):
        self.model = model
        self.view: MainView = view
        self.error_handler = ErrorController(parent_window=self.view)

        # Stockage de l'image courante sous forme numpy (float32 [0,1])
        self._current_array: np.ndarray | None = None
        
        # AJOUT : Stockage du QPixmap d'origine brute (en mémoire RAM)
        self._original_pixmap: QPixmap | None = None

        self._connect_signals()

    def _connect_signals(self):
        # Bouton d'upload connecté via le bloc toolbar supérieur
        self.view.top_toolbar.upload_clicked.connect(self.handle_upload)
        # Bouton du filtre gaussien connecté via le bloc toolbar latéral gauche
        self.view.left_toolbar.gaussian_clicked.connect(self.handle_gaussian)
        # Bouton TFD2D
        self.view.left_toolbar.tfd2d_clicked.connect(self.handle_tfd2d)
        # Bouton "Origine"
        self.view.left_toolbar.reset_image_clicked.connect(self.handle_reset_image)
        # Bouton CLAHE
        self.view.left_toolbar.clahe_clicked.connect(self.handle_clahe)
        # Bouton Filtre Passe-Bas
        self.view.left_toolbar.low_pass_clicked.connect(self.handle_passe_bas)
        # Bouton Filtre Passe-Haut
        self.view.left_toolbar.high_pass_clicked.connect(self.handle_passe_haut)

        
    # -------------------------------------------------------------

    # ----------------------- Affichage ---------------------------
    def _display_numpy_array(self, array: np.ndarray):
        """
        Convertit un np.ndarray float32 2D [0,1] en QPixmap
        et l'envoie directement au QLabel de la View.

        :param array: Matrice 2D numpy float32, valeurs entre 0 et 1.
        """
        # On dénormalise : on repasse de [0,1] à [0,255] pour QImage
        img_uint8 = (array * 255).astype(np.uint8)

        h, w = img_uint8.shape  # hauteur et largeur de l'image

        # QImage attend : data, largeur, hauteur, bytes_per_line, format
        # Format_Grayscale8 = 1 octet par pixel, parfait pour les images médicales
        # bytes() évite le warning Pylance sur memoryview
        qimage = QImage(bytes(img_uint8.data), w, h, w, QImage.Format.Format_Grayscale8)

        # .copy() force Qt à copier les données en mémoire
        # sans ça, l'image disparaît dès que la fonction se termine
        qimage = qimage.copy()

        # Conversion QImage -> QPixmap pour l'affichage dans un QLabel
        pixmap = QPixmap.fromImage(qimage)

        if self._original_pixmap is None:
            self._original_pixmap = pixmap.copy()  # On mémorise le pixmap d'origine pour les restaurations futures

        # "from_controller" signale à la View que le pixmap vient d'un traitement
        # et non d'un fichier disque — active le zoom sans recharger le fichier
        self.view.current_file_path = "from_controller"

        # Stockage du pixmap dans la View pour que le resize fonctionne correctement
        self.view.current_pixmap = pixmap

        # Recalcul du rendu avec zoom si nécessaire
        self.view.update_image_render()

    def handle_reset_image(self):
        """
        Réaffiche instantanément la radiographie d'origine 
        en écrasant l'image courante par le Pixmap d'origine gardé en cache RAM.
        """
        if self._original_pixmap is None:
            return  # Rien à réinitialiser si rien n'est chargé
            
        print("Réaffichage instantané de l'image d'origine depuis la RAM...")
        
        # On remet le facteur de zoom de la vue à 1.0 pour un reset visuel propre
        self.view.zoom_factor = 1.0
        
        # On donne à la vue une copie propre du Pixmap brut de départ
        self.view.current_pixmap = self._original_pixmap.copy()
        
        # On demande à la vue de mettre à jour le QLabel à l'écran
        self.view.update_image_render()