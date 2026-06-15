from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGridLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon
import os
from views.PatientManagerWidget import PatientManagerWidget

# ===== IMPORT HELPER ======
from utils.paths import resource_path


class SectionHeaderButton(QPushButton):
    def __init__(self, title, is_expanded=False, parent=None):
        super().__init__(parent)
        self.setObjectName("SectionHeader")
        self.setCheckable(True)

        # Layout interne flex-like
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(0)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: white; font-weight: bold; background-color: transparent;")
        
        self.arrow_label = QLabel("▼" if is_expanded else "▶")
        self.arrow_label.setStyleSheet("color: white; font-weight: bold; background-color: transparent;")

        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addWidget(self.arrow_label)

        # Ignore mouse events on labels so they pass through to the button
        self.title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.arrow_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def set_expanded(self, expanded):
        self.arrow_label.setText("▼" if expanded else "▶")


class LeftToolbar(QWidget):
    reset_image_clicked = pyqtSignal()
    gaussian_clicked = pyqtSignal(bool)
    sobel_clicked = pyqtSignal(bool)
    low_pass_clicked = pyqtSignal(bool)
    high_pass_clicked = pyqtSignal(bool)
    clahe_clicked = pyqtSignal(bool)
    contrast_slider_clicked = pyqtSignal(bool)
    watershed_clicked = pyqtSignal(bool)
    ruler_clicked = pyqtSignal(bool)
    angle_clicked = pyqtSignal(bool)
    height_comp_clicked = pyqtSignal(bool)
    circle_roi_clicked = pyqtSignal(bool)
    square_roi_clicked = pyqtSignal(bool)
    area_clicked = pyqtSignal(bool)
    pipette_clicked = pyqtSignal(bool)
    pen_clicked = pyqtSignal(bool)
    text_clicked = pyqtSignal(bool)
    color_clicked = pyqtSignal()
    clear_annotations_clicked = pyqtSignal()
    save_to_patient_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedWidth(170)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(20)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.main_layout)

        icon_font = QFont("FontAwesome", 12)
        button_size = 40

        # === FILTRES ===
        self.section_filters = SectionHeaderButton("Filtres", is_expanded=True)
        self.section_filters.setChecked(True)
        self.main_layout.addWidget(self.section_filters)

        self.filters_container = QWidget()
        self.grid_layout = QGridLayout(self.filters_container)
        self.grid_layout.setContentsMargins(12, 8, 8, 12)
        self.grid_layout.setSpacing(6)
        self.grid_layout.setRowMinimumHeight(0, button_size)
        self.grid_layout.setRowMinimumHeight(1, button_size)

        self.btn_origin = QPushButton("\uf0e2")
        self.btn_origin.setFont(icon_font)
        self.btn_origin.setFixedSize(button_size, button_size)
        self.btn_origin.setToolTip("Afficher l'image d'origine")

        self.btn_gaussian = QPushButton("\uf0d0")
        self.btn_gaussian.setFont(icon_font)
        self.btn_gaussian.setFixedSize(button_size, button_size)
        self.btn_gaussian.setToolTip("Appliquer un filtre gaussien pour lisser l'image")

        self.btn_low_pass = QPushButton("\uf103")
        self.btn_low_pass.setFont(icon_font)
        self.btn_low_pass.setFixedSize(button_size, button_size)
        self.btn_low_pass.setToolTip("Appliquer un filtre passe-bas pour ne conserver que les basses fréquences (lissage)")

        self.btn_high_pass = QPushButton("\uf102")
        self.btn_high_pass.setFont(icon_font)
        self.btn_high_pass.setFixedSize(button_size, button_size)
        self.btn_high_pass.setToolTip("Appliquer un filtre passe-haut pour ne conserver que les hautes fréquences (détails)")

        self.btn_sobel = QPushButton("\uf096")
        self.btn_sobel.setFont(icon_font)
        self.btn_sobel.setFixedSize(button_size, button_size)
        self.btn_sobel.setToolTip("Appliquer un filtre de Sobel pour détecter les contours")

        self.grid_layout.addWidget(self.btn_origin, 0, 0)
        self.grid_layout.addWidget(self.btn_gaussian, 0, 1)
        self.grid_layout.addWidget(self.btn_low_pass, 0, 2)
        self.grid_layout.addWidget(self.btn_high_pass, 1, 0)
        self.grid_layout.addWidget(self.btn_sobel, 1, 1)

        self.main_layout.addWidget(self.filters_container)

        # === CONTRASTE ===
        self.section_contrast = SectionHeaderButton("Contraste", is_expanded=False)
        self.main_layout.addWidget(self.section_contrast)

        self.contrast_container = QWidget()
        self.contrast_container.setVisible(False)
        self.grid_layout_contrast = QGridLayout(self.contrast_container)
        self.grid_layout_contrast.setContentsMargins(12, 8, 8, 12)
        self.grid_layout_contrast.setSpacing(6)
        self.grid_layout_contrast.setRowMinimumHeight(0, button_size)

        self.btn_clahe = QPushButton("\uf042")
        self.btn_clahe.setFont(icon_font)
        self.btn_clahe.setFixedSize(button_size, button_size)
        self.btn_clahe.setToolTip("Appliquer un filtre CLAHE pour améliorer le contraste")
        self.grid_layout_contrast.addWidget(self.btn_clahe, 0, 0)

        self.btn_contrast_slider = QPushButton("\uf0b2")
        self.btn_contrast_slider.setFont(icon_font)
        self.btn_contrast_slider.setFixedSize(button_size, button_size)
        self.btn_contrast_slider.setToolTip("Ajuster le contraste avec un slider")
        self.btn_contrast_slider.setCheckable(True)
        self.btn_contrast_slider.clicked.connect(self.contrast_slider_clicked.emit)
        self.grid_layout_contrast.addWidget(self.btn_contrast_slider, 0, 1)

        self.btn_watershed = QPushButton("\uf0b0")
        self.btn_watershed.setFont(icon_font)
        self.btn_watershed.setFixedSize(button_size, button_size)
        self.btn_watershed.setToolTip("Appliquer la segmentation Watershed")
        self.grid_layout_contrast.addWidget(self.btn_watershed, 0, 2)

        self.main_layout.addWidget(self.contrast_container)

        # === MESURES ===
        self.section_measures = SectionHeaderButton("Mesures", is_expanded=False)
        self.main_layout.addWidget(self.section_measures)

        self.measures_container = QWidget()
        self.measures_container.setVisible(False)
        self.grid_layout_measures = QGridLayout(self.measures_container)
        self.grid_layout_measures.setContentsMargins(12, 8, 8, 12)
        self.grid_layout_measures.setSpacing(6)
        self.grid_layout_measures.setRowMinimumHeight(0, button_size)
        self.grid_layout_measures.setRowMinimumHeight(1, button_size)
        self.grid_layout_measures.setRowMinimumHeight(2, button_size)

        self.btn_ruler = QPushButton()
        ruler_icon_path = resource_path(os.path.join("assets", "icons", "ruler-icon.svg"))
        if os.path.exists(ruler_icon_path):
            self.btn_ruler.setIcon(QIcon(ruler_icon_path))
            self.btn_ruler.setIconSize(QSize(18, 18))
        self.btn_ruler.setFixedSize(button_size, button_size)
        self.btn_ruler.setToolTip("Mesurer la distance entre deux points en cm")
        self.btn_ruler.setCheckable(True)

        self.btn_angle = QPushButton()
        icon_path = resource_path(os.path.join("assets", "icons", "angle-icon.svg"))
        if os.path.exists(icon_path):
            self.btn_angle.setIcon(QIcon(icon_path))
            self.btn_angle.setIconSize(QSize(18, 18))
        self.btn_angle.setFixedSize(button_size, button_size)
        self.btn_angle.setToolTip("Mesurer l'angle entre deux droites")
        self.btn_angle.setCheckable(True)

        self.btn_height_comp = QPushButton("\uf07d")
        self.btn_height_comp.setFont(icon_font)
        self.btn_height_comp.setFixedSize(button_size, button_size)
        self.btn_height_comp.setToolTip("Comparer la hauteur entre deux plans")
        self.btn_height_comp.setCheckable(True)

        self.btn_area = QPushButton("\uf1ec")
        self.btn_area.setFont(icon_font)
        self.btn_area.setFixedSize(button_size, button_size)
        self.btn_area.setToolTip("Calculer les aires du Watershed")
        self.btn_area.setCheckable(True)

        self.btn_circle_roi = QPushButton("\uf111")
        self.btn_circle_roi.setFont(icon_font)
        self.btn_circle_roi.setFixedSize(button_size, button_size)
        self.btn_circle_roi.setToolTip("ROI Cercle : Statistiques d'intensité et aire")
        self.btn_circle_roi.setCheckable(True)

        self.btn_square_roi = QPushButton("\uf0c8")
        self.btn_square_roi.setFont(icon_font)
        self.btn_square_roi.setFixedSize(button_size, button_size)
        self.btn_square_roi.setToolTip("ROI Carré : Statistiques d'intensité et aire")
        self.btn_square_roi.setCheckable(True)

        self.btn_pipette = QPushButton("\uf1fb")
        self.btn_pipette.setFont(icon_font)
        self.btn_pipette.setFixedSize(button_size, button_size)
        self.btn_pipette.setToolTip("Relever le niveau de gris (pipette)")
        self.btn_pipette.setCheckable(True)

        self.grid_layout_measures.addWidget(self.btn_ruler, 0, 0)
        self.grid_layout_measures.addWidget(self.btn_angle, 0, 1)
        self.grid_layout_measures.addWidget(self.btn_height_comp, 0, 2)
        self.grid_layout_measures.addWidget(self.btn_area, 1, 0)
        self.grid_layout_measures.addWidget(self.btn_circle_roi, 1, 1)
        self.grid_layout_measures.addWidget(self.btn_square_roi, 1, 2)
        self.grid_layout_measures.addWidget(self.btn_pipette, 2, 0)

        self.main_layout.addWidget(self.measures_container)

        # === ANNOTATIONS ===
        self.section_annotations = SectionHeaderButton("Annotations", is_expanded=False)
        self.main_layout.addWidget(self.section_annotations)

        self.annotations_container = QWidget()
        self.annotations_container.setVisible(False)
        self.grid_layout_annotations = QGridLayout(self.annotations_container)
        self.grid_layout_annotations.setContentsMargins(12, 8, 8, 12)
        self.grid_layout_annotations.setSpacing(6)
        self.grid_layout_annotations.setRowMinimumHeight(0, button_size)

        self.btn_pen = QPushButton("\uf040")
        self.btn_pen.setFont(icon_font)
        self.btn_pen.setFixedSize(button_size, button_size)
        self.btn_pen.setToolTip("Stylo : Annoter l'image à main levée")
        self.btn_pen.setCheckable(True)

        self.btn_text = QPushButton("\uf031")
        self.btn_text.setFont(icon_font)
        self.btn_text.setFixedSize(button_size, button_size)
        self.btn_text.setToolTip("Texte : Ajouter une annotation textuelle")
        self.btn_text.setCheckable(True)

        self.btn_color = QPushButton("\uf1fc")
        self.btn_color.setFont(icon_font)
        self.btn_color.setFixedSize(button_size, button_size)
        self.btn_color.setToolTip("Couleur : Choisir la couleur active")
        self.btn_color.setStyleSheet("background-color: #ff0000; border: 2px solid white; border-radius: 4px; color: white;")

        self.btn_clear_annotations = QPushButton("\uf1f8")
        self.btn_clear_annotations.setFont(icon_font)
        self.btn_clear_annotations.setFixedSize(button_size, button_size)
        self.btn_clear_annotations.setToolTip("Effacer : Supprimer toutes les annotations")

        self.btn_save_to_patient = QPushButton("\uf0c7")
        self.btn_save_to_patient.setFont(icon_font)
        self.btn_save_to_patient.setFixedSize(button_size, button_size)
        self.btn_save_to_patient.setToolTip("Sauvegarder dans le dossier du patient")

        self.grid_layout_annotations.addWidget(self.btn_pen, 0, 0)
        self.grid_layout_annotations.addWidget(self.btn_text, 0, 1)
        self.grid_layout_annotations.addWidget(self.btn_color, 0, 2)
        self.grid_layout_annotations.addWidget(self.btn_clear_annotations, 1, 0)
        self.grid_layout_annotations.addWidget(self.btn_save_to_patient, 1, 1)

        self.main_layout.addWidget(self.annotations_container)

        # === DOSSIERS (PATIENTS BDD) ===
        self.section_folders = SectionHeaderButton("Dossiers", is_expanded=False)
        self.main_layout.addWidget(self.section_folders)

        self.folders_container = QWidget()
        self.folders_container.setVisible(False)
        folders_layout = QVBoxLayout(self.folders_container)
        folders_layout.setContentsMargins(12, 8, 8, 12)
        folders_layout.setSpacing(8)

        self.patient_manager = PatientManagerWidget(main_view=parent, parent=self.folders_container)
        folders_layout.addWidget(self.patient_manager)

        self.main_layout.addWidget(self.folders_container)

        # === CONFIG BTN GRILLE ===
        self.filter_buttons = [self.btn_gaussian, self.btn_low_pass, self.btn_high_pass, self.btn_sobel, self.btn_clahe]
        for btn in self.filter_buttons:
            btn.setCheckable(True)

        self.contrast_buttons = [self.btn_clahe, self.btn_watershed, self.btn_contrast_slider]
        for btn in self.contrast_buttons:
            btn.setCheckable(True)

        # === CONNEXIONS ===
        self.section_filters.clicked.connect(lambda: self.toggle_section(self.section_filters, self.filters_container, "Filtres"))
        self.section_contrast.clicked.connect(lambda: self.toggle_section(self.section_contrast, self.contrast_container, "Contraste"))
        self.section_measures.clicked.connect(lambda: self.toggle_section(self.section_measures, self.measures_container, "Mesures"))
        self.section_annotations.clicked.connect(lambda: self.toggle_section(self.section_annotations, self.annotations_container, "Annotations"))
        self.section_folders.clicked.connect(lambda: self.toggle_section(self.section_folders, self.folders_container, "Dossiers"))

        # === CONNEXIONS SIGNAUX ===
        self.btn_origin.clicked.connect(self._handle_origin_clicked)
        self.btn_gaussian.clicked.connect(lambda: self._on_button_clicked(self.btn_gaussian, self.gaussian_clicked))
        self.btn_low_pass.clicked.connect(lambda: self._on_button_clicked(self.btn_low_pass, self.low_pass_clicked))
        self.btn_high_pass.clicked.connect(lambda: self._on_button_clicked(self.btn_high_pass, self.high_pass_clicked))
        self.btn_sobel.clicked.connect(lambda: self._on_button_clicked(self.btn_sobel, self.sobel_clicked))
        self.btn_clahe.clicked.connect(lambda: self._on_button_clicked(self.btn_clahe, self.clahe_clicked))
        self.btn_watershed.clicked.connect(lambda: self._on_button_clicked(self.btn_watershed, self.watershed_clicked))
        self.btn_ruler.clicked.connect(self.ruler_clicked.emit)
        self.btn_angle.clicked.connect(self.angle_clicked.emit)
        self.btn_height_comp.clicked.connect(self.height_comp_clicked.emit)
        self.btn_circle_roi.clicked.connect(self.circle_roi_clicked.emit)
        self.btn_square_roi.clicked.connect(self.square_roi_clicked.emit)
        self.btn_area.clicked.connect(self.area_clicked.emit)
        self.btn_pipette.clicked.connect(self.pipette_clicked.emit)
        self.btn_pen.clicked.connect(lambda: self._on_button_clicked(self.btn_pen, self.pen_clicked))
        self.btn_text.clicked.connect(lambda: self._on_button_clicked(self.btn_text, self.text_clicked))
        self.btn_color.clicked.connect(self.color_clicked.emit)
        self.btn_clear_annotations.clicked.connect(self.clear_annotations_clicked.emit)
        self.btn_save_to_patient.clicked.connect(self.save_to_patient_clicked.emit)

    def toggle_section(self, button, container, title_text):
        """Masque ou affiche le conteneur et force l'état Checked pour le QSS."""
        is_visible = container.isVisible()
        new_visibility = not is_visible
        container.setVisible(new_visibility)
        button.setChecked(new_visibility)
        button.set_expanded(new_visibility)

    def uncheck_all_processing_buttons(self, except_btn=None):
        """Désélectionne tous les boutons de traitement/contraste sauf celui spécifié."""
        buttons = [
            self.btn_gaussian,
            self.btn_low_pass,
            self.btn_high_pass,
            self.btn_sobel,
            self.btn_clahe,
            self.btn_watershed,
            self.btn_contrast_slider
        ]
        for btn in buttons:
            if btn != except_btn:
                btn.setChecked(False)

    def _on_button_clicked(self, button, signal):
        checked = button.isChecked()
        if checked:
            self.uncheck_all_processing_buttons(except_btn=button)
        signal.emit(checked)

    def _handle_origin_clicked(self):
        self.uncheck_all_processing_buttons()
        self.reset_image_clicked.emit()