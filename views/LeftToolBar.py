from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class LeftToolbar(QWidget):
    reset_image_clicked = pyqtSignal()
    gaussian_clicked = pyqtSignal()
    tfd2d_clicked = pyqtSignal()
    clahe_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        
        toolbar_layout = QVBoxLayout()
        toolbar_layout.setContentsMargins(10, 15, 10, 15)
        toolbar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(toolbar_layout)
        
        icon_font = QFont("FontAwesome", 14)
        button_size = 45 
        
        # 1. Btn"Origine"
        self.btn_origin = QPushButton("\uf0e2")
        self.btn_origin.setFont(icon_font)
        self.btn_origin.setFixedSize(button_size, button_size)
        self.btn_origin.setToolTip("Revenir à la radiographie brute d'origine")
        toolbar_layout.addWidget(self.btn_origin)
        
        # 2. Btn filtre gaussien
        self.btn_gaussian = QPushButton("\uf0d0")
        self.btn_gaussian.setFont(icon_font)
        self.btn_gaussian.setFixedSize(button_size, button_size)
        self.btn_gaussian.setToolTip("Appliquer le filtre Gaussien (Flou)")
        toolbar_layout.addWidget(self.btn_gaussian)
        
        # 3. Btn TFD2D 
        self.btn_tfd2d = QPushButton("\uf1fe")
        self.btn_tfd2d.setFont(icon_font)
        self.btn_tfd2d.setFixedSize(button_size, button_size)
        self.btn_tfd2d.setToolTip("Calculer la Transformée de Fourier (TFD 2D)")
        toolbar_layout.addWidget(self.btn_tfd2d)
        
        # 4. Btn CLAHE 
        self.btn_clahe = QPushButton("\uf042")
        self.btn_clahe.setFont(icon_font)
        self.btn_clahe.setFixedSize(button_size, button_size)
        self.btn_clahe.setToolTip("Améliorer les contrastes locaux (CLAHE)")
        toolbar_layout.addWidget(self.btn_clahe)

        # Connexions des clics aux signaux
        self.btn_origin.clicked.connect(self.reset_image_clicked.emit)
        self.btn_gaussian.clicked.connect(self.gaussian_clicked.emit)
        self.btn_tfd2d.clicked.connect(self.tfd2d_clicked.emit)
        self.btn_clahe.clicked.connect(self.clahe_clicked.emit)