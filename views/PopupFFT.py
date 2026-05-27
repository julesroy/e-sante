# views/FilterDialog.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QSlider, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal

class FilterDialog(QDialog):
    cutoff_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Filtre Fréquentiel")
        self.setFixedSize(300, 130)
        self.setWindowModality(Qt.WindowModality.WindowModal)

        layout = QVBoxLayout(self)

        self.label = QLabel("Fréquence de coupure : 30")
        layout.addWidget(self.label)

        # Création du Slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(150)
        self.slider.setValue(30)
        layout.addWidget(self.slider)

        self.btn_ok = QPushButton("Appliquer")
        layout.addWidget(self.btn_ok)

        # Connexions passives
        self.slider.valueChanged.connect(lambda v: self.label.setText(f"Fréquence de coupure : {v}"))
        self.slider.valueChanged.connect(self.cutoff_changed.emit)
        self.btn_ok.clicked.connect(self.accept)