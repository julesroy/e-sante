import math
import os
import numpy as np
from PyQt6.QtCore import Qt, QPoint, QRect
from PyQt6.QtGui import QPainter, QPen, QColor, QFont


class FormsOverlay:
    def __init__(self, label_view):
        self.label_view = label_view
        self.shape_type = None  # "circle" ou "square"
        self.rel_a = None
        self.rel_b = None
        self.rel_temp = None  # Point temporaire pour le tracé en direct

        # Cache pour éviter de recharger l'image brute à chaque déplacement de souris
        self.cached_file_path = None
        self.cached_raw_pixels = None
        self.cached_unit = None

    def clear(self):
        """Réinitialise l'état de la mesure."""
        self.rel_a = None
        self.rel_b = None
        self.rel_temp = None

    def handle_mouse_press(self, local_pos: QPoint, img_rect: QRect) -> bool:
        """Calcule et stocke les points de clic sous forme relative (0.0 à 1.0)."""
        if not img_rect.contains(local_pos):
            return False

        # Conversion en coordonnées relatives
        img_x = local_pos.x() - img_rect.left()
        img_y = local_pos.y() - img_rect.top()
        pos_relative = (img_x / img_rect.width(), img_y / img_rect.height())

        # Logique d'alternance A et B
        if self.rel_a is None or (self.rel_a is not None and self.rel_b is not None):
            self.rel_a = pos_relative
            self.rel_b = None
            self.rel_temp = None
        elif self.rel_b is None:
            self.rel_b = pos_relative
            self.rel_temp = None

        return True

    def handle_mouse_move(self, local_pos: QPoint, img_rect: QRect) -> bool:
        """Met à jour le tracé en direct."""
        if self.rel_a is None or self.rel_b is not None:
            if self.rel_temp is not None:
                self.rel_temp = None
                return True
            return False

        # Clamping
        img_x = max(0, min(local_pos.x() - img_rect.left(), img_rect.width()))
        img_y = max(0, min(local_pos.y() - img_rect.top(), img_rect.height()))
        new_temp = (img_x / img_rect.width(), img_y / img_rect.height())

        if self.rel_temp != new_temp:
            self.rel_temp = new_temp
            return True

        return False

    def get_raw_pixels(self):
        """Récupère l'image d'origine sous forme de tableau NumPy non normalisé avec métadonnées."""
        main_view = self.label_view.visualizer.main_view
        if not main_view:
            return None, ""

        file_path = main_view.current_file_path
        if (not file_path or file_path == "from_controller") and main_view.controller:
            file_path = getattr(main_view.controller, "_last_file_path", None)

        if not file_path or not os.path.exists(file_path):
            return None, ""

        if self.cached_file_path != file_path:
            try:
                if file_path.lower().endswith(".dcm"):
                    import pydicom
                    dicom_image = pydicom.dcmread(file_path)
                    pixel_array = dicom_image.pixel_array.astype(np.float32)
                    slope = getattr(dicom_image, "RescaleSlope", 1.0)
                    intercept = getattr(dicom_image, "RescaleIntercept", 0.0)
                    self.cached_raw_pixels = pixel_array * slope + intercept
                    self.cached_unit = "HU"
                else:
                    from PIL import Image
                    img = Image.open(file_path).convert("L")
                    self.cached_raw_pixels = np.array(img).astype(np.float32)
                    self.cached_unit = ""
                self.cached_file_path = file_path
            except Exception as e:
                print(f"Error loading raw pixels: {e}")
                return None, ""

        return self.cached_raw_pixels, self.cached_unit

    def draw_measure(self, painter: QPainter, img_rect: QRect):
        if self.rel_a is None:
            return

        # Déterminer le point cible (B finalisé ou temporel de preview)
        target = None
        is_preview = False

        if self.rel_b is not None:
            target = self.rel_b
            is_preview = False
        elif self.rel_temp is not None:
            target = self.rel_temp
            is_preview = True

        if target is None:
            # Si seul le point A est posé, on le dessine simplement
            screen_ax = int(img_rect.left() + (self.rel_a[0] * img_rect.width()))
            screen_ay = int(img_rect.top() + (self.rel_a[1] * img_rect.height()))
            painter.setPen(QPen(QColor("#ffaa00"), 6, Qt.PenStyle.SolidLine))
            painter.drawPoint(QPoint(screen_ax, screen_ay))
            return

        # Stylos de dessin
        pen_final = QPen(QColor("#ffaa00"), 2, Qt.PenStyle.SolidLine)
        pen_preview = QPen(QColor("#ffaa00"), 2, Qt.PenStyle.DashLine)
        pen_dots = QPen(QColor("#ffaa00"), 6, Qt.PenStyle.SolidLine)

        # Calculer les coordonnées réelles écran
        screen_ax = int(img_rect.left() + (self.rel_a[0] * img_rect.width()))
        screen_ay = int(img_rect.top() + (self.rel_a[1] * img_rect.height()))
        screen_tx = int(img_rect.left() + (target[0] * img_rect.width()))
        screen_ty = int(img_rect.top() + (target[1] * img_rect.height()))

        # Récupération des pixels bruts pour calculs statistiques
        raw_pixels, unit = self.get_raw_pixels()
        if raw_pixels is None:
            return

        orig_h, orig_w = raw_pixels.shape
        ax = self.rel_a[0] * orig_w
        ay = self.rel_a[1] * orig_h
        tx = target[0] * orig_w
        ty = target[1] * orig_h

        # Variables de positionnement de la boîte d'infos
        text_x = 0
        text_y = 0

        # Calculs et dessins spécifiques selon la forme
        if self.shape_type == "circle":
            cx, cy = ax, ay
            r = math.sqrt((tx - ax)**2 + (ty - ay)**2)

            # 1. Dessin de la forme écran
            screen_cx, screen_cy = screen_ax, screen_ay
            screen_r = int(math.sqrt((screen_tx - screen_ax)**2 + (screen_ty - screen_ay)**2))

            if is_preview:
                painter.setPen(pen_preview)
            else:
                painter.setPen(pen_final)
            painter.drawEllipse(QPoint(screen_cx, screen_cy), screen_r, screen_r)

            # Points d'ancrage
            painter.setPen(pen_dots)
            painter.drawPoint(QPoint(screen_cx, screen_cy))
            if is_preview:
                painter.drawPoint(QPoint(screen_tx, screen_ty))

            # 2. Extraction des pixels d'origine
            xmin = max(0, int(math.floor(cx - r)))
            xmax = min(orig_w - 1, int(math.ceil(cx + r)))
            ymin = max(0, int(math.floor(cy - r)))
            ymax = min(orig_h - 1, int(math.ceil(cy + r)))

            if xmax >= xmin and ymax >= ymin:
                Y, X = np.ogrid[ymin:ymax+1, xmin:xmax+1]
                dist_from_center = (X - cx)**2 + (Y - cy)**2
                mask = dist_from_center <= r**2
                sub_pixels = raw_pixels[ymin:ymax+1, xmin:xmax+1]
                values = sub_pixels[mask]
            else:
                values = np.array([])

            # Position texte
            text_x = screen_cx + screen_r + 15
            text_y = screen_cy - 40

        elif self.shape_type == "square":
            # 1. Dessin de la forme écran
            s_xmin = min(screen_ax, screen_tx)
            s_xmax = max(screen_ax, screen_tx)
            s_ymin = min(screen_ay, screen_ty)
            s_ymax = max(screen_ay, screen_ty)

            if is_preview:
                painter.setPen(pen_preview)
            else:
                painter.setPen(pen_final)
            painter.drawRect(QRect(QPoint(s_xmin, s_ymin), QPoint(s_xmax, s_ymax)))

            # Points d'ancrage
            painter.setPen(pen_dots)
            painter.drawPoint(QPoint(screen_ax, screen_ay))
            if is_preview:
                painter.drawPoint(QPoint(screen_tx, screen_ty))

            # 2. Extraction des pixels d'origine
            xmin = max(0, int(math.floor(min(ax, tx))))
            xmax = min(orig_w - 1, int(math.ceil(max(ax, tx))))
            ymin = max(0, int(math.floor(min(ay, ty))))
            ymax = min(orig_h - 1, int(math.ceil(max(ay, ty))))

            if xmax >= xmin and ymax >= ymin:
                values = raw_pixels[ymin:ymax+1, xmin:xmax+1].flatten()
            else:
                values = np.array([])

            # Position texte
            text_x = s_xmax + 15
            text_y = (s_ymin + s_ymax) // 2 - 40

        # Calculer les statistiques
        if values.size > 0:
            mean_val = np.mean(values)
            max_val = np.max(values)
            min_val = np.min(values)
            sd_val = np.std(values)
            num_pixels = values.size
        else:
            mean_val = max_val = min_val = sd_val = num_pixels = 0

        # Calcul de l'aire physique en cm²
        largeur_physique_totale_cm = 45.0
        dynamic_pixel_to_cm = largeur_physique_totale_cm / orig_w
        pixel_area_cm2 = dynamic_pixel_to_cm ** 2
        area_cm2 = num_pixels * pixel_area_cm2

        # Création des lignes de texte
        unit_str = f" {unit}" if unit else ""
        text_lines = [
            f"Moy: {mean_val:.2f}{unit_str}",
            f"Max: {max_val:.2f} / Min: {min_val:.2f}",
            f"SD: {sd_val:.2f}",
            f"Aire: {num_pixels} px² (~ {area_cm2:.2f} cm²)"
        ]

        # Calculer la taille de la boîte
        font = QFont("Arial", 10, QFont.Weight.Bold)
        painter.setFont(font)
        metrics = painter.fontMetrics()

        max_w = 0
        for line in text_lines:
            w = metrics.horizontalAdvance(line)
            if w > max_w:
                max_w = w

        line_height = metrics.height()
        box_h = line_height * len(text_lines) + 12
        box_w = max_w + 16

        # Ajuster le positionnement horizontal si hors limites
        if text_x + box_w > img_rect.right():
            if self.shape_type == "circle":
                text_x = screen_cx - screen_r - box_w - 15
            elif self.shape_type == "square":
                text_x = s_xmin - box_w - 15

        # Clamping vertical et horizontal absolu
        text_x = max(img_rect.left() + 5, min(text_x, img_rect.right() - box_w - 5))
        text_y = max(img_rect.top() + 5, min(text_y, img_rect.bottom() - box_h - 5))

        # Dessiner la boîte d'infos
        text_rect = QRect(text_x, text_y, box_w, box_h)
        painter.fillRect(text_rect, QColor(0, 0, 0, 180))
        painter.setPen(QPen(QColor("#ffaa00"), 1))
        painter.drawRect(text_rect)

        # Dessiner le texte en jaune
        painter.setPen(QColor("#ffaa00"))
        for i, line in enumerate(text_lines):
            line_y = text_y + 6 + i * line_height + metrics.ascent()
            painter.drawText(text_x + 8, line_y, line)
