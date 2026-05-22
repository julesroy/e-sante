from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal

class LeftToolbar(QWidget):
    # On crée un signal personnalisé que le Controller pourra écouter
    gaussian_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Bouton pour le filtre gaussien
        self.btn_gaussian = QPushButton("Filtre Gaussien")
        self.btn_gaussian.setFixedWidth(120)
        self.layout.addWidget(self.btn_gaussian)
        
        # Quand on clique sur le bouton, on déclenche notre signal personnalisé
        self.btn_gaussian.clicked.connect(self.gaussian_clicked.emit)
        
        # Plus tard, le Dev 3 ajoutera ses boutons et ses signaux ici :
        # self.segmentation_clicked = pyqtSignal()
        # self.btn_seg.clicked.connect(self.segmentation_clicked.emit)