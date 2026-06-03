import math
from PyQt6.QtCore import Qt, QPoint, QRect
from PyQt6.QtGui import QPainter, QPen, QColor, QFont

class RulerOverlay:
    def __init__(self, label_view):
        self.label_view = label_view
        
        # Points pour l'affichage à l'écran
        self.screen_a = None
        self.screen_b = None
        
        # pixels originaux
        self.orig_a = None
        self.orig_b = None
        
        self.pixel_to_cm = 0.14

    def clear(self):
        """Réinitialise les points de mesure."""
        self.screen_a = None
        self.screen_b = None
        self.orig_a = None
        self.orig_b = None

    def handle_mouse_press(self, local_pos: QPoint, img_rect: QRect, scale_x: float, scale_y: float):
        """Gère le placement des points en enregistrant les coordonnées écran ET d'origine."""
        if not img_rect.contains(local_pos):
            return False

        # Calcul de la position
        img_x = local_pos.x() - img_rect.left()
        img_y = local_pos.y() - img_rect.top()

        pixel_orig_x = int(img_x * scale_x)
        pixel_orig_y = int(img_y * scale_y)
        pos_origin = QPoint(pixel_orig_x, pixel_orig_y)

        if self.screen_a is None or (self.screen_a is not None and self.screen_b is not None):
            self.screen_a = local_pos
            self.orig_a = pos_origin
            self.screen_b = None
            self.orig_b = None
        elif self.screen_b is None:
            self.screen_b = local_pos
            self.orig_b = pos_origin
            
        return True

    def draw_measure(self, painter: QPainter, img_rect: QRect):
        """Dessine la ligne sur l'écran mais calcule la distance sur les pixels d'origine."""
        if self.screen_a is None:
            return

        pen_line = QPen(QColor("#00ff00"), 2, Qt.PenStyle.SolidLine)
        pen_dots = QPen(QColor("#ffaa00"), 6, Qt.PenStyle.SolidLine)
        
        # premier point
        painter.setPen(pen_dots)
        painter.drawPoint(self.screen_a)

        # deuxième point posé
        if self.screen_b is not None and self.orig_a is not None and self.orig_b is not None:
            painter.setPen(pen_line)
            painter.drawLine(self.screen_a, self.screen_b)
            painter.setPen(pen_dots)
            painter.drawPoint(self.screen_b)

            # --- LE CALCUL FIXE SUR L'IMAGE D'ORIGINE ---
            dx = self.orig_b.x() - self.orig_a.x()
            dy = self.orig_b.y() - self.orig_a.y()
            distance_px_orig = math.sqrt(dx*dx + dy*dy)
            
            distance_cm = distance_px_orig * self.pixel_to_cm
            # Texte distance
            mid_x = (self.screen_a.x() + self.screen_b.x()) // 2
            mid_y = (self.screen_a.y() + self.screen_b.y()) // 2

            text = f" {distance_cm:.2f} cm "
            font = QFont("Arial", 10, QFont.Weight.Bold)
            painter.setFont(font)
            
            text_rect = painter.fontMetrics().boundingRect(text)
            text_rect.moveCenter(QPoint(mid_x, mid_y))
            
            painter.fillRect(text_rect, QColor(0, 0, 0, 180))
            painter.setPen(QColor("#ffffff"))
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)