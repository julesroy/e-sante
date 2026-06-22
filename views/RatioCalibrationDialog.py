# views/RatioCalibrationDialog.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDoubleSpinBox, QFormLayout, QComboBox
from PyQt6.QtCore import Qt


class RatioCalibrationDialog(QDialog):
    def __init__(self, parent=None, default_ratio=None, image_width=None):
        super().__init__(parent)
        self.setWindowTitle("Calibration de mesure")
        self.setFixedSize(380, 240)
        self.setWindowModality(Qt.WindowModality.WindowModal)

        # Définition de l'object name pour appliquer le style QSS externe
        self.setObjectName("RatioCalibrationDialog")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        info_label = QLabel("Saisissez le ratio pixel/mm ou choisissez un préréglage pour convertir les pixels en millimètres :")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        self.image_width = image_width if image_width else 1024

        # Préréglages basés sur le champ de vue (FOV) en mm
        self.preset_combo = QComboBox()
        self.preset_combo.addItem("Valeur personnalisée", None)

        # Calcul des ratios pour des FOV typiques en mm
        fov_thorax_large = 450.0  # 45 cm
        fov_thorax_std = 400.0   # 40 cm
        fov_tibia = 300.0        # 30 cm
        fov_cerveau = 220.0      # 22 cm
        fov_main_pied = 150.0    # 15 cm

        ratio_thorax_large = self.image_width / fov_thorax_large
        ratio_thorax_std = self.image_width / fov_thorax_std
        ratio_tibia = self.image_width / fov_tibia
        ratio_cerveau = self.image_width / fov_cerveau
        ratio_main_pied = self.image_width / fov_main_pied

        self.preset_combo.addItem(f"Thorax (Largeur ~45 cm) : {ratio_thorax_large:.3f} px/mm", ratio_thorax_large)
        self.preset_combo.addItem(f"Thorax (Largeur ~40 cm) : {ratio_thorax_std:.3f} px/mm", ratio_thorax_std)
        self.preset_combo.addItem(f"Tibia (Largeur ~30 cm) : {ratio_tibia:.3f} px/mm", ratio_tibia)
        self.preset_combo.addItem(f"Cerveau (Largeur ~22 cm) : {ratio_cerveau:.3f} px/mm", ratio_cerveau)
        self.preset_combo.addItem(f"Main / Pied (Largeur ~15 cm) : {ratio_main_pied:.3f} px/mm", ratio_main_pied)

        # Ratio personnalisé
        self.ratio_spin = QDoubleSpinBox()
        self.ratio_spin.setRange(0.001, 1000.0)
        self.ratio_spin.setDecimals(4)
        self.ratio_spin.setSingleStep(0.1)

        # Sélectionner la valeur initiale par défaut (Thorax standard par défaut)
        initial_val = default_ratio if default_ratio is not None else ratio_thorax_std
        self.ratio_spin.setValue(initial_val)

        # Tenter de faire correspondre la valeur initiale à un préréglage existant
        self._select_matching_preset(initial_val)

        # Connecter le combo pour mettre à jour le spin box
        self.preset_combo.currentIndexChanged.connect(self.on_preset_changed)

        form_layout.addRow(QLabel("Préréglages :"), self.preset_combo)
        form_layout.addRow(QLabel("Ratio (px/mm) :"), self.ratio_spin)
        layout.addLayout(form_layout)

        # Boutons OK / Annuler
        btn_layout = QHBoxLayout()
        self.btn_cancel = QPushButton("Annuler")
        # Définition de l'object name du bouton annuler pour son style QSS spécifique
        self.btn_cancel.setObjectName("CancelBtn")
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_ok = QPushButton("Appliquer")
        self.btn_ok.clicked.connect(self.accept)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_ok)
        layout.addLayout(btn_layout)

    def _select_matching_preset(self, val):
        for i in range(1, self.preset_combo.count()):
            preset_val = self.preset_combo.itemData(i)
            if preset_val is not None and abs(preset_val - val) < 0.01:
                self.preset_combo.setCurrentIndex(i)
                return
        self.preset_combo.setCurrentIndex(0)

    def on_preset_changed(self, index):
        val = self.preset_combo.itemData(index)
        if val is not None:
            self.ratio_spin.setValue(val)

    def get_value(self):
        return self.ratio_spin.value()
