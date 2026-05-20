from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap , QGuiApplication


class MainView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Notre super projet e-santé")
        self.resize(500, 300)
        
        # 2. Centrage automatique de la fenêtre au milieu de l'écran
        self.center_on_screen()

        # composants
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # widgets
        self.btn_upload = QPushButton("Ouvrir une radiographie")
        self.layout.addWidget(self.btn_upload)

        # visualisation img
        self.image_display = QLabel("Aucune radiographie chargée.")
        self.image_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # style
        self.image_display.setStyleSheet(
            "background-color: #111111; "
            "color: #888888; "
            "border: 2px dashed #333333; "
            "min-height: 500px; "
            "font-size: 16px;"
        )
        self.layout.addWidget(self.image_display)

    def display_medical_image(self, file_path: str):
        """Affiche la radio dans le viewer et ajuste sa taille proprement."""
        pixmap = QPixmap(file_path)
        # Ajuste l'image aux dimensions du viewer (on garde les ratios) 
        scaled_pixmap = pixmap.scaled(
            self.image_display.width(),
            self.image_display.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.image_display.setPixmap(scaled_pixmap)
    def center_on_screen(self):
        """Calcule le centre de l'écran de l'utilisateur et y place la fenêtre."""
        screen = QGuiApplication.primaryScreen()
        if screen:
            screen_geometry = screen.geometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)