# views/WatershedDialog.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QDoubleSpinBox, QSpinBox, QCheckBox, QFormLayout
from PyQt6.QtCore import Qt

class WatershedDialog(QDialog):
    def __init__(self, parent=None, default_sigma=2.0, default_seuil_otsu=True, default_seuil=40, default_kernel=3, default_min_dist=50):
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
        self.sigma_spin.setValue(default_sigma)
        form_layout.addRow(QLabel("Sigma Gaussien :"), self.sigma_spin)

        # 2. Seuillage
        self.otsu_check = QCheckBox("Seuillage Otsu automatique")
        self.otsu_check.setChecked(default_seuil_otsu)
        form_layout.addRow(self.otsu_check)

        self.seuil_spin = QSpinBox()
        self.seuil_spin.setRange(1, 255)
        self.seuil_spin.setValue(default_seuil)
        self.seuil_spin.setEnabled(not default_seuil_otsu)
        form_layout.addRow(QLabel("Seuil manuel :"), self.seuil_spin)

        # Connecter la checkbox de seuil Otsu pour activer/désactiver le seuil manuel
        self.otsu_check.toggled.connect(lambda checked: self.seuil_spin.setEnabled(not checked))

        # 3. Taille du noyau pour morphologie mathématique
        self.kernel_spin = QSpinBox()
        self.kernel_spin.setRange(1, 99)
        self.kernel_spin.setSingleStep(2)
        self.kernel_spin.setValue(default_kernel)
        self.kernel_spin.editingFinished.connect(self._adjust_kernel_odd)
        form_layout.addRow(QLabel("Taille noyau morpho. (impair) :"), self.kernel_spin)

        # 4. Min distance marqueurs
        self.dist_spin = QSpinBox()
        self.dist_spin.setRange(1, 500)
        self.dist_spin.setValue(default_min_dist)
        form_layout.addRow(QLabel("Min distance marqueurs :"), self.dist_spin)

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
        return sigma, seuil, kernel, min_dist
