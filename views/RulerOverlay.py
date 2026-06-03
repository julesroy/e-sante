import math
from PyQt6.QtCore import Qt, QPoint, QRect
from PyQt6.QtGui import QPainter, QPen, QColor, QFont

class RulerOverlay:
    def __init__(self, label_view):
        self.label_view = label_view
        
        # Positions relatives unifiées (en pourcentage de l'image de 0.0 à 1.0)
        self.rel_a = None
        self.rel_b = None
        
        self.pixel_to_cm = 0.14

    def clear(self):
        """Réinitialise les points de mesure."""
        self.rel_a = None
        self.rel_b = None

    def handle_mouse_press(self, local_pos: QPoint, img_rect: QRect):
        """Calcule et stocke la position du clic en valeurs relatives (0 à 1)."""
        if not img_rect.contains(local_pos):
            return False

        # Calcul de la position à l'intérieur de la zone de la radio (sans les marges)
        img_x = local_pos.x() - img_rect.left()
        img_y = local_pos.y() - img_rect.top()

        # Conversion en valeurs relatives (pourcentages de 0.0 à 1.0)
        rel_x = img_x / img_rect.width()
        rel_y = img_y / img_rect.height()
        pos_relative = (rel_x, rel_y)

        # Logique de clic alternatif pour poser A puis B
        if self.rel_a is None or (self.rel_a is not None and self.rel_b is not None):
            self.rel_a = pos_relative
            self.rel_b = None
        elif self.rel_b is None:
            self.rel_b = pos_relative
            
        return True

    def draw_measure(self, painter: QPainter, img_rect: QRect):
        """Calcule dynamiquement la distance en se basant sur une largeur physique d'image fixe."""
        if self.rel_a is None:
            return

        # 1. Reconstitution des positions réelles à l'écran à partir des pourcentages
        screen_ax = int(img_rect.left() + (self.rel_a[0] * img_rect.width()))
        screen_ay = int(img_rect.top() + (self.rel_a[1] * img_rect.height()))
        screen_a = QPoint(screen_ax, screen_ay)

        pen_line = QPen(QColor("#00ff00"), 2, Qt.PenStyle.SolidLine)
        pen_dots = QPen(QColor("#ffaa00"), 6, Qt.PenStyle.SolidLine)
        
        # Dessiner le premier point
        painter.setPen(pen_dots)
        painter.drawPoint(screen_a)

        # 2. Dessiner la ligne et calculer la vraie distance si le point B existe
        if self.rel_b is not None:
            screen_bx = int(img_rect.left() + (self.rel_b[0] * img_rect.width()))
            screen_by = int(img_rect.top() + (self.rel_b[1] * img_rect.height()))
            screen_b = QPoint(screen_bx, screen_by)

            # Dessin de la ligne écran
            painter.setPen(pen_line)
            painter.drawLine(screen_a, screen_b)
            painter.setPen(pen_dots)
            painter.drawPoint(screen_b)

            # --- CALCUL DYNAMIQUE ET UNIVERSEL ---
            main_view = self.label_view.visualizer.main_view
            if main_view and main_view.current_pixmap:
                orig_w = main_view.current_pixmap.width()
                orig_h = main_view.current_pixmap.height()

                # ÉVALUATION DU COEF : On considère que l'image fait toujours 45 cm de large en vrai
                largeur_physique_totale_cm = 45.0
                dynamic_pixel_to_cm = largeur_physique_totale_cm / orig_w

                # On projette nos pourcentages directement sur la taille du fichier d'origine
                orig_ax, orig_ay = self.rel_a[0] * orig_w, self.rel_a[1] * orig_h
                orig_bx, orig_by = self.rel_b[0] * orig_w, self.rel_b[1] * orig_h

                # Pythagore sur l'image brute de base
                dx = orig_bx - orig_ax
                dy = orig_by - orig_ay
                distance_px_orig = math.sqrt(dx*dx + dy*dy)
                
                # Conversion finale avec le coefficient dynamique
                distance_cm = distance_px_orig * dynamic_pixel_to_cm
            else:
                distance_cm = 0.0

            # Positionnement du texte au milieu de la ligne
            mid_x = (screen_a.x() + screen_b.x()) // 2
            mid_y = (screen_a.y() + screen_b.y()) // 2

            text = f" {distance_cm:.2f} cm "
            font = QFont("Arial", 10, QFont.Weight.Bold)
            painter.setFont(font)
            
            text_rect = painter.fontMetrics().boundingRect(text)
            text_rect.moveCenter(QPoint(mid_x, mid_y))
            
            painter.fillRect(text_rect, QColor(0, 0, 0, 180))
            painter.setPen(QColor("#ffffff"))
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)