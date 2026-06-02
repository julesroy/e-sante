from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal , Qt
from PyQt6.QtGui import QFont

class TopToolbar(QWidget):
    upload_clicked = pyqtSignal()
    loupe_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(15, 10, 15, 10)
        toolbar_layout.setSpacing(10)
        self.setLayout(toolbar_layout)
    
        icon_font = QFont("FontAwesome", 14)
        
        self.btn_upload = QPushButton("\uf115")
        self.btn_upload.setFont(icon_font)
        self.btn_upload.setFixedSize(42, 42)
        self.btn_upload.setToolTip("Ouvrir une nouvelle radiographie")
        
        self.btn_loupe = QPushButton("\uf002")
        self.btn_loupe.setFont(icon_font)
        self.btn_loupe.setFixedSize(42, 42)
        self.btn_loupe.setToolTip("Activer la loupe de précision")
        
        toolbar_layout.addWidget(self.btn_upload)
        toolbar_layout.addWidget(self.btn_loupe)
        toolbar_layout.addStretch()
        
        self.btn_upload.clicked.connect(self.upload_clicked.emit)
        self.btn_loupe.clicked.connect(self.loupe_clicked.emit)