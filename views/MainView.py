from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPixmap, QGuiApplication


# --- Zoom et déplacement ---
class MedicalImageVisualizer(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background-color: #111111; border: 2px dashed #333333;")

        # Référence vers la vue principale pour accéder au zoom_factor
        self.main_view = parent

    def wheelEvent(self, event):
        """scroll molette = zoom fluide et surle curseur"""
        if not self.main_view or not self.main_view.current_file_path:
            event.ignore()
            return

        modifiers = event.modifiers()

        # Récupération des deux axes de la molette pour être compatible avec toutes les souris/touchpads
        delta_y = event.angleDelta().y()
        delta_x = event.angleDelta().x()

        # On utilise le delta vertical s'il existe, sinon le horizontal (pour certaines molettes)
        delta = delta_y if delta_y != 0 else delta_x
        pas_deplacement = 15

        # 1. SHIFT + MOLETTE -> Déplacement vertical(Haut / Bas)
        if modifiers == Qt.KeyboardModifier.ShiftModifier:
            v_bar = self.verticalScrollBar()
            if delta > 0:
                v_bar.setValue(v_bar.value() - pas_deplacement)  # Monte
            else:
                v_bar.setValue(v_bar.value() + pas_deplacement)  # Descend
            event.accept()
            return

        # 2. ALT + MOLETTE -> Déplacement horizontal (Gauche / Droite)
        elif modifiers == Qt.KeyboardModifier.AltModifier:
            h_bar = self.horizontalScrollBar()
            if delta > 0:
                h_bar.setValue(h_bar.value() - pas_deplacement)  # Gauche
            else:
                h_bar.setValue(h_bar.value() + pas_deplacement)  # Droite
            event.accept()
            return

        # 3. MOLETTE -> Zoom centré sur le curseur
        elif modifiers == Qt.KeyboardModifier.NoModifier:
            h_bar = self.horizontalScrollBar()
            v_bar = self.verticalScrollBar()
            mouse_pos_viewport = event.position().toPoint()
            content_widget = self.widget()
            if not content_widget:
                event.ignore()
                return
            mouse_pos_in_label = content_widget.mapFrom(self.viewport(), mouse_pos_viewport)
            old_zoom = self.main_view.zoom_factor
            if delta > 0:
                self.main_view.zoom_factor *= 1.06  # Zoom avant
            else:
                self.main_view.zoom_factor /= 1.06  # Dézoom arrière
            self.main_view.zoom_factor = max(0.5, min(self.main_view.zoom_factor, 8.0))
            if old_zoom != self.main_view.zoom_factor:
                # Blocage des scrollbars pour empêcher PyQt de faire n'imp
                h_bar.blockSignals(True)
                v_bar.blockSignals(True)
                self.main_view.update_image_render()
                zoom_ratio = self.main_view.zoom_factor / old_zoom
                new_x_in_label = mouse_pos_in_label.x() * zoom_ratio
                new_y_in_label = mouse_pos_in_label.y() * zoom_ratio

                # On replace les scrollbars pour réaligner le pixel ciblé sur le curseur physique de l'écran
                new_scroll_x = int(new_x_in_label - mouse_pos_viewport.x())
                new_scroll_y = int(new_y_in_label - mouse_pos_viewport.y())

                h_bar.setValue(new_scroll_x)
                v_bar.setValue(new_scroll_y)

                h_bar.blockSignals(False)
                v_bar.blockSignals(False)

            event.accept()
        else:
            event.ignore()


# --- FENÊTRE PRINCIPALE ---
class MainView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Notre super projet e-santé")
        self.resize(600, 500)

        # Variables pour stocker l'image active + zoom
        self.current_file_path = None
        self.zoom_factor = 1.0

        # Centrage automatique au milieu de l'écran
        self.center_on_screen()

        # composants
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # widgets
        self.toolbar_layout = QHBoxLayout()
        self.btn_upload = QPushButton("Ouvrir une radiographie")
        self.btn_zoom_reset = QPushButton("Ajuster")
        self.toolbar_layout.addWidget(self.btn_upload)
        self.toolbar_layout.addWidget(self.btn_zoom_reset)
        self.layout.addLayout(self.toolbar_layout)

        # visualisation img via notre classe spécialisée
        self.scroll_area = MedicalImageVisualizer(self)

        self.image_display = QLabel("Aucune radiographie chargée.")
        self.image_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_display.setStyleSheet("color: #888888; font-size: 16px; background-color: transparent;")

        # zone scrollable
        self.scroll_area.setWidget(self.image_display)
        self.layout.addWidget(self.scroll_area)

        # connexion bouton d'ajustement
        self.btn_zoom_reset.clicked.connect(self.zoom_reset)

    def display_medical_image(self, file_path: str):
        """Enregistre le fichier et force le premier rendu."""
        self.current_file_path = file_path
        self.zoom_factor = 1.0
        self.update_image_render()

    def update_image_render(self):
        """Calcule la taille idéale de l'image en tenant compte du zoom et de la fenêtre."""
        if not self.current_file_path:
            return

        pixmap = QPixmap(self.current_file_path)

        available_width = self.scroll_area.width() - 25
        available_height = self.scroll_area.height() - 25

        # base scale
        scaled_pixmap = pixmap.scaled(
            available_width,
            available_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        # zoom loupe
        if self.zoom_factor != 1.0:
            new_width = int(scaled_pixmap.width() * self.zoom_factor)
            new_height = int(scaled_pixmap.height() * self.zoom_factor)
            scaled_pixmap = scaled_pixmap.scaled(
                new_width,
                new_height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )

        self.image_display.setPixmap(scaled_pixmap)

    def resizeEvent(self, event):
        """Fonction native PyQt déclenchée AUTOMATIQUEMENT au redimensionnement."""
        super().resizeEvent(event)
        if self.current_file_path:
            self.update_image_render()

    def center_on_screen(self):
        """Calcule le centre de l'écran de l'utilisateur et y place la fenêtre."""
        screen = QGuiApplication.primaryScreen()
        if screen:
            screen_geometry = screen.geometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)

    # --- LOUPE ---
    def zoom_reset(self):
        if self.current_file_path:
            self.zoom_factor = 1.0
            self.update_image_render()
