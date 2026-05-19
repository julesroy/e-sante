from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt


class MainView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MVC PyQt6")
        self.resize(300, 200)

        # composants
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # widgets
        self.label_counter = QLabel("Compteur : 0")
        self.label_counter.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_increment = QPushButton("+1")
        self.btn_reset = QPushButton("Reset")

        # assemblage
        self.layout.addWidget(self.label_counter)
        self.layout.addWidget(self.btn_increment)
        self.layout.addWidget(self.btn_reset)

    def update_counter_display(self, value: int):
        """Met à jour l'affichage avec la nouvelle valeur."""
        self.label_counter.setText(f"Compteur : {value}")
