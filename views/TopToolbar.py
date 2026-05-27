from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont

class TopToolbar(QWidget):
    # Signaux pour l'import et le reset du zoom
    upload_clicked = pyqtSignal()
    reset_clicked = pyqtSignal()
    low_pass_clicked = pyqtSignal()
    high_pass_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        toolbar_layout = QHBoxLayout()
        self.setLayout(toolbar_layout)
    
        icon_font = QFont("FontAwesome", 14)
        
        # 1. Btn import 
        self.btn_upload = QPushButton("\uf115")
        self.btn_upload.setFont(icon_font)
        self.btn_upload.setFixedSize(40, 40)
        self.btn_upload.setToolTip("Ouvrir une nouvelle radiographie")
        
        # 2. Btn reset
        self.btn_zoom_reset = QPushButton("\uf065")
        self.btn_zoom_reset.setFont(icon_font)
        self.btn_zoom_reset.setFixedSize(40, 40)
        self.btn_zoom_reset.setToolTip("Ajuster l'image à la taille de l'écran")

        # 3.Btn fréq PASSE-BAS
        self.btn_low_pass = QPushButton("\uf103")
        self.btn_low_pass.setFont(icon_font)
        self.btn_low_pass.setFixedSize(40, 40)
        self.btn_low_pass.setToolTip("Appliquer un Filtre Passe-Bas (Fréquentiel)")

        # 4. AJOUT : Btn fréq PASSE-HAUT
        #self.btn_high_pass = QPushButton("\uf102")
        #self.btn_high_pass.setFont(icon_font)
        #self.btn_high_pass.setFixedSize(40, 40)
        #self.btn_high_pass.setToolTip("Appliquer un Filtre Passe-Haut (Fréquentiel)")
        
        toolbar_layout.addWidget(self.btn_upload)
        toolbar_layout.addWidget(self.btn_zoom_reset)
        toolbar_layout.addWidget(self.btn_low_pass)
        #toolbar_layout.addWidget(self.btn_high_pass)
        toolbar_layout.addStretch()
        
        # connexion clics aux signaux
        self.btn_upload.clicked.connect(self.upload_clicked.emit)
        self.btn_zoom_reset.clicked.connect(self.reset_clicked.emit)
        self.btn_low_pass.clicked.connect(self.low_pass_clicked.emit)   # Connecté
        #self.btn_high_pass.clicked.connect(self.high_pass_clicked.emit)