from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea, QInputDialog, QSlider
from PyQt6.QtCore import Qt, QPoint, QRect
from PyQt6.QtGui import QPixmap, QGuiApplication, QIcon, QPainter, QCursor, QPen, QColor, QFont
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
from views.FormsOverlay import FormsOverlay
from views.HistogramWidget import HistogramWidget

# ===== IMPORT HELPER ======
from utils.paths import resource_path

class MedicalImageLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.visualizer = parent
        self.ruler_overlay = RulerOverlay(self)
        self.angle_overlay = AngleOverlay(self)
        self.height_comp_overlay = HeightCompOverlay(self)
        self.forms_overlay = FormsOverlay(self)
        self.pipette_pos = None
        self.pipette_val = None

    def leaveEvent(self, event):
        super().leaveEvent(event)
        if hasattr(self, "pipette_pos"):
            self.pipette_pos = None
            self.pipette_val = None
            self.update()

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
            elif self.visualizer.main_view.circle_roi_active or self.visualizer.main_view.square_roi_active:
                pixmap_displayed = self.pixmap()
                if pixmap_displayed:
                    margin_x = (self.width() - pixmap_displayed.width()) // 2
                    margin_y = (self.height() - pixmap_displayed.height()) // 2
                    img_rect = QRect(margin_x, margin_y, pixmap_displayed.width(), pixmap_displayed.height())

                    shape = "circle" if self.visualizer.main_view.circle_roi_active else "square"
                    self.forms_overlay.shape_type = shape
                    if self.forms_overlay.handle_mouse_press(event.position().toPoint(), img_rect):
                        self.update()
            elif self.visualizer.main_view.pipette_active:
                pixmap_displayed = self.pixmap()
                if pixmap_displayed:
                    margin_x = (self.width() - pixmap_displayed.width()) // 2
                    margin_y = (self.height() - pixmap_displayed.height()) // 2
                    local_pos = event.position().toPoint()
                    img_x = local_pos.x() - margin_x
                    img_y = local_pos.y() - margin_y

                    if 0 <= img_x < pixmap_displayed.width() and 0 <= img_y < pixmap_displayed.height():
                        controller = getattr(self.visualizer.main_view, "controller", None)
                        if controller and controller._current_array is not None:
                            # Lire à partir de l'image de base avant pipette
                            base_array = None
                            if hasattr(controller, "ruler_ctrl"):
                                base_array = getattr(controller.ruler_ctrl, "image_before_pipette", None)
                            if base_array is None:
                                base_array = controller._current_array

                            orig_h, orig_w = base_array.shape
                            orig_x = int(img_x * (orig_w / pixmap_displayed.width()))
                            orig_y = int(img_y * (orig_h / pixmap_displayed.height()))

                            orig_x = max(0, min(orig_x, orig_w - 1))
                            orig_y = max(0, min(orig_y, orig_h - 1))

                            val_float = base_array[orig_y, orig_x]
                            val_255 = int(val_float * 255)

                            if controller:
                                controller.last_pipette_threshold = val_255

                            # Copier dans le presse-papiers
                            from PyQt6.QtGui import QGuiApplication
                            QGuiApplication.clipboard().setText(str(val_255))

                            # Afficher confirmation
                            from PyQt6.QtWidgets import QToolTip
                            QToolTip.showText(event.globalPosition().toPoint(), f"Seuil de gris relevé : {val_255} (copié)", self)
                            print(f"Pipette : seuil de gris sélectionné = {val_255}")

    def mouseMoveEvent(self, event):
        """Met à jour le tracé temporaire pour la règle ou l'angle."""
        super().mouseMoveEvent(event)
        if self.visualizer and self.visualizer.main_view:
            if self.visualizer.main_view.ruler_active:
                pixmap_displayed = self.pixmap()
                if pixmap_displayed:
                    margin_x = (self.width() - pixmap_displayed.width()) // 2
                    margin_y = (self.height() - pixmap_displayed.height()) // 2
                    img_rect = QRect(margin_x, margin_y, pixmap_displayed.width(), pixmap_displayed.height())

                    if self.ruler_overlay.handle_mouse_move(event.position().toPoint(), img_rect):
                        self.update()
            elif self.visualizer.main_view.angle_active:
                pixmap_displayed = self.pixmap()
                if pixmap_displayed:
                    margin_x = (self.width() - pixmap_displayed.width()) // 2
                    margin_y = (self.height() - pixmap_displayed.height()) // 2
                    img_rect = QRect(margin_x, margin_y, pixmap_displayed.width(), pixmap_displayed.height())

                    if self.angle_overlay.handle_mouse_move(event.position().toPoint(), img_rect):
                        self.update()
            elif self.visualizer.main_view.circle_roi_active or self.visualizer.main_view.square_roi_active:
                pixmap_displayed = self.pixmap()
                if pixmap_displayed:
                    margin_x = (self.width() - pixmap_displayed.width()) // 2
                    margin_y = (self.height() - pixmap_displayed.height()) // 2
                    img_rect = QRect(margin_x, margin_y, pixmap_displayed.width(), pixmap_displayed.height())

                    shape = "circle" if self.visualizer.main_view.circle_roi_active else "square"
                    self.forms_overlay.shape_type = shape
                    if self.forms_overlay.handle_mouse_move(event.position().toPoint(), img_rect):
                        self.update()
            elif self.visualizer.main_view.pipette_active:
                pixmap_displayed = self.pixmap()
                if pixmap_displayed:
                    margin_x = (self.width() - pixmap_displayed.width()) // 2
                    margin_y = (self.height() - pixmap_displayed.height()) // 2
                    local_pos = event.position().toPoint()
                    img_x = local_pos.x() - margin_x
                    img_y = local_pos.y() - margin_y

                    if 0 <= img_x < pixmap_displayed.width() and 0 <= img_y < pixmap_displayed.height():
                        controller = getattr(self.visualizer.main_view, "controller", None)
                        if controller and controller._current_array is not None:
                            base_array = None
                            if hasattr(controller, "ruler_ctrl"):
                                base_array = getattr(controller.ruler_ctrl, "image_before_pipette", None)
                            if base_array is None:
                                base_array = controller._current_array

                            orig_h, orig_w = base_array.shape
                            orig_x = int(img_x * (orig_w / pixmap_displayed.width()))
                            orig_y = int(img_y * (orig_h / pixmap_displayed.height()))

                            orig_x = max(0, min(orig_x, orig_w - 1))
                            orig_y = max(0, min(orig_y, orig_h - 1))

                            val_float = base_array[orig_y, orig_x]
                            val_255 = int(val_float * 255)

                            self.pipette_pos = local_pos
                            self.pipette_val = val_255
                            self.update()
                    else:
                        self.pipette_pos = None
                        self.pipette_val = None
                        self.update()
        event.ignore()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if self.visualizer and self.visualizer.main_view:
            if self.visualizer.main_view.circle_roi_active or self.visualizer.main_view.square_roi_active:
                pixmap_displayed = self.pixmap()
                if pixmap_displayed:
                    margin_x = (self.width() - pixmap_displayed.width()) // 2
                    margin_y = (self.height() - pixmap_displayed.height()) // 2
                    img_rect = QRect(margin_x, margin_y, pixmap_displayed.width(), pixmap_displayed.height())
                    if self.forms_overlay.handle_mouse_release(event.position().toPoint(), img_rect):
                        self.update()
        event.ignore()

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

        # --- DESSIN DES FORMES D'ANALYSE (CERCLE / CARRE) AU PREMIER PLAN ---
        if self.visualizer and self.visualizer.main_view and (self.visualizer.main_view.circle_roi_active or self.visualizer.main_view.square_roi_active):
            self.forms_overlay.draw_measure(painter, img_rect)

        # --- DESSIN DU RETICULE ET VALEUR PIPETTE AU PREMIER PLAN ---
        if self.visualizer and self.visualizer.main_view and self.visualizer.main_view.pipette_active and getattr(self, "pipette_pos", None) is not None and getattr(self, "pipette_val", None) is not None:
            painter.setClipping(False)
            x, y = self.pipette_pos.x(), self.pipette_pos.y()
            
            # Reticule de ciblage
            painter.setPen(QPen(QColor(255, 255, 255, 200), 1, Qt.PenStyle.SolidLine))
            painter.drawEllipse(QPoint(x, y), 6, 6)
            painter.drawLine(x - 10, y, x + 10, y)
            painter.drawLine(x, y - 10, x, y + 10)
            
            # Ombre pour lisibilité
            painter.setPen(QPen(QColor(0, 0, 0, 150), 1, Qt.PenStyle.DotLine))
            painter.drawEllipse(QPoint(x, y), 7, 7)
            
            # Cartouche d'affichage textuel
            text = f"Seuil (gris) : {self.pipette_val}"
            font = QFont("Segoe UI", 10, QFont.Weight.Bold)
            painter.setFont(font)
            fm = painter.fontMetrics()
            text_width = fm.horizontalAdvance(text)
            text_height = fm.height()
            
            padding_x = 8
            padding_y = 4
            rect_width = text_width + 2 * padding_x
            rect_height = text_height + 2 * padding_y
            
            offset_x = 12
            offset_y = 12
            rect_x = x + offset_x
            rect_y = y + offset_y
            
            if rect_x + rect_width > self.width():
                rect_x = x - rect_width - offset_x
            if rect_y + rect_height > self.height():
                rect_y = y - rect_height - offset_y
                
            rect = QRect(rect_x, rect_y, rect_width, rect_height)
            painter.setBrush(QColor(20, 20, 20, 220))
            painter.setPen(QPen(QColor(80, 80, 80, 200), 1))
            painter.drawRoundedRect(rect, 4.0, 4.0)
            
            painter.setPen(QColor(240, 240, 240))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)

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

        icon_path = resource_path(os.path.join("assets", "icons", "app_icon.png"))
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
        self.circle_roi_active = False
        self.square_roi_active = False
        self.pipette_active = False

        # --- SLIDER DE CONTRASTE ---
        self.contrast_slider_active = False
        self.contrast_slider = None
        self._contrast_slider_connection = None

        self.center_on_screen()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(15)

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

        # --- INFO DE L'IMAGE (overlay en bas à droite) ---
        self.image_info_label = QLabel(self.scroll_area)
        self.image_info_label.setObjectName("ImageInfoLabel")
        self.image_info_label.setStyleSheet("""
            #ImageInfoLabel {
                color: #e0e0e0;
                background-color: rgba(32, 32, 32, 200);
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 11px;
                font-family: "Segoe UI", Arial, sans-serif;
            }
        """)
        self.image_info_label.hide()

        # --- AIRES WATERSHED (overlay en bas à droite, au-dessus de image_info_label) ---
        self.watershed_area_label = QLabel(self.scroll_area)
        self.watershed_area_label.setObjectName("WatershedAreaLabel")
        self.watershed_area_label.setStyleSheet("""
            #WatershedAreaLabel {
                color: #e0e0e0;
                background-color: rgba(32, 32, 32, 200);
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 11px;
                font-family: "Segoe UI", Arial, sans-serif;
            }
        """)
        self.watershed_area_label.hide()

        # --- SPECTRE FFT (overlay en bas à droite, au-dessus de watershed_area_label / image_info_label) ---
        self.fft_label = QLabel(self.scroll_area)
        self.fft_label.setObjectName("FftLabel")
        self.fft_label.setStyleSheet("""
            #FftLabel {
                background-color: rgba(32, 32, 32, 200);
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 6px;
            }
        """)
        self.fft_label.hide()

        # --- HISTOGRAMME (overlay en bas à droite, au-dessus de watershed_area_label / image_info_label) ---
        self.histo_widget = HistogramWidget(self.scroll_area)
        self.histo_widget.hide()

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

        # Mettre à jour les infos de l'image
        path = self.current_file_path
        if (path == "from_controller" or not path) and self.controller:
            path = self.controller._last_file_path
        self.update_image_info(path, self.current_pixmap)

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

    def toggle_pipette_mode(self, checked):
        """Active ou désactive le mode pipette pour relever le niveau de gris"""
        if self.current_pixmap is None:
            self.left_toolbar.btn_pipette.setChecked(False)
            return

        self.pipette_active = checked
        if checked:
            print("Mode Pipette de niveau de gris activé.")
            self.image_display.setCursor(Qt.CursorShape.CrossCursor)
        else:
            print("Mode Pipette de niveau de gris désactivé.")
            self.image_display.setCursor(Qt.CursorShape.ArrowCursor)

    def _update_contrast_slider_position(self):
        """Repositionne le slider de contraste en bas à gauche de la scroll_area"""
        if self.contrast_slider is not None and self.contrast_slider_active:
            x = 15
            y = self.scroll_area.height() - 35
            self.contrast_slider.move(x, y)

    def _update_image_info_position(self):
        """Repositionne les infos de l'image en bas à droite de la scroll_area"""
        if hasattr(self, "image_info_label") and self.image_info_label.isVisible():
            self.image_info_label.adjustSize()
            x = self.scroll_area.width() - self.image_info_label.width() - 15
            y = self.scroll_area.height() - self.image_info_label.height() - 15
            self.image_info_label.move(max(0, x), max(0, y))

            y_current = y

            # Positionner aussi self.watershed_area_label juste au-dessus
            if hasattr(self, "watershed_area_label") and self.watershed_area_label.isVisible():
                self.watershed_area_label.setFixedWidth(self.image_info_label.width())
                self.watershed_area_label.adjustSize()
                y_current = y_current - self.watershed_area_label.height() - 10
                   # Positionner aussi self.fft_label encore au-dessus
            if hasattr(self, "fft_label") and self.fft_label.isVisible():
                if self.fft_label.pixmap():
                    # Forcer la largeur du pixmap à correspondre à la largeur de image_info_label
                    scaled = self.fft_label.pixmap().scaledToWidth(self.image_info_label.width(), Qt.TransformationMode.SmoothTransformation)
                    self.fft_label.setPixmap(scaled)
                self.fft_label.adjustSize()
                x_fft = self.scroll_area.width() - self.fft_label.width() - 15
                y_fft = y_current - self.fft_label.height() - 10
                self.fft_label.move(max(0, x_fft), max(0, y_fft))
                y_current = y_fft

            # Positionner aussi self.histo_widget encore au-dessus
            if hasattr(self, "histo_widget") and self.histo_widget.isVisible():
                self.histo_widget.adjustSize()
                x_histo = self.scroll_area.width() - self.histo_widget.width() - 15
                y_histo = y_current - self.histo_widget.height() - 10
                self.histo_widget.move(max(0, x_histo), max(0, y_histo))
                y_current = y_histo
        else:
            y_current = self.scroll_area.height() - 15
            if hasattr(self, "fft_label") and self.fft_label.isVisible():
                self.fft_label.adjustSize()
                x = self.scroll_area.width() - self.fft_label.width() - 15
                y = y_current - self.fft_label.height()
                self.fft_label.move(max(0, x), max(0, y))
                y_current = y - 10
            if hasattr(self, "histo_widget") and self.histo_widget.isVisible():
                self.histo_widget.adjustSize()
                x = self.scroll_area.width() - self.histo_widget.width() - 15
                y = y_current - self.histo_widget.height()
                self.histo_widget.move(max(0, x), max(0, y))

    def update_image_info(self, file_path: str | None, pixmap: QPixmap | None):
        """Met à jour et affiche le panneau d'information de l'image"""
        if pixmap is None or pixmap.isNull():
            if hasattr(self, "image_info_label"):
                self.image_info_label.hide()
            if hasattr(self, "watershed_area_label"):
                self.watershed_area_label.hide()
            if hasattr(self, "fft_label"):
                self.fft_label.hide()
            if hasattr(self, "histo_widget"):
                self.histo_widget.hide()
            return

        dims = f"{pixmap.width()} x {pixmap.height()} px"

        # Par défaut, on conserve les anciennes valeurs si le chemin est None / from_controller
        if file_path and file_path != "from_controller" and os.path.exists(file_path):
            try:
                size_bytes = os.path.getsize(file_path)
                size_mb = size_bytes / (1024 * 1024)
                self.original_image_size_str = f"{size_mb:.2f} Mo"
                
                _, ext = os.path.splitext(file_path)
                fmt_str = ext.lstrip('.').upper()
                if fmt_str == "DCM":
                    self.original_image_format = "DICOM (dcm)"
                else:
                    self.original_image_format = fmt_str if fmt_str else "INCONNU"
            except Exception as e:
                print(f"Erreur lors de la lecture des infos fichier : {e}")
                self.original_image_size_str = "-- Mo"
                self.original_image_format = "N/A"
        elif not hasattr(self, "original_image_size_str"):
            self.original_image_size_str = "-- Mo"
            self.original_image_format = "N/A"

        text = f"Dimensions : {dims}\nTaille : {self.original_image_size_str}\nFormat : {self.original_image_format}"
        self.image_info_label.setText(text)
        self.image_info_label.show()
        self._update_image_info_position()

    def display_watershed_areas(self, text: str):
        """Met à jour et affiche le panneau d'aires du Watershed"""
        if hasattr(self, "watershed_area_label"):
            self.watershed_area_label.setText(text)
            self.watershed_area_label.show()
            self._update_image_info_position()

    def display_fft_spectrum(self, pixmap: QPixmap):
        """Affiche le spectre FFT dans l'overlay avec la même largeur que les infos de l'image"""
        if hasattr(self, "fft_label"):
            target_width = self.image_info_label.width() if self.image_info_label.isVisible() else 200
            scaled_pixmap = pixmap.scaledToWidth(target_width, Qt.TransformationMode.SmoothTransformation)
            self.fft_label.setPixmap(scaled_pixmap)
            self.fft_label.show()
            self._update_image_info_position()

    def hide_fft_spectrum(self):
        """Masque l'overlay du spectre FFT"""
        if hasattr(self, "fft_label"):
            self.fft_label.hide()
            self._update_image_info_position()

    def display_histogram(self, image_array, file_path):
        """Met à jour et affiche l'histogramme dans son widget d'overlay"""
        if hasattr(self, "histo_widget"):
            self.histo_widget.set_image_data(image_array, file_path)
            self.histo_widget.show()
            self._update_image_info_position()

    def hide_histogram(self):
        """Masque l'overlay de l'histogramme"""
        if hasattr(self, "histo_widget"):
            self.histo_widget.hide()
            self._update_image_info_position()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.current_pixmap is not None:
            self.update_image_render()
        self._update_contrast_slider_position()
        self._update_image_info_position()

    def center_on_screen(self):
        screen = QGuiApplication.primaryScreen()
        if screen:
            screen_geometry = screen.geometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if self.image_display and hasattr(self.image_display, "forms_overlay"):
            if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
                if self.image_display.forms_overlay.delete_selected():
                    self.image_display.update()