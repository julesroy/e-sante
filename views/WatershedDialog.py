# views/WatershedDialog.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QDoubleSpinBox, QSpinBox, QCheckBox, QFormLayout
from PyQt6.QtCore import Qt

class WatershedDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Paramètres Watershed")
        self.setFixedSize(340, 300)
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
                min-width: 80px;
            }
            QDoubleSpinBox:focus, QSpinBox:focus {
                border: 1px solid #00a2ed;
            }
            QCheckBox {
                color: #e0e0e0;
                font-size: 12px;
                font-weight: bold;
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
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        # 1. Sigma du filtre Gaussien
        self.sigma_spin = QDoubleSpinBox()
        self.sigma_spin.setRange(0.1, 50.0)
        self.sigma_spin.setSingleStep(0.5)
        self.sigma_spin.setValue(2.0)
        form_layout.addRow(QLabel("Sigma Gaussien :"), self.sigma_spin)

        # 2. Seuillage
        self.otsu_check = QCheckBox("Seuillage Otsu automatique")
        self.otsu_check.setChecked(True)
        form_layout.addRow(self.otsu_check)

        self.seuil_spin = QSpinBox()
        self.seuil_spin.setRange(1, 255)
        self.seuil_spin.setValue(40)
        self.seuil_spin.setEnabled(False)  # Désactivé par défaut car Otsu est coché
        form_layout.addRow(QLabel("Seuil manuel :"), self.seuil_spin)

        # Connecter la checkbox de seuil Otsu pour activer/désactiver le seuil manuel
        self.otsu_check.toggled.connect(lambda checked: self.seuil_spin.setEnabled(not checked))

        # 3. Taille du noyau pour morphologie mathématique
        self.kernel_spin = QSpinBox()
        self.kernel_spin.setRange(1, 99)
        self.kernel_spin.setSingleStep(2)
        self.kernel_spin.setValue(3)
        self.kernel_spin.editingFinished.connect(self._adjust_kernel_odd)
        form_layout.addRow(QLabel("Taille noyau morpho. (impair) :"), self.kernel_spin)

        # 4. Min distance marqueurs
        self.dist_spin = QSpinBox()
        self.dist_spin.setRange(1, 500)
        self.dist_spin.setValue(50)
        form_layout.addRow(QLabel("Min distance marqueurs :"), self.dist_spin)

        # 5. Supprimer les bordures
        self.border_check = QCheckBox("Supprimer les bordures")
        self.border_check.setChecked(True)
        form_layout.addRow(self.border_check)

        layout.addLayout(form_layout)

        # Bouton Appliquer
        self.btn_ok = QPushButton("Appliquer")
        self.btn_ok.clicked.connect(self.accept)
        layout.addWidget(self.btn_ok)

    def _adjust_kernel_odd(self):
        val = self.kernel_spin.value()
        if val % 2 == 0:
            self.kernel_spin.setValue(val + 1)

    def get_values(self):
        sigma = self.sigma_spin.value()
        seuil = None if self.otsu_check.isChecked() else self.seuil_spin.value()
        kernel = self.kernel_spin.value()
        min_dist = self.dist_spin.value()
        supprimer_bordures = self.border_check.isChecked()
        return sigma, seuil, kernel, min_dist, supprimer_bordures
