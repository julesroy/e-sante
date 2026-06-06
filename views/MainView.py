from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea, QInputDialog, QSlider
from PyQt6.QtCore import Qt, QPoint, QRect
from PyQt6.QtGui import QPixmap, QGuiApplication, QIcon, QPainter, QCursor, QPen, QColor
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controllers.MainController import MainController
import os
from views.LeftToolBar import LeftToolbar
from views.TopToolbar import TopToolbar
from views.RulerOverlay import RulerOverlay
from views.PatientInfoWidget import PatientInfoWidget
from views.AngleOverlay import AngleOverlay
from views.HeightCompOverlay import HeightCompOverlay


class MedicalImageLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.visualizer = parent
        self.ruler_overlay = RulerOverlay(self)
        self.angle_overlay = AngleOverlay(self)
        self.height_comp_overlay = HeightCompOverlay(self)

    def mousePressEvent(self, event):
        """Intercepte les clics pour positionner les points de mesure si la règle, l'angle ou le comparateur de hauteur est actif."""
        super().mousePressEvent(event)
        if self.visualizer and self.visualizer.main_view:
            if self.visualizer.main_view.ruler_active:
                pixmap_displayed = self.pixmap()
                if pixmap_displayed:
                    margin_x = (self.width() - pixmap_displayed.width()) // 2
                    margin_y = (self.height() - pixmap_displayed.height()) // 2
                    img_rect = QRect(margin_x, margin_y, pixmap_displayed.width(), pixmap_displayed.height())

                    if self.ruler_overlay.handle_mouse_press(event.position().toPoint(), img_rect):
                        self.update()
            elif self.visualizer.main_view.angle_active:
                pixmap_displayed = self.pixmap()
                if pixmap_displayed:
                    margin_x = (self.width() - pixmap_displayed.width()) // 2
                    margin_y = (self.height() - pixmap_displayed.height()) // 2
                    img_rect = QRect(margin_x, margin_y, pixmap_displayed.width(), pixmap_displayed.height())

                    if self.angle_overlay.handle_mouse_press(event.position().toPoint(), img_rect):
                        self.update()
            elif self.visualizer.main_view.height_comp_active:
                pixmap_displayed = self.pixmap()
                if pixmap_displayed:
                    margin_x = (self.width() - pixmap_displayed.width()) // 2
                    margin_y = (self.height() - pixmap_displayed.height()) // 2
                    img_rect = QRect(margin_x, margin_y, pixmap_displayed.width(), pixmap_displayed.height())

                    if self.height_comp_overlay.handle_mouse_press(event.position().toPoint(), img_rect):
                        self.update()

    def paintEvent(self, event):
        """Dessine l'image et force la ligne du slider au premier plan absolu"""
        super().paintEvent(event)

        pixmap_displayed = self.pixmap()
        if not pixmap_displayed:
            return

        painter = QPainter(self)

        # Calcul des marges
        margin_x = (self.width() - pixmap_displayed.width()) // 2
        margin_y = (self.height() - pixmap_displayed.height()) // 2
        img_rect = QRect(margin_x, margin_y, pixmap_displayed.width(), pixmap_displayed.height())

        # --- DESSIN DE LA REGLE DE MESURE AU PREMIER PLAN ---
        if self.visualizer and self.visualizer.main_view and self.visualizer.main_view.ruler_active:
            self.ruler_overlay.draw_measure(painter, img_rect)

        # --- DESSIN DE L'ANGLE DE MESURE AU PREMIER PLAN ---
        if self.visualizer and self.visualizer.main_view and self.visualizer.main_view.angle_active:
            self.angle_overlay.draw_measure(painter, img_rect)

        # --- DESSIN DU COMPARATEUR DE HAUTEUR AU PREMIER PLAN ---
        if self.visualizer and self.visualizer.main_view and self.visualizer.main_view.height_comp_active:
            self.height_comp_overlay.draw_measure(painter, img_rect)

        if not self.visualizer or not self.visualizer.main_view or not self.visualizer.main_view.slider_compare_active or not self.visualizer.main_view.current_pixmap:
            painter.end()
            return

        # Récupération de l'image d'origine
        controller = getattr(self.visualizer.main_view, "controller", None)
        if controller and hasattr(controller, "_original_pixmap") and controller._original_pixmap:
            image_a = controller._original_pixmap.scaled(pixmap_displayed.width(), pixmap_displayed.height(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        else:
            image_a = pixmap_displayed

        image_b = pixmap_displayed

        # Conversion pos slider
        local_slider_x = self.mapFrom(self.visualizer.viewport(), QPoint(self.visualizer.slider_pos_x, 0)).x()
        split_x = local_slider_x - img_rect.left()

        # Dessin image origine
        if split_x > 0:
            rect_left = QRect(img_rect.left(), img_rect.top(), split_x, img_rect.height())
            painter.setClipRect(rect_left)
            painter.drawPixmap(img_rect.left(), img_rect.top(), image_a)

        # Dessin image modifiée
        if split_x < img_rect.width():
            rect_right = QRect(img_rect.left() + split_x, img_rect.top(), img_rect.width() - split_x, img_rect.height())
            painter.setClipRect(rect_right)
            painter.drawPixmap(img_rect.left(), img_rect.top(), image_b)

        # Dessin slider compa
        painter.setClipping(False)
        pen = QPen(QColor("#00a2ed"), 2, Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        painter.drawLine(local_slider_x, img_rect.top(), local_slider_x, img_rect.bottom())
        painter.end()


# === Image et Loupe ===
class MedicalImageVisualizer(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_view = parent

        # Tracking souris
        self.setMouseTracking(True)
        self.magnifier = QLabel(self)
        self.magnifier.setFixedSize(230, 230)
        self.magnifier.setObjectName("MagnifierLens")

        self.magnifier.hide()

        # Var slider compa
        self.slider_pos_x = 300
        self.is_dragging_slider = False

        self.controller = None

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if not self.main_view or not self.main_view.slider_compare_active or self.main_view.current_pixmap is None:
            return

        content_widget = self.widget()
        if not content_widget or not content_widget.pixmap():
            return

        pos_viewport = event.position().toPoint()

        if abs(pos_viewport.x() - self.slider_pos_x) < 10:
            self.is_dragging_slider = True
            self.setCursor(Qt.CursorShape.SplitHCursor)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.is_dragging_slider = False
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def mouseMoveEvent(self, event):
        """Gère la découpe et le déplacement de la bulle loupe avec correction d'offset"""
        super().mouseMoveEvent(event)

        # Logique glissement slider
        if self.main_view and self.main_view.slider_compare_active and self.main_view.current_pixmap is not None:
            pos_viewport = event.position().toPoint()
            content_widget = self.widget()

            if content_widget and content_widget.pixmap():
                pixmap_displayed = content_widget.pixmap()
                margin_x = (content_widget.width() - pixmap_displayed.width()) // 2

                if self.is_dragging_slider:
                    min_x = margin_x
                    max_x = margin_x + pixmap_displayed.width()
                    self.slider_pos_x = max(min_x, min(pos_viewport.x(), max_x))
                    content_widget.update()  # Rafraîchit le label directement
                    return

                if abs(pos_viewport.x() - self.slider_pos_x) < 10:
                    self.setCursor(Qt.CursorShape.SplitHCursor)
                else:
                    self.setCursor(Qt.CursorShape.ArrowCursor)

        if not self.main_view or self.main_view.current_pixmap is None or not self.main_view.magnifier_active:
            self.magnifier.hide()
            return

        content_widget = self.widget()  # Le QLabel affichant la radio
        if not content_widget or not content_widget.pixmap():
            return

        pixmap_displayed = content_widget.pixmap()

        # Position souris repère global
        pos_viewport = event.position().toPoint()
        pos_in_label = content_widget.mapFrom(self.viewport(), pos_viewport)

        # Centrage
        margin_x = (content_widget.width() - pixmap_displayed.width()) // 2
        margin_y = (content_widget.height() - pixmap_displayed.height()) // 2

        # Position souris relative image
        img_x = pos_in_label.x() - margin_x
        img_y = pos_in_label.y() - margin_y

        # Vérifier curseur dans l'image ou pas
        if 0 <= img_x < pixmap_displayed.width() and 0 <= img_y < pixmap_displayed.height():
            self.magnifier.show()

            # Empêcher la loupe de sortir du viewport
            viewport_w = self.viewport().width()
            viewport_h = self.viewport().height()
            mag_w = self.magnifier.width()
            mag_h = self.magnifier.height()

            # Offsets par défaut (en bas à droite du curseur)
            offset_x = 15
            offset_y = 15

            # Si la loupe dépasse à droite, on la place à gauche du curseur
            if pos_viewport.x() + offset_x + mag_w > viewport_w:
                offset_x = -mag_w - 15

            # Si la loupe dépasse en bas, on la place au-dessus du curseur
            if pos_viewport.y() + offset_y + mag_h > viewport_h:
                offset_y = -mag_h - 15

            target_x = pos_viewport.x() + offset_x
            target_y = pos_viewport.y() + offset_y

            # Sécurité : forcer dans les limites du viewport
            target_x = max(0, min(target_x, viewport_w - mag_w))
            target_y = max(0, min(target_y, viewport_h - mag_h))

            # Conversion dans le repère du parent (QScrollArea)
            pos_in_parent = self.viewport().mapTo(self, QPoint(target_x, target_y))

            # loupe suivre curseur
            self.magnifier.move(pos_in_parent)
            self.magnifier.raise_()

            # 4. Projection image origine
            scale_x = self.main_view.current_pixmap.width() / pixmap_displayed.width()
            scale_y = self.main_view.current_pixmap.height() / pixmap_displayed.height()

            orig_x = int(img_x * scale_x)
            orig_y = int(img_y * scale_y)

            # Taille zone source
            size_src = int(230 / self.main_view.magnifier_power)

            rect_src = QRect(orig_x - size_src // 2, orig_y - size_src // 2, size_src, size_src)

            # Découpe / redim le zoom via image affiché
            cropped = self.main_view.current_pixmap.copy(rect_src)
            zoom_pixmap = cropped.scaled(230, 230, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

            self.magnifier.setPixmap(zoom_pixmap)
        else:
            self.magnifier.hide()


# === FENÊTRE PRINCIPALE ===
class MainView(QMainWindow):
    def __init__(self):
        super().__init__()
        # Déclaration des attributs pour Pylance
        self.controller: MainController | None = None
        self.contrast_slider: QSlider | None = None

        self.setWindowTitle("PixelMed")
        self.resize(1024, 680)

        base_dir = os.path.dirname(os.path.dirname(__file__))
        icon_path = os.path.join(base_dir, "assets", "icons", "app_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.current_file_path = None
        self.current_pixmap = None

        # --- ETATS DE LA LOUPE ---
        self.magnifier_active = False
        self.magnifier_power = 2.0
        self.slider_compare_active = False

        # --- ETATS DE LA REGLE ---
        self.ruler_active = False
        self.angle_active = False
        self.height_comp_active = False

        # --- SLIDER DE CONTRASTE ---
        self.contrast_slider_active = False
        self.contrast_slider = None
        self._contrast_slider_connection = None

        self.center_on_screen()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.top_toolbar = TopToolbar(self)
        self.layout.addWidget(self.top_toolbar)

        self.viewer_container = QWidget()
        content_layout = QHBoxLayout(self.viewer_container)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(15)

        self.left_toolbar = LeftToolbar(self)
        content_layout.addWidget(self.left_toolbar)
        self.patient_info_panel = PatientInfoWidget(self)
        content_layout.addWidget(self.patient_info_panel)

        self.scroll_area = MedicalImageVisualizer(self)

        self.image_display = MedicalImageLabel("Aucune radiographie chargée.", self.scroll_area)
        self.image_display.setObjectName("PlaceholderLabel")
        self.image_display.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Activer le suivi souris sur le label d'affichage
        self.image_display.setMouseTracking(True)
        self.scroll_area.setWidget(self.image_display)

        # --- SETUP SLIDER DE CONTRASTE (overlay) ---
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal, self.scroll_area)
        self.contrast_slider.setMinimum(1)
        self.contrast_slider.setMaximum(10)
        self.contrast_slider.setValue(1)
        self.contrast_slider.setFixedWidth(200)
        self.contrast_slider.setFixedHeight(20)
        self.contrast_slider.hide()
        # Positionnement initial (sera mis à jour quand la fenêtre se redimensionne)
        self.contrast_slider.move(15, self.scroll_area.height() - 35)

        content_layout.addWidget(self.scroll_area)

        content_layout.setStretchFactor(self.left_toolbar, 0)
        content_layout.setStretchFactor(self.scroll_area, 1)
        self.layout.addWidget(self.viewer_container)

        # On transforme le bouton d'agrandissement du haut en Interrupteur Loupe
        self.btn_magnifier = self.top_toolbar.btn_loupe
        self.btn_magnifier.setCheckable(True)

        # Déconnexion des anciens signaux pour lier le nouveau mode
        try:
            self.btn_magnifier.clicked.disconnect()
        except:
            pass
        self.btn_magnifier.clicked.connect(self.toggle_magnifier_mode)

        # Btn Slider compa
        self.btn_slider_compare = self.top_toolbar.btn_slider_compare
        self.btn_slider_compare.setCheckable(True)
        self.btn_slider_compare.clicked.connect(self.toggle_slider_mode)

        # Btn Contrast Slider
        self.btn_contrast_slider = self.left_toolbar.btn_contrast_slider
        self.btn_contrast_slider.setCheckable(True)
        self.left_toolbar.contrast_slider_clicked.connect(self.toggle_contrast_slider_mode)

    def display_medical_image(self, file_path: str):
        self.current_file_path = file_path
        self.current_pixmap = QPixmap(file_path)
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
        self.image_display.setPixmap(scaled_pixmap)

    def toggle_magnifier_mode(self, checked):
        """Ouvre la popup de réglage et active l'effet au survol"""
        if self.current_pixmap is None:
            self.btn_magnifier.setChecked(False)
            return

        self.magnifier_active = checked

        if checked:
            # Affichage de la boîte de dialogue (Popup)
            power, ok = QInputDialog.getDouble(self, "Configuration Loupe", "Facteur de zoom de la lentille (x2.0 à x8.0) :", value=3.0, min=2.0, max=8.0, decimals=1)
            if ok:
                self.magnifier_power = power
                self.btn_magnifier.setToolTip(f"Désactiver la loupe (Active: x{power})")
            else:
                self.magnifier_active = False
                self.btn_magnifier.setChecked(False)
        else:
            self.btn_magnifier.setToolTip("Activer la loupe de précision")
            self.scroll_area.magnifier.hide()

    def toggle_slider_mode(self, checked):
        """Active ou désactive l'état du slider de comparaison"""
        if self.current_pixmap is None:
            self.btn_slider_compare.setChecked(False)
            return

        self.slider_compare_active = checked
        print(f"Mode Slider de comparaison {'activé' if checked else 'désactivé'}.")
        if checked:
            print("Mode Slider de comparaison activé.")
            self.scroll_area.slider_pos_x = self.scroll_area.width() // 2
            self.image_display.update()
        else:
            print("Mode Slider de comparaison désactivé.")
            self.image_display.update()

    def toggle_contrast_slider_mode(self, checked):
        """Active ou désactive le mode slider de contraste"""
        if self.current_pixmap is None or self.contrast_slider is None:
            self.left_toolbar.btn_contrast_slider.setChecked(False)
            return

        self.contrast_slider_active = checked
        if checked:
            print("Mode Slider de contraste activé.")
            self.contrast_slider.show()
            self._update_contrast_slider_position()
            if self.controller and self._contrast_slider_connection is None:
                self._contrast_slider_connection = self.contrast_slider.valueChanged.connect(self.controller.apply_contrast_realtime)
        else:
            print("Mode Slider de contraste désactivé.")
            self.contrast_slider.hide()
            if self._contrast_slider_connection is not None:
                try:
                    self.contrast_slider.valueChanged.disconnect(self._contrast_slider_connection)
                except:
                    pass
                self._contrast_slider_connection = None
            self.contrast_slider.setValue(1)

    def toggle_ruler_mode(self, checked):
        """Active ou désactive l'état de la règle de mesure"""
        if self.current_pixmap is None:
            self.left_toolbar.btn_ruler.setChecked(False)
            return

        self.ruler_active = checked
        if checked:
            print("Mode Règle de mesure activé.")
            if hasattr(self.image_display, "ruler_overlay"):
                self.image_display.ruler_overlay.clear()
        else:
            print("Mode Règle de mesure désactivé.")
        self.image_display.update()

    def _update_contrast_slider_position(self):
        """Repositionne le slider de contraste en bas à gauche de la scroll_area"""
        if self.contrast_slider is not None and self.contrast_slider_active:
            x = 15
            y = self.scroll_area.height() - 35
            self.contrast_slider.move(x, y)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.current_pixmap is not None:
            self.update_image_render()
        self._update_contrast_slider_position()

    def center_on_screen(self):
        screen = QGuiApplication.primaryScreen()
        if screen:
            screen_geometry = screen.geometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)