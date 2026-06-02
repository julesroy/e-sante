from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QPixmap, QGuiApplication, QIcon
import os

from views.LeftToolBar import LeftToolbar
from views.TopToolbar import TopToolbar

# === Zoom et déplacement ===
class MedicalImageVisualizer(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_view = parent

    def wheelEvent(self, event):
        if not self.main_view or self.main_view.current_pixmap is None:
            event.ignore()
            return

        modifiers = event.modifiers()
        delta_y = event.angleDelta().y()
        delta_x = event.angleDelta().x()
        delta = delta_y if delta_y != 0 else delta_x
        pas_deplacement = 15

        if modifiers == Qt.KeyboardModifier.ShiftModifier:
            v_bar = self.verticalScrollBar()
            v_bar.setValue(v_bar.value() - pas_deplacement if delta > 0 else v_bar.value() + pas_deplacement)
            event.accept()
            return
        elif modifiers == Qt.KeyboardModifier.AltModifier:
            h_bar = self.horizontalScrollBar()
            h_bar.setValue(h_bar.value() - pas_deplacement if delta > 0 else h_bar.value() + pas_deplacement)
            event.accept()
            return
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
                self.main_view.zoom_factor *= 1.06
            else:
                self.main_view.zoom_factor /= 1.06
            self.main_view.zoom_factor = max(0.5, min(self.main_view.zoom_factor, 8.0))
            if old_zoom != self.main_view.zoom_factor:
                h_bar.blockSignals(True)
                v_bar.blockSignals(True)
                self.main_view.update_image_render()
                zoom_ratio = self.main_view.zoom_factor / old_zoom
                new_x_in_label = mouse_pos_in_label.x() * zoom_ratio
                new_y_in_label = mouse_pos_in_label.y() * zoom_ratio
                h_bar.setValue(int(new_x_in_label - mouse_pos_viewport.x()))
                v_bar.setValue(int(new_y_in_label - mouse_pos_viewport.y()))
                h_bar.blockSignals(False)
                v_bar.blockSignals(False)
            event.accept()
        else:
            event.ignore()

# === FENÊTRE PRINCIPALE ===
class MainView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PixelMed")
        self.resize(1024, 680) # Légèrement agrandi pour correspondre aux proportions de votre maquette

        base_dir = os.path.dirname(os.path.dirname(__file__))
        icon_path = os.path.join(base_dir, "assets", "icons", "app_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.current_file_path = None
        self.current_pixmap = None  
        self.zoom_factor = 1.0
        self.center_on_screen()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # TopToolbar
        self.top_toolbar = TopToolbar(self)
        self.layout.addWidget(self.top_toolbar)

        # === Colonnes ===
        self.viewer_container = QWidget()
        content_layout = QHBoxLayout(self.viewer_container)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(15)

        # === Colonne de gauche : La barre d'outils latérale ===
        self.left_toolbar = LeftToolbar(self)
        content_layout.addWidget(self.left_toolbar)

        # === Colonne de droite IMAGE ===
        self.scroll_area = MedicalImageVisualizer(self)
        self.image_display = QLabel("Aucune radiographie chargée.")
        self.image_display.setObjectName("PlaceholderLabel")
        self.image_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setWidget(self.image_display)
        content_layout.addWidget(self.scroll_area)

        content_layout.setStretchFactor(self.left_toolbar, 0)
        content_layout.setStretchFactor(self.scroll_area, 1)
        self.layout.addWidget(self.viewer_container)
        self.btn_zoom_reset = self.top_toolbar.btn_zoom_reset
        self.btn_zoom_reset.clicked.connect(self.zoom_reset)

    def display_medical_image(self, file_path: str):
        self.current_file_path = file_path
        self.current_pixmap = QPixmap(file_path)
        self.zoom_factor = 1.0
        self.update_image_render()

    def update_image_render(self):
        if self.current_pixmap is None:
            return
        available_width = self.scroll_area.width() - 15
        available_height = self.scroll_area.height() - 15

        scaled_pixmap = self.current_pixmap.scaled(
            available_width,
            available_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

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
        super().resizeEvent(event)
        if self.current_pixmap is not None:
            self.update_image_render()

    def center_on_screen(self):
        screen = QGuiApplication.primaryScreen()
        if screen:
            screen_geometry = screen.geometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)

    def zoom_reset(self):
        if self.current_pixmap is not None:
            self.zoom_factor = 1.0
            self.update_image_render()