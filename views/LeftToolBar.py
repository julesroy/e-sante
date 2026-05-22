from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal

class LeftToolbar(QWidget):
    reset_image_clicked = pyqtSignal()
    gaussian_clicked = pyqtSignal()
    tfd2d_clicked = pyqtSignal()
    clahe_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # AJOUT : Bouton "Origine" placé TOUT EN HAUT
        self.btn_origin = QPushButton("Image d'origine")
        self.btn_origin.setFixedWidth(120)
        self.layout.addWidget(self.btn_origin)
        
        # Bouton pour le filtre gaussien
        self.btn_gaussian = QPushButton("Filtre Gaussien")
        self.btn_gaussian.setFixedWidth(120)
        self.layout.addWidget(self.btn_gaussian)
        
        # Bouton pour la TFD2D
        self.btn_tfd2d = QPushButton("TFD 2D")
        self.btn_tfd2d.setFixedWidth(120)
        self.layout.addWidget(self.btn_tfd2d)
        
        # Bouton pour le CLAHE
        self.btn_clahe = QPushButton("CLAHE")
        self.btn_clahe.setFixedWidth(120)
        self.layout.addWidget(self.btn_clahe)

        # Connexions des clics aux signaux
        self.btn_origin.clicked.connect(self.reset_image_clicked.emit)
        self.btn_gaussian.clicked.connect(self.gaussian_clicked.emit)
        self.btn_tfd2d.clicked.connect(self.tfd2d_clicked.emit)
        self.btn_clahe.clicked.connect(self.clahe_clicked.emit)