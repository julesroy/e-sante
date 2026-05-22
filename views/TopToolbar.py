from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal

class TopToolbar(QWidget):
    # Signaux pour l'import et le reset du zoom
    upload_clicked = pyqtSignal()
    reset_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        
        self.btn_upload = QPushButton("Ouvrir une radiographie")
        self.btn_zoom_reset = QPushButton("Ajuster")
        
        self.layout.addWidget(self.btn_upload)
        self.layout.addWidget(self.btn_zoom_reset)
        self.layout.addStretch()
        
        # Connexion des clics aux signaux correspondants
        self.btn_upload.clicked.connect(self.upload_clicked.emit)
        self.btn_zoom_reset.clicked.connect(self.reset_clicked.emit)