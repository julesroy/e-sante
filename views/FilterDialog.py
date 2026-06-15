# views/FilterDialog.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QSlider, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal


class FilterDialog(QDialog):
    cutoff_changed = pyqtSignal(int)

    def __init__(self, parent=None, default_val=30, label_prefix="Fréquence de coupure : ", min_val=1, max_val=150):
        super().__init__(parent)
        self.label_prefix = label_prefix
        self.setWindowTitle("Filtre Fréquentiel")
        self.setFixedSize(300, 130)
        self.setWindowModality(Qt.WindowModality.WindowModal)

        layout = QVBoxLayout(self)

        self.label = QLabel(f"{self.label_prefix}{default_val}")
        layout.addWidget(self.label)

        # Création du Slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(min_val)
        self.slider.setMaximum(max_val)
        self.slider.setValue(default_val)
        layout.addWidget(self.slider)

        self.btn_ok = QPushButton("Appliquer")
        layout.addWidget(self.btn_ok)

        # Connexions passives
        self.slider.valueChanged.connect(lambda v: self.label.setText(f"{self.label_prefix}{v}"))
        self.slider.valueChanged.connect(self.cutoff_changed.emit)
        self.btn_ok.clicked.connect(self.accept)
