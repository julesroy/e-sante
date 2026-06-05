from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QGridLayout
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class LeftToolbar(QWidget):
    reset_image_clicked = pyqtSignal()
    gaussian_clicked = pyqtSignal()
    sobel_clicked = pyqtSignal()
    tfd2d_clicked = pyqtSignal()
    low_pass_clicked = pyqtSignal()
    high_pass_clicked = pyqtSignal()
    clahe_clicked = pyqtSignal()
    contrast_slider_clicked = pyqtSignal(bool)
    ruler_clicked = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedWidth(160)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(5)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.main_layout)

        icon_font = QFont("FontAwesome", 12)
        button_size = 44

        # === FILTRES ===
        self.section_filters = QPushButton("Filtres  ▼")
        self.section_filters.setObjectName("SectionHeader")
        self.section_filters.setCheckable(True)  # Rendu mémorisable pour le QSS
        self.section_filters.setChecked(True)  # Sélectionné par défaut (ouvert)
        self.main_layout.addWidget(self.section_filters)

        self.filters_container = QWidget()
        self.grid_layout = QGridLayout(self.filters_container)
        self.grid_layout.setContentsMargins(8, 5, 8, 10)
        self.grid_layout.setSpacing(6)

        # Btn filtres
        self.btn_origin = QPushButton("\uf0e2")
        self.btn_origin.setFont(icon_font)
        self.btn_origin.setFixedSize(button_size, button_size)
        self.btn_origin.setToolTip("Afficher l'image d'origine")

        self.btn_gaussian = QPushButton("\uf0d0")
        self.btn_gaussian.setFont(icon_font)
        self.btn_gaussian.setFixedSize(button_size, button_size)
        self.btn_gaussian.setToolTip("Appliquer un filtre gaussien pour lisser l'image")

        self.btn_tfd2d = QPushButton("\uf1fe")
        self.btn_tfd2d.setFont(icon_font)
        self.btn_tfd2d.setFixedSize(button_size, button_size)
        self.btn_tfd2d.setToolTip("Afficher la Transformée de Fourier 2D de l'image")

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
        self.grid_layout.addWidget(self.btn_tfd2d, 0, 2)
        self.grid_layout.addWidget(self.btn_low_pass, 1, 0)
        self.grid_layout.addWidget(self.btn_high_pass, 1, 1)
        self.grid_layout.addWidget(self.btn_sobel, 1, 2)

        self.main_layout.addWidget(self.filters_container)

        # === CONTRASTE ===
        self.section_contrast = QPushButton("Contraste  ▶")
        self.section_contrast.setObjectName("SectionHeader")
        self.section_contrast.setCheckable(True)  # Rendu mémorisable pour le QSS
        self.main_layout.addWidget(self.section_contrast)

        self.contrast_container = QWidget()
        self.contrast_container.setVisible(False)
        self.grid_layout_contrast = QGridLayout(self.contrast_container)
        self.grid_layout_contrast.setContentsMargins(8, 5, 8, 10)
        self.grid_layout_contrast.setSpacing(6)

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

        self.main_layout.addWidget(self.contrast_container)

        # === MESURES ===
        self.section_measures = QPushButton("Mesures  ▶")
        self.section_measures.setObjectName("SectionHeader")
        self.section_measures.setCheckable(True)  # Rendu mémorisable pour le QSS
        self.main_layout.addWidget(self.section_measures)

        self.measures_container = QWidget()
        self.measures_container.setVisible(False)

        measures_layout = QVBoxLayout(self.measures_container)
        measures_layout.setContentsMargins(8, 5, 8, 10)

        self.btn_ruler = QPushButton("\uf545")
        self.btn_ruler.setFont(icon_font)
        self.btn_ruler.setFixedSize(button_size, button_size)
        self.btn_ruler.setToolTip("Mesurer la distance entre deux points en cm")
        self.btn_ruler.setCheckable(True)  # Devient bleu quand cliqué
        measures_layout.addWidget(self.btn_ruler)

        self.main_layout.addWidget(self.measures_container)


        # === CONFIG BTN GRILLE ===
        self.filter_buttons = [self.btn_origin, self.btn_gaussian, self.btn_tfd2d, self.btn_low_pass, self.btn_high_pass, self.btn_sobel, self.btn_clahe]
        for btn in self.filter_buttons:
            btn.setCheckable(True)
            btn.setAutoExclusive(True)

        self.contrast_buttons = [self.btn_clahe]
        for btn in self.contrast_buttons:
            btn.setCheckable(True)
            btn.setAutoExclusive(True)

        # === CONNEXIONS ===
        self.section_filters.clicked.connect(lambda: self.toggle_section(self.section_filters, self.filters_container, "Filtres"))
        self.section_contrast.clicked.connect(lambda: self.toggle_section(self.section_contrast, self.contrast_container, "Contraste"))
        self.section_measures.clicked.connect(lambda: self.toggle_section(self.section_measures, self.measures_container, "Mesures"))

        # === CONNEXIONS SIGNAUX ===
        self.btn_origin.clicked.connect(self.reset_image_clicked.emit)
        self.btn_gaussian.clicked.connect(self.gaussian_clicked.emit)
        self.btn_tfd2d.clicked.connect(self.tfd2d_clicked.emit)
        self.btn_low_pass.clicked.connect(self.low_pass_clicked.emit)
        self.btn_high_pass.clicked.connect(self.high_pass_clicked.emit)
        self.btn_sobel.clicked.connect(self.sobel_clicked.emit)
        self.btn_clahe.clicked.connect(self.clahe_clicked.emit)
        self.btn_ruler.clicked.connect(self.ruler_clicked.emit)

    def toggle_section(self, button, container, title_text):
        """Masque ou affiche le conteneur et force l'état Checked pour le QSS."""
        is_visible = container.isVisible()
        new_visibility = not is_visible
        container.setVisible(new_visibility)
        button.setChecked(new_visibility)
        if is_visible:
            button.setText(f"{title_text}  ▶")
        else:
            button.setText(f"{title_text}  ▼")
