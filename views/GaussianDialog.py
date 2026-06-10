# views/GaussianDialog.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QDoubleSpinBox, QFormLayout
from PyQt6.QtCore import Qt

class GaussianDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Filtre Gaussien")
        self.setFixedSize(300, 140)
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
            QDoubleSpinBox {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 5px;
                min-width: 70px;
            }
            QDoubleSpinBox:focus {
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
                margin-top: 10px;
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

        # Sigma (Écart-type)
        self.sigma_label = QLabel("Écart type (sigma) :")
        self.sigma_spin = QDoubleSpinBox()
        self.sigma_spin.setRange(0.1, 100.0)
        self.sigma_spin.setSingleStep(0.5)
        self.sigma_spin.setValue(1.0)

        form_layout.addRow(self.sigma_label, self.sigma_spin)
        layout.addLayout(form_layout)

        # Boutons
        self.btn_ok = QPushButton("Appliquer")
        self.btn_ok.clicked.connect(self.accept)
        layout.addWidget(self.btn_ok)

    def get_value(self):
        return self.sigma_spin.value()
