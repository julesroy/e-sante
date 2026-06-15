import math
import os
import numpy as np
from PyQt6.QtCore import Qt, QPoint, QRect, QRectF, QPointF
from PyQt6.QtGui import QPainter, QPen, QColor, QFont

class Shape:
    def __init__(self, shape_type, cx, cy, w, h, rotation=0.0):
        self.shape_type = shape_type  # "circle" ou "square"
        self.cx = cx                  # centre relatif x (0.0 à 1.0)
        self.cy = cy                  # centre relatif y (0.0 à 1.0)
        self.w = w                    # largeur relative (0.0 à 1.0)
        self.h = h                    # hauteur relative (0.0 à 1.0)
        self.rotation = rotation      # angle en degrés
        self.selected = False


class FormsOverlay:
    def __init__(self, label_view):
        self.label_view = label_view
        self.shape_type = None  # "circle" ou "square"
        self.rel_a = None
        self.rel_b = None
        self.rel_temp = None  # Point temporaire pour le tracé en direct

        # Liste des formes persistantes
        self.shapes = []

        # État d'interaction
        self.selected_shape = None
        self.interaction_mode = None  # None, "creating", "moving", "resizing", "rotating"
        self.active_handle = None     # "tl", "tr", "bl", "br"
        self.drag_offset_x = 0.0
        self.drag_offset_y = 0.0
        self.initial_rotation = 0.0
        self.initial_mouse_angle = 0.0

        # Cache pour éviter de recharger l'image brute à chaque déplacement de souris
        self.cached_file_path = None
        self.cached_raw_pixels = None
        self.cached_unit = None

    def to_screen(self, rx, ry, img_rect: QRect):
        sx = img_rect.left() + rx * img_rect.width()
        sy = img_rect.top() + ry * img_rect.height()
        return sx, sy

    def to_relative(self, sx, sy, img_rect: QRect):
        rx = (sx - img_rect.left()) / img_rect.width()
        ry = (sy - img_rect.top()) / img_rect.height()
        return rx, ry

    def rotate_point(self, x, y, angle_rad):
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        rx = x * cos_a - y * sin_a
        ry = x * sin_a + y * cos_a
        return rx, ry

    def dist(self, p1, p2):
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    def clear(self):
        """Réinitialise l'état du tracé temporaire en cours."""
        self.rel_a = None
        self.rel_b = None
        self.rel_temp = None
        self.interaction_mode = None

    def clear_all(self):
        """Supprime toutes les formes et réinitialise l'état."""
        self.clear()
        self.shapes = []
        self.selected_shape = None

    def handle_mouse_press(self, local_pos: QPoint, img_rect: QRect) -> bool:
        """Gère le clic de la souris."""
        if not img_rect.contains(local_pos):
            return False

        sx = local_pos.x()
        sy = local_pos.y()
        rx, ry = self.to_relative(sx, sy, img_rect)

        # 1. Si une forme est déjà sélectionnée, vérifier si on clique sur l'une de ses poignées
        if self.selected_shape is not None:
            shape = self.selected_shape
            scx, scy = self.to_screen(shape.cx, shape.cy, img_rect)
            sw = shape.w * img_rect.width()
            sh = shape.h * img_rect.height()
            rad = math.radians(shape.rotation)

            # Poignée de rotation (0, -sh/2 - 25)
            rx_rot, ry_rot = self.rotate_point(0, -sh/2 - 25, rad)
            rot_handle_pos = (scx + rx_rot, scy + ry_rot)
            if self.dist((sx, sy), rot_handle_pos) < 10:
                self.interaction_mode = "rotating"
                self.initial_rotation = shape.rotation
                self.initial_mouse_angle = math.degrees(math.atan2(sy - scy, sx - scx))
                return True

            # Poignées de redimensionnement aux coins
            corners = [
                ("tl", (-sw/2, -sh/2)),
                ("tr", (sw/2, -sh/2)),
                ("bl", (-sw/2, sh/2)),
                ("br", (sw/2, sh/2))
            ]
            for name, (lx, ly) in corners:
                rx_c, ry_c = self.rotate_point(lx, ly, rad)
                corner_pos = (scx + rx_c, scy + ry_c)
                if self.dist((sx, sy), corner_pos) < 10:
                    self.interaction_mode = "resizing"
                    self.active_handle = name
                    return True

        # 2. Vérifier si on clique à l'intérieur d'une forme existante pour la sélectionner/déplacer
        for shape in reversed(self.shapes):
            scx, scy = self.to_screen(shape.cx, shape.cy, img_rect)
            sw = shape.w * img_rect.width()
            sh = shape.h * img_rect.height()
            rad = math.radians(shape.rotation)

            dx = sx - scx
            dy = sy - scy
            lx, ly = self.rotate_point(dx, dy, -rad)

            inside = False
            if shape.shape_type == "circle":
                inside = (lx / (sw/2))**2 + (ly / (sh/2))**2 <= 1.0
            else:
                inside = abs(lx) <= sw/2 and abs(ly) <= sh/2

            if inside:
                if self.selected_shape:
                    self.selected_shape.selected = False
                self.selected_shape = shape
                shape.selected = True
                self.interaction_mode = "moving"
                self.drag_offset_x = rx - shape.cx
                self.drag_offset_y = ry - shape.cy
                return True

        # 3. Finaliser le tracé en cours s'il s'agit du deuxième clic de création
        if self.interaction_mode == "creating":
            self.rel_b = (rx, ry)
            dx = abs(self.rel_b[0] - self.rel_a[0])
            dy = abs(self.rel_b[1] - self.rel_a[1])
            if dx > 0.005 or dy > 0.005:
                if self.shape_type == "circle":
                    cx = self.rel_a[0]
                    cy = self.rel_a[1]
                    r = math.sqrt((self.rel_b[0] - self.rel_a[0])**2 + (self.rel_b[1] - self.rel_a[1])**2)
                    w = h = 2.0 * r
                else:
                    cx = (self.rel_a[0] + self.rel_b[0]) / 2.0
                    cy = (self.rel_a[1] + self.rel_b[1]) / 2.0
                    w = dx
                    h = dy

                new_shape = Shape(self.shape_type, cx, cy, w, h, 0.0)
                new_shape.selected = True
                if self.selected_shape:
                    self.selected_shape.selected = False
                self.selected_shape = new_shape
                self.shapes.append(new_shape)

            self.rel_a = None
            self.rel_b = None
            self.rel_temp = None
            self.interaction_mode = None
            return True

        # 4. Clic dans le vide : désélectionner et initier le tracé d'une nouvelle forme
        if self.selected_shape:
            self.selected_shape.selected = False
            self.selected_shape = None

        self.interaction_mode = "creating"
        self.rel_a = (rx, ry)
        self.rel_b = None
        self.rel_temp = None
        return True

    def handle_mouse_move(self, local_pos: QPoint, img_rect: QRect) -> bool:
        """Gère le déplacement de la souris."""
        sx = local_pos.x()
        sy = local_pos.y()

        img_x = max(img_rect.left(), min(sx, img_rect.right()))
        img_y = max(img_rect.top(), min(sy, img_rect.bottom()))
        rx, ry = self.to_relative(img_x, img_y, img_rect)

        if self.interaction_mode == "creating":
            self.rel_temp = (rx, ry)
            return True

        elif self.interaction_mode == "moving" and self.selected_shape:
            shape = self.selected_shape
            shape.cx = rx - self.drag_offset_x
            shape.cy = ry - self.drag_offset_y
            shape.cx = max(0.0, min(shape.cx, 1.0))
            shape.cy = max(0.0, min(shape.cy, 1.0))
            return True

        elif self.interaction_mode == "rotating" and self.selected_shape:
            shape = self.selected_shape
            scx, scy = self.to_screen(shape.cx, shape.cy, img_rect)
            current_angle = math.degrees(math.atan2(sy - scy, sx - scx))
            delta_angle = current_angle - self.initial_mouse_angle
            shape.rotation = (self.initial_rotation + delta_angle) % 360.0
            return True

        elif self.interaction_mode == "resizing" and self.selected_shape:
            shape = self.selected_shape
            scx, scy = self.to_screen(shape.cx, shape.cy, img_rect)
            rad = math.radians(shape.rotation)

            dx = sx - scx
            dy = sy - scy
            lx, ly = self.rotate_point(dx, dy, -rad)

            new_w = 2.0 * abs(lx) / img_rect.width()
            new_h = 2.0 * abs(ly) / img_rect.height()

            min_size = 0.005
            new_w = max(min_size, new_w)
            new_h = max(min_size, new_h)

            if shape.shape_type == "circle":
                dist_local = math.sqrt(lx**2 + ly**2)
                new_w = 2.0 * dist_local / img_rect.width()
                shape.w = max(min_size, new_w)
                shape.h = shape.w * (img_rect.width() / img_rect.height())
            else:
                shape.w = new_w
                shape.h = new_h

            return True

        else:
            self.update_hover_cursor(sx, sy, img_rect)

        return False

    def handle_mouse_release(self, local_pos: QPoint, img_rect: QRect) -> bool:
        """Gère le relâchement du bouton de la souris."""
        if self.interaction_mode in ("moving", "resizing", "rotating"):
            self.interaction_mode = None
            self.active_handle = None
            return True
        return False

    def update_hover_cursor(self, sx, sy, img_rect: QRect):
        """Met à jour l'apparence du curseur selon ce qui est survolé."""
        if self.selected_shape is None:
            self.label_view.setCursor(Qt.CursorShape.CrossCursor)
            return

        shape = self.selected_shape
        scx, scy = self.to_screen(shape.cx, shape.cy, img_rect)
        sw = shape.w * img_rect.width()
        sh = shape.h * img_rect.height()
        rad = math.radians(shape.rotation)

        # 1. Survol de la poignée de rotation
        rx_rot, ry_rot = self.rotate_point(0, -sh/2 - 25, rad)
        rot_handle_pos = (scx + rx_rot, scy + ry_rot)
        if self.dist((sx, sy), rot_handle_pos) < 10:
            self.label_view.setCursor(Qt.CursorShape.PointingHandCursor)
            return

        # 2. Survol des poignées de redimensionnement
        corners = [
            ("tl", (-sw/2, -sh/2)),
            ("tr", (sw/2, -sh/2)),
            ("bl", (-sw/2, sh/2)),
            ("br", (sw/2, sh/2))
        ]
        for name, (lx, ly) in corners:
            rx_c, ry_c = self.rotate_point(lx, ly, rad)
            corner_pos = (scx + rx_c, scy + ry_c)
            if self.dist((sx, sy), corner_pos) < 10:
                if name in ("tl", "br"):
                    self.label_view.setCursor(Qt.CursorShape.SizeFDiagCursor)
                else:
                    self.label_view.setCursor(Qt.CursorShape.SizeBDiagCursor)
                return

        # 3. Survol du corps de la forme
        dx = sx - scx
        dy = sy - scy
        lx, ly = self.rotate_point(dx, dy, -rad)

        inside = False
        if shape.shape_type == "circle":
            inside = (lx / (sw/2))**2 + (ly / (sh/2))**2 <= 1.0
        else:
            inside = abs(lx) <= sw/2 and abs(ly) <= sh/2

        if inside:
            self.label_view.setCursor(Qt.CursorShape.SizeAllCursor)
        else:
            self.label_view.setCursor(Qt.CursorShape.CrossCursor)

    def delete_selected(self) -> bool:
        """Supprime la forme sélectionnée de la liste."""
        if self.selected_shape is not None:
            if self.selected_shape in self.shapes:
                self.shapes.remove(self.selected_shape)
                self.selected_shape = None
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
        """Rendu graphique principal de l'overlay."""
        # 1. Dessiner toutes les formes persistantes
        for shape in self.shapes:
            self.draw_shape(painter, img_rect, shape)

        # 2. Dessiner la forme temporaire de création
        if self.rel_a is not None:
            target = None
            if self.rel_b is not None:
                target = self.rel_b
            elif self.rel_temp is not None:
                target = self.rel_temp

            if target is None:
                screen_ax, screen_ay = self.to_screen(self.rel_a[0], self.rel_a[1], img_rect)
                painter.save()
                painter.setPen(QPen(QColor("#ffaa00"), 6, Qt.PenStyle.SolidLine))
                painter.drawPoint(QPoint(int(screen_ax), int(screen_ay)))
                painter.restore()
            else:
                self.draw_preview_shape(painter, img_rect, self.shape_type, self.rel_a, target)

    def draw_shape(self, painter: QPainter, img_rect: QRect, shape: Shape):
        """Dessine une forme persistante."""
        scx, scy = self.to_screen(shape.cx, shape.cy, img_rect)
        sw = shape.w * img_rect.width()
        sh = shape.h * img_rect.height()

        painter.save()
        painter.translate(scx, scy)
        painter.rotate(shape.rotation)

        pen_color = QColor("#00a2ed") if shape.selected else QColor("#ffaa00")
        pen_outline = QPen(pen_color, 2, Qt.PenStyle.SolidLine)
        painter.setPen(pen_outline)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        if shape.shape_type == "circle":
            painter.drawEllipse(QRectF(-sw/2, -sh/2, sw, sh))
        else:
            painter.drawRect(QRectF(-sw/2, -sh/2, sw, sh))

        painter.restore()

        # Si sélectionnée, dessiner les poignées de contrôle et les statistiques
        if shape.selected:
            self.draw_shape_handles(painter, img_rect, shape)
            self.draw_shape_stats(painter, img_rect, shape)

    def draw_shape_handles(self, painter: QPainter, img_rect: QRect, shape: Shape):
        """Dessine le cadre de sélection et les poignées d'un objet sélectionné."""
        scx, scy = self.to_screen(shape.cx, shape.cy, img_rect)
        sw = shape.w * img_rect.width()
        sh = shape.h * img_rect.height()

        painter.save()
        painter.translate(scx, scy)
        painter.rotate(shape.rotation)

        # Dessiner le cadre de sélection en tirets bleus
        pen_bbox = QPen(QColor("#00a2ed"), 1, Qt.PenStyle.DashLine)
        painter.setPen(pen_bbox)
        painter.drawRect(QRectF(-sw/2, -sh/2, sw, sh))

        # Ligne de liaison vers la poignée de rotation
        painter.drawLine(QPointF(0, -sh/2), QPointF(0, -sh/2 - 25))

        # Dessiner les poignées d'angle
        painter.setPen(QPen(QColor("#00a2ed"), 1, Qt.PenStyle.SolidLine))
        painter.setBrush(QColor("#ffffff"))
        handle_size = 8
        painter.drawRect(QRectF(-sw/2 - handle_size/2, -sh/2 - handle_size/2, handle_size, handle_size))
        painter.drawRect(QRectF(sw/2 - handle_size/2, -sh/2 - handle_size/2, handle_size, handle_size))
        painter.drawRect(QRectF(-sw/2 - handle_size/2, sh/2 - handle_size/2, handle_size, handle_size))
        painter.drawRect(QRectF(sw/2 - handle_size/2, sh/2 - handle_size/2, handle_size, handle_size))

        # Poignée de rotation
        painter.setBrush(QColor("#00a2ed"))
        painter.drawEllipse(QPointF(0, -sh/2 - 25), handle_size/2, handle_size/2)

        painter.restore()

    def draw_preview_shape(self, painter: QPainter, img_rect: QRect, shape_type: str, rel_a, rel_b):
        """Dessine l'aperçu dynamique lors du tracé initial."""
        screen_ax, screen_ay = self.to_screen(rel_a[0], rel_a[1], img_rect)
        screen_bx, screen_by = self.to_screen(rel_b[0], rel_b[1], img_rect)

        pen_preview = QPen(QColor("#ffaa00"), 2, Qt.PenStyle.DashLine)
        pen_dots = QPen(QColor("#ffaa00"), 6, Qt.PenStyle.SolidLine)
        painter.save()
        painter.setPen(pen_preview)

        if shape_type == "circle":
            screen_r = int(math.sqrt((screen_bx - screen_ax)**2 + (screen_by - screen_ay)**2))
            painter.drawEllipse(QPoint(int(screen_ax), int(screen_ay)), screen_r, screen_r)
            painter.setPen(pen_dots)
            painter.drawPoint(QPoint(int(screen_ax), int(screen_ay)))
            painter.drawPoint(QPoint(int(screen_bx), int(screen_by)))
        else:
            s_xmin = min(screen_ax, screen_bx)
            s_xmax = max(screen_ax, screen_bx)
            s_ymin = min(screen_ay, screen_by)
            s_ymax = max(screen_ay, screen_by)
            painter.drawRect(QRect(QPoint(int(s_xmin), int(s_ymin)), QPoint(int(s_xmax), int(s_ymax))))
            painter.setPen(pen_dots)
            painter.drawPoint(QPoint(int(screen_ax), int(screen_ay)))
            painter.drawPoint(QPoint(int(screen_bx), int(screen_by)))
        painter.restore()

    def draw_shape_stats(self, painter: QPainter, img_rect: QRect, shape: Shape):
        """Calcule les statistiques et dessine la boîte d'informations."""
        raw_pixels, unit = self.get_raw_pixels()
        if raw_pixels is None:
            return

        orig_h, orig_w = raw_pixels.shape
        orig_cx = shape.cx * orig_w
        orig_cy = shape.cy * orig_h
        orig_rw = shape.w * orig_w
        orig_rh = shape.h * orig_h

        # Calculer le AABB (Axis-Aligned Bounding Box) pour limiter la zone de scan
        orig_rad = math.radians(shape.rotation)
        orig_corners = [
            self.rotate_point(-orig_rw/2, -orig_rh/2, orig_rad),
            self.rotate_point(orig_rw/2, -orig_rh/2, orig_rad),
            self.rotate_point(-orig_rw/2, orig_rh/2, orig_rad),
            self.rotate_point(orig_rw/2, orig_rh/2, orig_rad)
        ]
        orig_xs = [orig_cx + dx for dx, dy in orig_corners]
        orig_ys = [orig_cy + dy for dx, dy in orig_corners]

        xmin = max(0, int(math.floor(min(orig_xs))))
        xmax = min(orig_w - 1, int(math.ceil(max(orig_xs))))
        ymin = max(0, int(math.floor(min(orig_ys))))
        ymax = min(orig_h - 1, int(math.ceil(max(orig_ys))))

        # Extraction vectorisée NumPy avec rotation inverse pour le calcul du masque
        if xmax >= xmin and ymax >= ymin:
            Y, X = np.ogrid[ymin:ymax+1, xmin:xmax+1]
            cos_a = math.cos(orig_rad)
            sin_a = math.sin(orig_rad)
            
            # Transformation inverse vers le repère local de la ROI
            local_X = (X - orig_cx) * cos_a + (Y - orig_cy) * sin_a
            local_Y = -(X - orig_cx) * sin_a + (Y - orig_cy) * cos_a

            if shape.shape_type == "circle":
                # Le cercle utilise orig_rw comme diamètre (équivalent à sw à l'échelle d'origine)
                mask = (local_X**2 + local_Y**2) <= (orig_rw / 2.0)**2
            else:
                mask = (np.abs(local_X) <= orig_rw / 2.0) & (np.abs(local_Y) <= orig_rh / 2.0)

            sub_pixels = raw_pixels[ymin:ymax+1, xmin:xmax+1]
            values = sub_pixels[mask]
        else:
            values = np.array([])

        if values.size > 0:
            mean_val = np.mean(values)
            max_val = np.max(values)
            min_val = np.min(values)
            sd_val = np.std(values)
            num_pixels = values.size
        else:
            mean_val = max_val = min_val = sd_val = num_pixels = 0

        # Aire physique en cm²
        largeur_physique_totale_cm = 45.0
        dynamic_pixel_to_cm = largeur_physique_totale_cm / orig_w
        pixel_area_cm2 = dynamic_pixel_to_cm ** 2
        area_cm2 = num_pixels * pixel_area_cm2

        unit_str = f" {unit}" if unit else ""
        text_lines = [
            f"Moy: {mean_val:.2f}{unit_str}",
            f"Max: {max_val:.2f} / Min: {min_val:.2f}",
            f"SD: {sd_val:.2f}",
            f"Aire: {num_pixels} px² (~ {area_cm2:.2f} cm²)"
        ]

        font = QFont("Arial", 10, QFont.Weight.Bold)
        painter.save()
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

        # Position de la boîte sur l'écran
        sw = shape.w * img_rect.width()
        sh = shape.h * img_rect.height()
        screen_corners = [
            self.rotate_point(-sw/2, -sh/2, orig_rad),
            self.rotate_point(sw/2, -sh/2, orig_rad),
            self.rotate_point(-sw/2, sh/2, orig_rad),
            self.rotate_point(sw/2, sh/2, orig_rad)
        ]
        scx, scy = self.to_screen(shape.cx, shape.cy, img_rect)
        xs = [scx + dx for dx, dy in screen_corners]
        ys = [scy + dy for dx, dy in screen_corners]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        text_x = max_x + 15
        text_y = (min_y + max_y) // 2 - box_h // 2

        if text_x + box_w > img_rect.right():
            text_x = min_x - box_w - 15

        text_x = max(img_rect.left() + 5, min(text_x, img_rect.right() - box_w - 5))
        text_y = max(img_rect.top() + 5, min(text_y, img_rect.bottom() - box_h - 5))

        # Dessiner le cartouche
        text_rect = QRect(int(text_x), int(text_y), int(box_w), int(box_h))
        painter.fillRect(text_rect, QColor(0, 0, 0, 180))
        painter.setPen(QPen(QColor("#ffaa00"), 1))
        painter.drawRect(text_rect)

        # Dessiner le texte
        painter.setPen(QColor("#ffaa00"))
        for i, line in enumerate(text_lines):
            line_y = text_y + 6 + i * line_height + metrics.ascent()
            painter.drawText(int(text_x + 8), int(line_y), line)
        painter.restore()
