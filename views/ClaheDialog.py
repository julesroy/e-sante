# views/ClaheDialog.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDoubleSpinBox, QSpinBox, QFormLayout
from PyQt6.QtCore import Qt

class ClaheDialog(QDialog):
    def __init__(self, parent=None, default_clip_limit=5.0, default_grid_size=16):
        super().__init__(parent)
        self.setWindowTitle("Paramètres CLAHE")
        self.setFixedSize(320, 180)
        self.setWindowModality(Qt.WindowModality.WindowModal)

        # Style sombre moderne et cohérent avec style.qss
        self.setStyleSheet("""
            QDialog {
                background-color: #202020;
                border: 1px solid #3c3c3c;
                border-radius: 8px;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 12px;
                font-weight: bold;
            }
            QDoubleSpinBox, QSpinBox {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 5px;
                min-width: 70px;
            }
            QDoubleSpinBox:focus, QSpinBox:focus {
                border: 1px solid #00a2ed;
            }
            QPushButton {
                background-color: #00a2ed;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0082bc;
            }
            QPushButton:pressed {
                background-color: #006896;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        # Limitation de Contraste (Clip Limit)
        self.clip_label = QLabel("Limitation contraste :")
        self.clip_spin = QDoubleSpinBox()
        self.clip_spin.setRange(0.1, 40.0)
        self.clip_spin.setSingleStep(1)
        self.clip_spin.setValue(default_clip_limit)

        # Taille de la grille locale (Tile Grid Size)
        self.grid_label = QLabel("Taille de grille locale (n * n) :")
        
        self.grid_wh_spin = QSpinBox()
        self.grid_wh_spin.setRange(2, 128)
        self.grid_wh_spin.setValue(default_grid_size)

        grid_layout = QHBoxLayout()
        grid_layout.addWidget(self.grid_wh_spin)

        form_layout.addRow(self.clip_label, self.clip_spin)
        form_layout.addRow(self.grid_label, grid_layout)

        layout.addLayout(form_layout)

        # Boutons
        self.btn_ok = QPushButton("Appliquer")
        self.btn_ok.clicked.connect(self.accept)
        layout.addWidget(self.btn_ok)

    def get_values(self):
        return self.clip_spin.value(), (self.grid_wh_spin.value(), self.grid_wh_spin.value())
