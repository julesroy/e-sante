import math
from PyQt6.QtCore import Qt, QPoint, QRect
from PyQt6.QtGui import QPainter, QPen, QColor, QFont

class RulerOverlay:
    def __init__(self, label_view):
        self.label_view = label_view
        self.point_a = None
        self.point_b = None
        # def taille des px
        self.pixel_to_cm = 0.02

    def clear(self):
        """Réinitialise les points de mesure."""
        self.point_a = None
        self.point_b = None

    def handle_mouse_press(self, local_pos: QPoint, img_rect: QRect):
        """Gère le placement alternatif des points A et B à l'intérieur de l'image."""
        if not img_rect.contains(local_pos):
            return False

        # Si aucun point n'est placé, ou si les deux le sont déjà, on démarre une nouvelle mesure
        if self.point_a is None or (self.point_a is not None and self.point_b is not None):
            self.point_a = local_pos
            self.point_b = None
        elif self.point_b is None:
            self.point_b = local_pos
            
        return True

    def draw_measure(self, painter: QPainter, img_rect: QRect):
        """Dessine la ligne de mesure et le texte de distance en centimètres."""
        if self.point_a is None:
            return

        # Configuration du crayon pour la mesure (Vert vif médical)
        pen_line = QPen(QColor("#00ff00"), 2, Qt.PenStyle.SolidLine)
        pen_dots = QPen(QColor("#ffaa00"), 6, Qt.PenStyle.SolidLine)
        
        # 1. Dessiner le premier point d'ancrage
        painter.setPen(pen_dots)
        painter.drawPoint(self.point_a)

        # 2. Dessiner la ligne et le texte si le point B est posé
        if self.point_b is not None:
            painter.setPen(pen_line)
            painter.drawLine(self.point_a, self.point_b)
            painter.setPen(pen_dots)
            painter.drawPoint(self.point_b)

            # Calcul de la distance géométrique (Pythagore)
            dx = self.point_b.x() - self.point_a.x()
            dy = self.point_b.y() - self.point_a.y()
            distance_px = math.sqrt(dx*dx + dy*dy)
            
            # Conversion en centimètres
            distance_cm = distance_px * self.pixel_to_cm

            # Calcul du centre de la ligne pour positionner le texte
            mid_x = (self.point_a.x() + self.point_b.x()) // 2
            mid_y = (self.point_a.y() + self.point_b.y()) // 2

            # Dessiner un petit fond noir sous le texte pour le rendre lisible
            text = f" {distance_cm:.2f} cm "
            font = QFont("Arial", 10, QFont.Weight.Bold)
            painter.setFont(font)
            
            # Ajustement du rectangle de texte
            text_rect = painter.fontMetrics().boundingRect(text)
            text_rect.moveCenter(QPoint(mid_x, mid_y))
            
            painter.fillRect(text_rect, QColor(0, 0, 0, 180))
            painter.setPen(QColor("#ffffff"))
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)