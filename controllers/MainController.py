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
    
    # --------------------- Connexion des signaux ------------------------
    def _connect_signals(self):
        self.view.top_toolbar.upload_clicked.connect(self.upload_ctrl.handle_upload)
        self.view.left_toolbar.gaussian_clicked.connect(self.filter_ctrl.handle_gaussian)
        self.view.left_toolbar.tfd2d_clicked.connect(self.analysis_ctrl.handle_tfd2d)
        self.view.left_toolbar.reset_image_clicked.connect(self.handle_reset_image)
        self.view.left_toolbar.clahe_clicked.connect(self.analysis_ctrl.handle_clahe)
        self.view.left_toolbar.contrast_slider_clicked.connect(self.analysis_ctrl.handle_contrast_slider)
        self.view.left_toolbar.watershed_clicked.connect(self.analysis_ctrl.handle_watershed)
        self.view.left_toolbar.low_pass_clicked.connect(self.filter_ctrl.handle_passe_bas)
        self.view.left_toolbar.high_pass_clicked.connect(self.filter_ctrl.handle_passe_haut)
        self.view.left_toolbar.sobel_clicked.connect(self.filter_ctrl.handle_sobel)
        self.view.left_toolbar.ruler_clicked.connect(self.ruler_ctrl.handle_ruler_toggle)
        self.view.left_toolbar.angle_clicked.connect(self.ruler_ctrl.handle_angle_toggle)
        self.view.left_toolbar.height_comp_clicked.connect(self.ruler_ctrl.handle_height_comp_toggle)
        self.view.left_toolbar.circle_roi_clicked.connect(self.ruler_ctrl.handle_circle_roi_toggle)
        self.view.left_toolbar.square_roi_clicked.connect(self.ruler_ctrl.handle_square_roi_toggle)
        self.view.left_toolbar.area_clicked.connect(self.ruler_ctrl.handle_area_calculation)
        self.view.top_toolbar.help_clicked.connect(self.handle_open_help)
    
    @property
    def _current_array(self): return self.model.current_array
    @_current_array.setter
    def _current_array(self, value): self.model.current_array = value

    @property
    def _original_pixmap(self): return self.model.original_pixmap
    @_original_pixmap.setter
    def _original_pixmap(self, value): self.model.original_pixmap = value

    @property
    def _contrast_base_array(self): return self.model.contrast_base_array
    @_contrast_base_array.setter
    def _contrast_base_array(self, value): self.model.contrast_base_array = value

    @property
    def _current_patient_id(self): return self.model.current_patient_id
    @_current_patient_id.setter
    def _current_patient_id(self, value): self.model.current_patient_id = value

    @property
    def _last_file_path(self): return self.model.last_file_path
    @_last_file_path.setter
    def _last_file_path(self, value): self.model.last_file_path = value

    def apply_contrast_realtime(self, facteur_contraste):
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
            print("[MainController] ONLINE - Synchronisation de la liste des patients...")
            # Chargement automatique au lancement de l'IHM
            manager = self.view.left_toolbar.patient_manager
            liste_patients = self.patient_ctrl.handle_charger_patients()
            manager.refresh_results(liste_patients)
        else:
            print("[MainController] OFFLINE - Fonctionnalités nécessitant la BDD sont désactivées.")

    def handle_reconnect(self):
        """
        Appelé quand l'utilisateur clique sur le bouton 'Reconnecter'.
        Reteste la connexion et met à jour l'UI.
        """
        print("[MainController] Tentative de reconnexion...")
        if check_connection():
            self.error_handler.show_info("Reconnexion réussie", "La connexion à la BDD est rétablie.")
            manager = self.view.left_toolbar.patient_manager
            manager.refresh_results(self.patient_ctrl.handle_charger_patients())
        else:
            self.error_handler.show_error("Hors-ligne", "Impossible de se connecter à la BDD.")

    def _display_numpy_array(self, array: np.ndarray):
        if array.dtype == np.uint8:
            img_uint8 = array
        else:
            img_uint8 = (array * 255).astype(np.uint8)

        if len(img_uint8.shape) == 2:
            h, w = img_uint8.shape
            qimage = QImage(bytes(img_uint8.data), w, h, w, QImage.Format.Format_Grayscale8).copy()
        elif len(img_uint8.shape) == 3 and img_uint8.shape[2] == 3:
            h, w, c = img_uint8.shape
            import cv2
            img_rgb = cv2.cvtColor(img_uint8, cv2.COLOR_BGR2RGB)
            bytes_per_line = 3 * w
            qimage = QImage(bytes(img_rgb.data), w, h, bytes_per_line, QImage.Format.Format_RGB888).copy()
        else:
            raise ValueError(f"Format d'image non supporté : {img_uint8.shape}")

        pixmap = QPixmap.fromImage(qimage)

        if self._original_pixmap is None:
            self._original_pixmap = pixmap.copy()

        self.view.current_file_path = "from_controller"
        self.view.current_pixmap = pixmap
        self.view.update_image_render()

    def handle_reset_image(self):
        if self._original_pixmap is None: return
        print("Réaffichage de l'image d'origine...")
        self.view.current_pixmap = self._original_pixmap.copy()
        self._contrast_base_array = None
        self.model.watershed_labels = None
        if hasattr(self.view, "watershed_area_label"):
            self.view.watershed_area_label.hide()
        self.view.left_toolbar.btn_contrast_slider.setChecked(False)
        self.view.left_toolbar.btn_contrast_slider.setChecked(True)
        self.view.update_image_render()

    def handle_open_help(self):
        import webbrowser
        import os
        base_dir = os.path.dirname(os.path.dirname(__file__))
        help_path = os.path.join(base_dir, "manuel", "manuel.html")
        if os.path.exists(help_path):
            webbrowser.open(f"file://{help_path}")
        else:
            self.error_handler.show_error("Erreur", f"Le guide d'utilisation est introuvable à l'emplacement :\n{help_path}")