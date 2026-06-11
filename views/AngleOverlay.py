import math
from PyQt6.QtCore import Qt, QPoint, QRect
from PyQt6.QtGui import QPainter, QPen, QColor, QFont


class AngleOverlay:
    def __init__(self, label_view):
        self.label_view = label_view
        # Liste de points relatifs (pourcentages de l'image de 0.0 à 1.0), max 3 points
        self.pts = []
        self.rel_temp = None  # Position temporaire pour le tracé en direct

    def clear(self):
        """Réinitialise les points de mesure."""
        self.pts = []
        self.rel_temp = None

    def handle_mouse_press(self, local_pos: QPoint, img_rect: QRect) -> bool:
        """Enregistre la position du clic sous forme relative si elle se trouve sur l'image."""
        if not img_rect.contains(local_pos):
            return False

        # Conversion en coordonnées relatives (0.0 à 1.0)
        rel_x = (local_pos.x() - img_rect.left()) / img_rect.width()
        rel_y = (local_pos.y() - img_rect.top()) / img_rect.height()

        if len(self.pts) >= 3:
            # Si on a déjà placé 3 points, on redémarre une nouvelle mesure
            self.pts = []

        self.pts.append((rel_x, rel_y))
        self.rel_temp = None
        return True

    def handle_mouse_move(self, local_pos: QPoint, img_rect: QRect) -> bool:
        """Met à jour le point temporaire pour le tracé en direct de l'angle."""
        if not self.pts or len(self.pts) >= 3:
            # Aucun tracé en cours ou tracé déjà complet
            if self.rel_temp is not None:
                self.rel_temp = None
                return True
            return False

        # Clamping de la position de la souris pour qu'elle reste dans l'image
        img_x = max(0, min(local_pos.x() - img_rect.left(), img_rect.width()))
        img_y = max(0, min(local_pos.y() - img_rect.top(), img_rect.height()))

        rel_x = img_x / img_rect.width()
        rel_y = img_y / img_rect.height()
        new_temp = (rel_x, rel_y)

        if self.rel_temp != new_temp:
            self.rel_temp = new_temp
            return True

        return False

    def calculate_angle(self, p1: QPoint, p2: QPoint, p3: QPoint) -> float:
        """Calcule l'angle en degrés au sommet p2 formé par les segments p1-p2 et p3-p2."""
        dx1 = p1.x() - p2.x()
        dy1 = p1.y() - p2.y()
        dx2 = p3.x() - p2.x()
        dy2 = p3.y() - p2.y()

        # Produit scalaire et normes
        dot_product = dx1 * dx2 + dy1 * dy2
        mag1 = math.sqrt(dx1**2 + dy1**2)
        mag2 = math.sqrt(dx2**2 + dy2**2)

        if mag1 > 0 and mag2 > 0:
            cos_theta = max(-1.0, min(1.0, dot_product / (mag1 * mag2)))
            angle_rad = math.acos(cos_theta)
            angle_deg = math.degrees(angle_rad)
        else:
            angle_deg = 0.0

        return angle_deg

    def draw_angle_label(self, painter: QPainter, angle_deg: float, vertex: QPoint, img_rect: QRect, is_preview: bool):
        """Dessine l'étiquette de l'angle à côté du sommet de l'angle."""
        text = f" {angle_deg:.1f}° "
        font = QFont("Arial", 10, QFont.Weight.Bold)
        painter.setFont(font)
        text_rect = painter.fontMetrics().boundingRect(text)

        # Décalage par rapport au sommet pour ne pas masquer le point
        text_pos = vertex + QPoint(15, -15)
        text_rect.moveCenter(text_pos)

        # Clamping pour forcer l'étiquette à rester visible dans les limites de l'image
        if text_rect.left() < img_rect.left():
            text_rect.moveLeft(img_rect.left())
        if text_rect.right() > img_rect.right():
            text_rect.moveRight(img_rect.right())
        if text_rect.top() < img_rect.top():
            text_rect.moveTop(img_rect.top())
        if text_rect.bottom() > img_rect.bottom():
            text_rect.moveBottom(img_rect.bottom())

        painter.fillRect(text_rect, QColor(0, 0, 0, 180))
        if is_preview:
            painter.setPen(QColor("#ffaa00"))  # Orange/jaune pour la prévisualisation
        else:
            painter.setPen(QColor("#ffffff"))  # Blanc pour la mesure validée
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)

    def draw_measure(self, painter: QPainter, img_rect: QRect):
        """Dessine les points, les lignes, et affiche l'angle mesuré."""
        if not self.pts:
            return

        # 1. Stylos
        pen_dots = QPen(QColor("#ffaa00"), 6, Qt.PenStyle.SolidLine)
        pen_line1 = QPen(QColor("#00a2ed"), 2, Qt.PenStyle.SolidLine)
        pen_line2 = QPen(QColor("#2ecc71"), 2, Qt.PenStyle.SolidLine)
        pen_preview_line = QPen(QColor("#2ecc71"), 2, Qt.PenStyle.DashLine)

        # 2. Conversion en coordonnées écran
        screen_pts = []
        for pt in self.pts:
            sx = int(img_rect.left() + pt[0] * img_rect.width())
            sy = int(img_rect.top() + pt[1] * img_rect.height())
            screen_pts.append(QPoint(sx, sy))

        # 3. Dessiner les points existants
        painter.setPen(pen_dots)
        for pt in screen_pts:
            painter.drawPoint(pt)

        # 4. Dessiner le premier segment
        if len(screen_pts) == 1 and self.rel_temp is not None:
            # Premier segment en cours de tracé (preview)
            temp_x = int(img_rect.left() + self.rel_temp[0] * img_rect.width())
            temp_y = int(img_rect.top() + self.rel_temp[1] * img_rect.height())
            temp_pt = QPoint(temp_x, temp_y)

            painter.setPen(QPen(QColor("#00a2ed"), 2, Qt.PenStyle.DashLine))
            painter.drawLine(screen_pts[0], temp_pt)
            painter.setPen(pen_dots)
            painter.drawPoint(temp_pt)

        elif len(screen_pts) >= 2:
            # Premier segment finalisé
            painter.setPen(pen_line1)
            painter.drawLine(screen_pts[0], screen_pts[1])

        # 5. Dessiner le second segment (attaché à l'un des côtés du premier segment, ici le sommet B)
        # Cas 1 : 2 points posés, 3ème point en cours de déplacement (preview)
        if len(screen_pts) == 2 and self.rel_temp is not None:
            temp_x = int(img_rect.left() + self.rel_temp[0] * img_rect.width())
            temp_y = int(img_rect.top() + self.rel_temp[1] * img_rect.height())
            temp_pt = QPoint(temp_x, temp_y)

            # Deuxième segment en pointillés attachée au 2ème point (vertex)
            painter.setPen(pen_preview_line)
            painter.drawLine(screen_pts[1], temp_pt)
            painter.setPen(pen_dots)
            painter.drawPoint(temp_pt)

            # Calcul et affichage de l'angle en direct
            angle_deg = self.calculate_angle(screen_pts[0], screen_pts[1], temp_pt)
            self.draw_angle_label(painter, angle_deg, screen_pts[1], img_rect, is_preview=True)

        # Cas 2 : 3 points posés (mesure finale fixée)
        elif len(screen_pts) == 3:
            painter.setPen(pen_line2)
            painter.drawLine(screen_pts[1], screen_pts[2])

            angle_deg = self.calculate_angle(screen_pts[0], screen_pts[1], screen_pts[2])
            self.draw_angle_label(painter, angle_deg, screen_pts[1], img_rect, is_preview=False)
