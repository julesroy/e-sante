from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal

class LeftToolbar(QWidget):
    gaussian_clicked = pyqtSignal()
    tfd2d_clicked = pyqtSignal()
    # AJOUT : Le signal pour restaurer l'image
    reset_image_clicked = pyqtSignal()

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
        
        # Connexions des clics aux signaux
        self.btn_origin.clicked.connect(self.reset_image_clicked.emit)  # AJOUT
        self.btn_gaussian.clicked.connect(self.gaussian_clicked.emit)
        self.btn_tfd2d.clicked.connect(self.tfd2d_clicked.emit)