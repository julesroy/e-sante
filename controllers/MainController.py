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
from controllers.PatientController import PatientController
from controllers.ImageController import ImageController
from controllers.RulerController import RulerController

# ===== IMPORTS DE LA CONNEXION A LA BDD =====
from database.connection import is_online, check_connection


class MainController:

    # --------------------- Initialisation ------------------------
    def __init__(self, model, view: MainView):
        self.model = model
        self.view: MainView = view
        self.error_handler = ErrorController(parent_window=self.view)

        # Instanciation des sous-contrôleurs par composition
        self.upload_ctrl = UploadController(self)
        self.filter_ctrl = FilterController(self)
        self.analysis_ctrl = AnalysisController(self)
        self.patient_ctrl = PatientController(self)
        self.image_ctrl = ImageController(self)
        self.ruler_ctrl = RulerController(self)

        # Rendre le controller accessible à la view
        self.view.controller = self

        self._connect_signals()
        self._check_db_mode()

    def _connect_signals(self):
        # Bouton d'upload connecté via le bloc toolbar supérieur
        self.view.top_toolbar.upload_clicked.connect(self.upload_ctrl.handle_upload)
        # Bouton du filtre gaussien connecté via le bloc toolbar latéral gauche
        self.view.left_toolbar.gaussian_clicked.connect(self.filter_ctrl.handle_gaussian)
        # Bouton TFD2D
        self.view.left_toolbar.tfd2d_clicked.connect(self.analysis_ctrl.handle_tfd2d)
        # Bouton "Origine"
        self.view.left_toolbar.reset_image_clicked.connect(self.handle_reset_image)
        # Bouton CLAHE
        self.view.left_toolbar.clahe_clicked.connect(self.analysis_ctrl.handle_clahe)
        # Bouton Contraste (slider)
        self.view.left_toolbar.contrast_slider_clicked.connect(self.analysis_ctrl.handle_contrast_slider)
        # Bouton Filtre Passe-Bas
        self.view.left_toolbar.low_pass_clicked.connect(self.filter_ctrl.handle_passe_bas)
        # Bouton Filtre Passe-Haut
        self.view.left_toolbar.high_pass_clicked.connect(self.filter_ctrl.handle_passe_haut)
        # bouton filtre de Sobel
        self.view.left_toolbar.sobel_clicked.connect(self.filter_ctrl.handle_sobel)
        # bouton règle de mesure
        self.view.left_toolbar.ruler_clicked.connect(self.ruler_ctrl.handle_ruler_toggle)

    # ----------------- Propriétés de l'état ----------------------
    @property
    def _current_array(self):
        return self.model.current_array

    @_current_array.setter
    def _current_array(self, value):
        self.model.current_array = value

    @property
    def _original_pixmap(self):
        return self.model.original_pixmap

    @_original_pixmap.setter
    def _original_pixmap(self, value):
        self.model.original_pixmap = value

    @property
    def _contrast_base_array(self):
        return self.model.contrast_base_array

    @_contrast_base_array.setter
    def _contrast_base_array(self, value):
        self.model.contrast_base_array = value

    @property
    def _current_patient_id(self):
        return self.model.current_patient_id

    @_current_patient_id.setter
    def _current_patient_id(self, value):
        self.model.current_patient_id = value

    @property
    def _last_file_path(self):
        return self.model.last_file_path

    @_last_file_path.setter
    def _last_file_path(self, value):
        self.model.last_file_path = value

    # ------------------- Délégations / Facades -------------------
    def apply_contrast_realtime(self, facteur_contraste):
        """Délègue l'ajustement du contraste en temps réel au contrôleur d'analyse."""
        self.analysis_ctrl.apply_contrast_realtime(facteur_contraste)

    # -------------------------------------------------------------

    # ------------------- BDD Online/Offline ----------------------
    def _check_db_mode(self):
        """
        Appelé une fois au démarrage.
        Teste la connexion BDD et demande à la View d'adapter l'UI.
        """
        online = is_online()

        if online:
            print("[MainController] ONLINE - Toutes les fonctionnalités sont actives.")
        else:
            print("[MainController] OFFLINE - Fonctionnalités nécessitant la BDD sont désactivées.")

    def handle_reconnect(self):
        """
        Appelé quand l'utilisateur clique sur le bouton 'Reconnecter'.
        Reteste la connexion et met à jour l'UI.
        """
        print("[MainController] Tentative de reconnexion...")
        success = check_connection()

        if success:
            self.error_handler.show_info("Reconnexion réussie", "La connexion à la BDD est rétablie.")
        else:
            self.error_handler.show_error("Hors-ligne", "Impossible de se connecter à la BDD. Veuillez réessayer ultérieurement.")

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

        # Format_Grayscale8 = 1 octet par pixel, parfait pour les images médicales
        qimage = QImage(bytes(img_uint8.data), w, h, w, QImage.Format.Format_Grayscale8)

        # .copy() force Qt à copier les données en mémoire
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

        # On donne à la vue une copie propre du Pixmap brut de départ

        self.view.current_pixmap = self._original_pixmap.copy()

        # On remet à 0 le slider de contraste
        self._contrast_base_array = None
        self.view.left_toolbar.btn_contrast_slider.setChecked(False)
        self.view.left_toolbar.btn_contrast_slider.setChecked(True)

        # On demande à la vue de mettre à jour le QLabel à l'écran
        self.view.update_image_render()
