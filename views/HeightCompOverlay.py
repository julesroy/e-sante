import math
from PyQt6.QtCore import Qt, QPoint, QRect
from PyQt6.QtGui import QPainter, QPen, QColor, QFont


class HeightCompOverlay:
    def __init__(self, label_view):
        self.label_view = label_view
        # Liste de points relatifs (pourcentages de l'image de 0.0 à 1.0), max 2 points
        self.pts = []

    def clear(self):
        """Réinitialise les points de mesure."""
        self.pts = []

    def handle_mouse_press(self, local_pos: QPoint, img_rect: QRect) -> bool:
        """Enregistre la position du clic sous forme relative si elle se trouve sur l'image."""
        if not img_rect.contains(local_pos):
            return False

        # Conversion en coordonnées relatives (0.0 à 1.0)
        rel_x = (local_pos.x() - img_rect.left()) / img_rect.width()
        rel_y = (local_pos.y() - img_rect.top()) / img_rect.height()

        if len(self.pts) >= 2:
            # Si on a déjà placé 2 points, on redémarre une nouvelle mesure
            self.pts = []

        self.pts.append((rel_x, rel_y))
        return True

    def draw_measure(self, painter: QPainter, img_rect: QRect):
        """Dessine les lignes de référence horizontales et l'écart vertical en cm."""
        if not self.pts:
            return

        # 1. Stylos
        pen_dots = QPen(QColor("#ffaa00"), 6, Qt.PenStyle.SolidLine)
        pen_line = QPen(QColor("#00a2ed"), 1, Qt.PenStyle.DashLine)
        pen_vertical = QPen(QColor("#2ecc71"), 2, Qt.PenStyle.SolidLine)

        # 2. Conversion en coordonnées réelles écran
        screen_pts = []
        for pt in self.pts:
            sx = int(img_rect.left() + pt[0] * img_rect.width())
            sy = int(img_rect.top() + pt[1] * img_rect.height())
            screen_pts.append(QPoint(sx, sy))

        # 3. Dessiner les points
        painter.setPen(pen_dots)
        for pt in screen_pts:
            painter.drawPoint(pt)

        # 4. Dessiner le premier plan horizontal (pour Point A)
        y1 = screen_pts[0].y()
        painter.setPen(pen_line)
        painter.drawLine(img_rect.left(), y1, img_rect.right(), y1)

        # 5. Si le deuxième point est placé, dessiner le deuxième plan et le différentiel
        if len(screen_pts) >= 2:
            y2 = screen_pts[1].y()
            painter.drawLine(img_rect.left(), y2, img_rect.right(), y2)

            # Calcul du milieu horizontal entre les deux points pour placer la ligne de liaison verticale
            mid_x = (screen_pts[0].x() + screen_pts[1].x()) // 2

            # Dessiner la ligne de liaison verticale entre y1 et y2
            painter.setPen(pen_vertical)
            painter.drawLine(mid_x, y1, mid_x, y2)

            # --- CALCUL DE LA DISTANCE PHYSIQUE (CALIBRATION) ---
            main_view = self.label_view.visualizer.main_view
            if main_view and main_view.current_pixmap:
                orig_w = main_view.current_pixmap.width()
                orig_h = main_view.current_pixmap.height()

                # Même calibrage que RulerOverlay : l'image brute fait toujours 45 cm de large
                largeur_physique_totale_cm = 45.0
                dynamic_pixel_to_cm = largeur_physique_totale_cm / orig_w

                # Différence de hauteur relative projetée sur la hauteur de l'image d'origine
                dy_rel = abs(self.pts[0][1] - self.pts[1][1])
                dy_orig = dy_rel * orig_h

                # Distance en cm
                distance_cm = dy_orig * dynamic_pixel_to_cm
            else:
                distance_cm = 0.0

            # 6. Affichage du texte au milieu de la liaison verticale
            text = f" Δy: {distance_cm:.2f} cm "
            font = QFont("Arial", 10, QFont.Weight.Bold)
            painter.setFont(font)
            text_rect = painter.fontMetrics().boundingRect(text)

            mid_y = (y1 + y2) // 2
            text_rect.moveCenter(QPoint(mid_x, mid_y))

            # Dessin de l'étiquette
            painter.fillRect(text_rect, QColor(0, 0, 0, 180))
            painter.setPen(QColor("#ffffff"))
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)
