import math
from PyQt6.QtCore import Qt, QPoint, QRect, QRectF, QPointF
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QFontMetrics
from PyQt6.QtWidgets import QInputDialog

class AnnotationsOverlay:
    def __init__(self, label_view):
        self.label_view = label_view
        self.drawings = []  # Liste de dictionnaires : {"points": [QPointF], "color": QColor, "width": int}
        self.texts = []     # Liste de dictionnaires : {"pos": QPointF, "text": str, "color": QColor, "size": int, "selected": bool}
        
        self.current_color = QColor("#ff0000")  # Rouge par défaut
        self.pen_width = 3
        
        self.active_stroke = None
        self.selected_text = None
        self.interaction_mode = None  # None, "moving_text"
        self.drag_offset = QPointF(0, 0)

    def clear(self):
        """Réinitialise l'état temporaire en cours."""
        self.active_stroke = None
        self.interaction_mode = None

    def clear_all(self):
        """Efface tous les tracés et textes."""
        self.clear()
        self.drawings = []
        self.texts = []
        self.selected_text = None

    def to_screen(self, rx, ry, img_rect: QRect):
        sx = img_rect.left() + rx * img_rect.width()
        sy = img_rect.top() + ry * img_rect.height()
        return sx, sy

    def to_relative(self, sx, sy, img_rect: QRect):
        rx = (sx - img_rect.left()) / img_rect.width()
        ry = (sy - img_rect.top()) / img_rect.height()
        return rx, ry

    def handle_mouse_press(self, local_pos: QPoint, img_rect: QRect) -> bool:
        """Gère le clic de la souris."""
        if not img_rect.contains(local_pos):
            return False

        sx = local_pos.x()
        sy = local_pos.y()
        rx, ry = self.to_relative(sx, sy, img_rect)
        p_rel = QPointF(rx, ry)

        main_view = self.label_view.visualizer.main_view
        if not main_view:
            return False

        # --- MODE STYLO ---
        if getattr(main_view, "pen_active", False):
            self.active_stroke = {
                "points": [p_rel],
                "color": QColor(self.current_color),
                "width": self.pen_width
            }
            return True

        # --- MODE TEXTE ---
        elif getattr(main_view, "text_anno_active", False):
            # 1. Vérifier si on clique sur un texte existant pour le sélectionner/déplacer
            for text_obj in reversed(self.texts):
                tsx, tsy = self.to_screen(text_obj["pos"].x(), text_obj["pos"].y(), img_rect)
                
                font = QFont("Arial", text_obj["size"])
                font.setBold(True)
                fm = QFontMetrics(font)
                tw = fm.horizontalAdvance(text_obj["text"])
                th = fm.height()
                
                text_rect = QRect(int(tsx - tw/2 - 4), int(tsy - th/2), tw + 8, th)
                if text_rect.contains(local_pos):
                    if self.selected_text:
                        self.selected_text["selected"] = False
                    self.selected_text = text_obj
                    text_obj["selected"] = True
                    self.interaction_mode = "moving_text"
                    self.drag_offset = QPointF(rx - text_obj["pos"].x(), ry - text_obj["pos"].y())
                    return True
            
            # 2. Clic dans le vide : créer une nouvelle annotation textuelle
            text_val, ok = QInputDialog.getText(
                self.label_view, "Ajouter une annotation", "Saisissez votre texte :"
            )
            if ok and text_val.strip():
                new_text = {
                    "pos": p_rel,
                    "text": text_val.strip(),
                    "color": QColor(self.current_color),
                    "size": 12,
                    "selected": True
                }
                if self.selected_text:
                    self.selected_text["selected"] = False
                self.selected_text = new_text
                self.texts.append(new_text)
                return True

        return False

    def handle_mouse_move(self, local_pos: QPoint, img_rect: QRect) -> bool:
        """Gère le glissement de la souris."""
        sx = local_pos.x()
        sy = local_pos.y()

        img_x = max(img_rect.left(), min(sx, img_rect.right()))
        img_y = max(img_rect.top(), min(sy, img_rect.bottom()))
        rx, ry = self.to_relative(img_x, img_y, img_rect)

        # --- MODE STYLO : Accumuler les points du tracé libre ---
        if self.active_stroke is not None:
            self.active_stroke["points"].append(QPointF(rx, ry))
            return True

        # --- MODE TEXTE : Déplacer le texte sélectionné ---
        elif self.interaction_mode == "moving_text" and self.selected_text:
            self.selected_text["pos"] = QPointF(rx - self.drag_offset.x(), ry - self.drag_offset.y())
            return True

        # --- Gérer les curseurs au survol ---
        else:
            main_view = self.label_view.visualizer.main_view
            if main_view and getattr(main_view, "text_anno_active", False):
                # Si survol d'un texte en mode texte, curseur SizeAll, sinon Cross
                hovering_text = False
                for text_obj in self.texts:
                    tsx, tsy = self.to_screen(text_obj["pos"].x(), text_obj["pos"].y(), img_rect)
                    font = QFont("Arial", text_obj["size"])
                    font.setBold(True)
                    fm = QFontMetrics(font)
                    tw = fm.horizontalAdvance(text_obj["text"])
                    th = fm.height()
                    text_rect = QRect(int(tsx - tw/2 - 4), int(tsy - th/2), tw + 8, th)
                    if text_rect.contains(local_pos):
                        hovering_text = True
                        break
                if hovering_text:
                    self.label_view.setCursor(Qt.CursorShape.SizeAllCursor)
                else:
                    self.label_view.setCursor(Qt.CursorShape.CrossCursor)
            elif main_view and getattr(main_view, "pen_active", False):
                self.label_view.setCursor(Qt.CursorShape.PointingHandCursor)

        return False

    def handle_mouse_release(self, local_pos: QPoint, img_rect: QRect) -> bool:
        """Gère le relâchement du bouton de la souris."""
        if self.active_stroke is not None:
            self.drawings.append(self.active_stroke)
            self.active_stroke = None
            return True
        elif self.interaction_mode == "moving_text":
            self.interaction_mode = None
            return True
        return False

    def delete_selected(self) -> bool:
        """Supprime l'annotation textuelle sélectionnée."""
        if self.selected_text is not None:
            if self.selected_text in self.texts:
                self.texts.remove(self.selected_text)
                self.selected_text = None
                return True
        return False

    def draw_annotations(self, painter: QPainter, img_rect: QRect):
        """Dessine l'ensemble des annotations sur l'image."""
        painter.save()

        # 1. Dessiner les tracés libres confirmés
        for stroke in self.drawings:
            self.draw_stroke(painter, img_rect, stroke)

        # 2. Dessiner le tracé libre actif
        if self.active_stroke is not None:
            self.draw_stroke(painter, img_rect, self.active_stroke)

        # 3. Dessiner les annotations de texte
        for text_obj in self.texts:
            self.draw_text_obj(painter, img_rect, text_obj)

        painter.restore()

    def draw_stroke(self, painter: QPainter, img_rect: QRect, stroke: dict):
        """Trace une ligne brisée."""
        if len(stroke["points"]) < 2:
            return
        
        pen = QPen(
            stroke["color"],
            stroke["width"],
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
            Qt.PenJoinStyle.RoundJoin
        )
        painter.setPen(pen)

        for i in range(len(stroke["points"]) - 1):
            p1 = stroke["points"][i]
            p2 = stroke["points"][i+1]
            x1, y1 = self.to_screen(p1.x(), p1.y(), img_rect)
            x2, y2 = self.to_screen(p2.x(), p2.y(), img_rect)
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

    def draw_text_obj(self, painter: QPainter, img_rect: QRect, text_obj: dict):
        """Dessine un texte d'annotation."""
        tsx, tsy = self.to_screen(text_obj["pos"].x(), text_obj["pos"].y(), img_rect)
        
        font = QFont("Arial", text_obj["size"])
        font.setBold(True)
        painter.setFont(font)
        
        fm = QFontMetrics(font)
        text_str = text_obj["text"]
        tw = fm.horizontalAdvance(text_str)
        th = fm.height()

        rect_bg = QRect(int(tsx - tw/2 - 4), int(tsy - th/2), tw + 8, th)
        
        # Dessiner le fond pour assurer la lisibilité
        painter.fillRect(rect_bg, QColor(0, 0, 0, 160))

        # Dessiner le texte
        painter.setPen(text_obj["color"])
        painter.drawText(rect_bg, Qt.AlignmentFlag.AlignCenter, text_str)

        # Dessiner une bordure bleue si sélectionné
        if text_obj["selected"]:
            pen_sel = QPen(QColor("#00a2ed"), 1, Qt.PenStyle.DashLine)
            painter.setPen(pen_sel)
            painter.drawRect(rect_bg)
