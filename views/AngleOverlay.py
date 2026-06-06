import math
from PyQt6.QtCore import Qt, QPoint, QRect
from PyQt6.QtGui import QPainter, QPen, QColor, QFont


class AngleOverlay:
    def __init__(self, label_view):
        self.label_view = label_view
        # Liste de points relatifs (pourcentages de l'image de 0.0 à 1.0)
        self.pts = []

    def clear(self):
        """Réinitialise les points de mesure."""
        self.pts = []

    def handle_mouse_press(self, local_pos: QPoint, img_rect: QRect) -> bool:
        """Enregistre la position du clic sous forme relative si elle se trouve sur l'image."""
        if not img_rect.contains(local_pos):
            return False

        # Conversion en coordonnées relatives (0.0 à 1.0) par rapport à l'image affichée
        rel_x = (local_pos.x() - img_rect.left()) / img_rect.width()
        rel_y = (local_pos.y() - img_rect.top()) / img_rect.height()

        if len(self.pts) >= 4:
            # Si on a déjà placé 4 points, on redémarre une nouvelle mesure
            self.pts = []

        self.pts.append((rel_x, rel_y))
        return True

    def draw_measure(self, painter: QPainter, img_rect: QRect):
        """Dessine les points, les droites, et affiche l'angle mesuré."""
        if not self.pts:
            return

        # 1. Configuration des stylos
        pen_dots = QPen(QColor("#ffaa00"), 6, Qt.PenStyle.SolidLine)
        pen_line1 = QPen(QColor("#00a2ed"), 2, Qt.PenStyle.SolidLine)
        pen_line2 = QPen(QColor("#2ecc71"), 2, Qt.PenStyle.SolidLine)

        # 2. Conversion des points relatifs en coordonnées réelles à l'écran
        screen_pts = []
        for pt in self.pts:
            sx = int(img_rect.left() + pt[0] * img_rect.width())
            sy = int(img_rect.top() + pt[1] * img_rect.height())
            screen_pts.append(QPoint(sx, sy))

        # 3. Dessiner les points
        painter.setPen(pen_dots)
        for pt in screen_pts:
            painter.drawPoint(pt)

        # 4. Dessiner la première droite (si >= 2 points)
        if len(screen_pts) >= 2:
            painter.setPen(pen_line1)
            painter.drawLine(screen_pts[0], screen_pts[1])

        # 5. Dessiner la deuxième droite et calculer l'angle (si == 4 points)
        if len(screen_pts) >= 4:
            painter.setPen(pen_line2)
            painter.drawLine(screen_pts[2], screen_pts[3])

            p1, p2 = screen_pts[0], screen_pts[1]
            p3, p4 = screen_pts[2], screen_pts[3]

            # Vecteurs directeurs
            dx1 = p2.x() - p1.x()
            dy1 = p2.y() - p1.y()
            dx2 = p4.x() - p3.x()
            dy2 = p4.y() - p3.y()

            # Produit scalaire et normes
            dot_product = dx1 * dx2 + dy1 * dy2
            mag1 = math.sqrt(dx1**2 + dy1**2)
            mag2 = math.sqrt(dx2**2 + dy2**2)

            if mag1 > 0 and mag2 > 0:
                # Calcul de l'angle aigu entre les deux droites
                cos_theta = max(-1.0, min(1.0, dot_product / (mag1 * mag2)))
                angle_rad = math.acos(cos_theta)
                angle_deg = math.degrees(angle_rad)
                if angle_deg > 90.0:
                    angle_deg = 180.0 - angle_deg
            else:
                angle_deg = 0.0

            # 6. Calcul du point d'intersection théorique des deux droites
            # Droite 1 : a1*x + b1*y = c1
            a1 = p2.y() - p1.y()
            b1 = p1.x() - p2.x()
            c1 = a1 * p1.x() + b1 * p1.y()

            # Droite 2 : a2*x + b2*y = c2
            a2 = p4.y() - p3.y()
            b2 = p3.x() - p4.x()
            c2 = a2 * p3.x() + b2 * p3.y()

            det = a1 * b2 - a2 * b1
            intersect_pt = None

            if abs(det) > 1e-5:
                ix = (c1 * b2 - c2 * b1) / det
                iy = (a1 * c2 - a2 * c1) / det
                intersect_pt = QPoint(int(ix), int(iy))

            # 7. Positionnement et affichage du texte de l'angle
            text = f" {angle_deg:.1f}° "
            font = QFont("Arial", 10, QFont.Weight.Bold)
            painter.setFont(font)
            text_rect = painter.fontMetrics().boundingRect(text)

            if intersect_pt and img_rect.contains(intersect_pt):
                # Si l'intersection est visible sur l'image, on affiche à côté
                text_pos = intersect_pt + QPoint(15, -15)
                text_rect.moveCenter(text_pos)

                # Dessiner un point rouge sur l'intersection
                pen_intersect = QPen(QColor("#e74c3c"), 6, Qt.PenStyle.SolidLine)
                painter.setPen(pen_intersect)
                painter.drawPoint(intersect_pt)
            else:
                # Sinon, au milieu des centres des deux segments
                mid1 = QPoint((p1.x() + p2.x()) // 2, (p1.y() + p2.y()) // 2)
                mid2 = QPoint((p3.x() + p4.x()) // 2, (p3.y() + p4.y()) // 2)
                text_pos = QPoint((mid1.x() + mid2.x()) // 2, (mid1.y() + mid2.y()) // 2)
                text_rect.moveCenter(text_pos)

            # Dessin de l'étiquette de l'angle
            painter.fillRect(text_rect, QColor(0, 0, 0, 180))
            painter.setPen(QColor("#ffffff"))
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)
