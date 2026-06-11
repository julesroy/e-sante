# ===== IMPORTS UNIQUEMENT POUR PYLANCE (jamais exécutés) =====
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from views.MainView import MainView
    from controllers.MainController import MainController


class RulerController:
    def __init__(self, main_controller: MainController):
        self.main_controller = main_controller
        self.image_before_pipette = None

    @property
    def view(self):
        return self.main_controller.view

    @property
    def error_controller(self):
        return self.main_controller.error_handler

    def handle_ruler_toggle(self, checked: bool):
        """Gère l'activation du mode règle depuis la LeftToolbar."""
        if self.view.current_pixmap is None:
            self.view.left_toolbar.btn_ruler.setChecked(False)
            return

        self.view.ruler_active = checked
        if checked:
            print("Mode Règle de mesure activé.")
            # Désactiver les autres modes
            if getattr(self.view, "angle_active", False):
                self.view.left_toolbar.btn_angle.setChecked(False)
                self.view.angle_active = False
            if getattr(self.view, "height_comp_active", False):
                self.view.left_toolbar.btn_height_comp.setChecked(False)
                self.view.height_comp_active = False
            if getattr(self.view, "circle_roi_active", False):
                self.view.left_toolbar.btn_circle_roi.setChecked(False)
                self.view.circle_roi_active = False
            if getattr(self.view, "square_roi_active", False):
                self.view.left_toolbar.btn_square_roi.setChecked(False)
                self.view.square_roi_active = False
            if getattr(self.view, "pipette_active", False):
                self.view.left_toolbar.btn_pipette.setChecked(False)
                self.handle_pipette_toggle(False)

            if hasattr(self.view.image_display, "ruler_overlay"):
                self.view.image_display.ruler_overlay.clear()
            if hasattr(self.view.image_display, "angle_overlay"):
                self.view.image_display.angle_overlay.clear()
            if hasattr(self.view.image_display, "height_comp_overlay"):
                self.view.image_display.height_comp_overlay.clear()
            if hasattr(self.view.image_display, "forms_overlay"):
                self.view.image_display.forms_overlay.clear()
        else:
            print("Mode Règle de mesure désactivé.")

        self.view.image_display.update()

    def handle_angle_toggle(self, checked: bool):
        """Gère l'activation du mode angle depuis la LeftToolbar."""
        if self.view.current_pixmap is None:
            self.view.left_toolbar.btn_angle.setChecked(False)
            return

        self.view.angle_active = checked
        if checked:
            print("Mode Angle de mesure activé.")
            # Désactiver les autres modes
            if getattr(self.view, "ruler_active", False):
                self.view.left_toolbar.btn_ruler.setChecked(False)
                self.view.ruler_active = False
            if getattr(self.view, "height_comp_active", False):
                self.view.left_toolbar.btn_height_comp.setChecked(False)
                self.view.height_comp_active = False
            if getattr(self.view, "circle_roi_active", False):
                self.view.left_toolbar.btn_circle_roi.setChecked(False)
                self.view.circle_roi_active = False
            if getattr(self.view, "square_roi_active", False):
                self.view.left_toolbar.btn_square_roi.setChecked(False)
                self.view.square_roi_active = False
            if getattr(self.view, "pipette_active", False):
                self.view.left_toolbar.btn_pipette.setChecked(False)
                self.handle_pipette_toggle(False)

            if hasattr(self.view.image_display, "angle_overlay"):
                self.view.image_display.angle_overlay.clear()
            if hasattr(self.view.image_display, "ruler_overlay"):
                self.view.image_display.ruler_overlay.clear()
            if hasattr(self.view.image_display, "height_comp_overlay"):
                self.view.image_display.height_comp_overlay.clear()
            if hasattr(self.view.image_display, "forms_overlay"):
                self.view.image_display.forms_overlay.clear()
        else:
            print("Mode Angle de mesure désactivé.")

        self.view.image_display.update()

    def handle_height_comp_toggle(self, checked: bool):
        """Gère l'activation du mode comparateur de hauteur depuis la LeftToolbar."""
        if self.view.current_pixmap is None:
            self.view.left_toolbar.btn_height_comp.setChecked(False)
            return

        self.view.height_comp_active = checked
        if checked:
            print("Mode Comparateur de hauteur activé.")
            # Désactiver les autres modes
            if getattr(self.view, "ruler_active", False):
                self.view.left_toolbar.btn_ruler.setChecked(False)
                self.view.ruler_active = False
            if getattr(self.view, "angle_active", False):
                self.view.left_toolbar.btn_angle.setChecked(False)
                self.view.angle_active = False
            if getattr(self.view, "circle_roi_active", False):
                self.view.left_toolbar.btn_circle_roi.setChecked(False)
                self.view.circle_roi_active = False
            if getattr(self.view, "square_roi_active", False):
                self.view.left_toolbar.btn_square_roi.setChecked(False)
                self.view.square_roi_active = False
            if getattr(self.view, "pipette_active", False):
                self.view.left_toolbar.btn_pipette.setChecked(False)
                self.handle_pipette_toggle(False)

            if hasattr(self.view.image_display, "height_comp_overlay"):
                self.view.image_display.height_comp_overlay.clear()
            if hasattr(self.view.image_display, "ruler_overlay"):
                self.view.image_display.ruler_overlay.clear()
            if hasattr(self.view.image_display, "angle_overlay"):
                self.view.image_display.angle_overlay.clear()
            if hasattr(self.view.image_display, "forms_overlay"):
                self.view.image_display.forms_overlay.clear()
        else:
            print("Mode Comparateur de hauteur désactivé.")

        self.view.image_display.update()

    def handle_circle_roi_toggle(self, checked: bool):
        """Gère l'activation du mode ROI Cercle depuis la LeftToolbar."""
        if self.view.current_pixmap is None:
            self.view.left_toolbar.btn_circle_roi.setChecked(False)
            return

        self.view.circle_roi_active = checked
        if checked:
            print("Mode ROI Cercle activé.")
            # Désactiver les autres modes
            if getattr(self.view, "ruler_active", False):
                self.view.left_toolbar.btn_ruler.setChecked(False)
                self.view.ruler_active = False
            if getattr(self.view, "angle_active", False):
                self.view.left_toolbar.btn_angle.setChecked(False)
                self.view.angle_active = False
            if getattr(self.view, "height_comp_active", False):
                self.view.left_toolbar.btn_height_comp.setChecked(False)
                self.view.height_comp_active = False
            if getattr(self.view, "square_roi_active", False):
                self.view.left_toolbar.btn_square_roi.setChecked(False)
                self.view.square_roi_active = False
            if getattr(self.view, "pipette_active", False):
                self.view.left_toolbar.btn_pipette.setChecked(False)
                self.handle_pipette_toggle(False)

            if hasattr(self.view.image_display, "forms_overlay"):
                self.view.image_display.forms_overlay.shape_type = "circle"
                self.view.image_display.forms_overlay.clear()
            if hasattr(self.view.image_display, "ruler_overlay"):
                self.view.image_display.ruler_overlay.clear()
            if hasattr(self.view.image_display, "angle_overlay"):
                self.view.image_display.angle_overlay.clear()
            if hasattr(self.view.image_display, "height_comp_overlay"):
                self.view.image_display.height_comp_overlay.clear()
        else:
            print("Mode ROI Cercle désactivé.")

        self.view.image_display.update()

    def handle_square_roi_toggle(self, checked: bool):
        """Gère l'activation du mode ROI Carré depuis la LeftToolbar."""
        if self.view.current_pixmap is None:
            self.view.left_toolbar.btn_square_roi.setChecked(False)
            return

        self.view.square_roi_active = checked
        if checked:
            print("Mode ROI Carré activé.")
            # Désactiver les autres modes
            if getattr(self.view, "ruler_active", False):
                self.view.left_toolbar.btn_ruler.setChecked(False)
                self.view.ruler_active = False
            if getattr(self.view, "angle_active", False):
                self.view.left_toolbar.btn_angle.setChecked(False)
                self.view.angle_active = False
            if getattr(self.view, "height_comp_active", False):
                self.view.left_toolbar.btn_height_comp.setChecked(False)
                self.view.height_comp_active = False
            if getattr(self.view, "circle_roi_active", False):
                self.view.left_toolbar.btn_circle_roi.setChecked(False)
                self.view.circle_roi_active = False
            if getattr(self.view, "pipette_active", False):
                self.view.left_toolbar.btn_pipette.setChecked(False)
                self.handle_pipette_toggle(False)

            if hasattr(self.view.image_display, "forms_overlay"):
                self.view.image_display.forms_overlay.shape_type = "square"
                self.view.image_display.forms_overlay.clear()
            if hasattr(self.view.image_display, "ruler_overlay"):
                self.view.image_display.ruler_overlay.clear()
            if hasattr(self.view.image_display, "angle_overlay"):
                self.view.image_display.angle_overlay.clear()
            if hasattr(self.view.image_display, "height_comp_overlay"):
                self.view.image_display.height_comp_overlay.clear()
        else:
            print("Mode ROI Carré désactivé.")

        self.view.image_display.update()

    def handle_pipette_toggle(self, checked: bool):
        """Gère l'activation du mode pipette depuis la LeftToolbar."""
        if self.view.current_pixmap is None:
            self.view.left_toolbar.btn_pipette.setChecked(False)
            return

        if checked:
            print("Mode Pipette de niveau de gris activé.")
            # Désactiver les autres modes
            if getattr(self.view, "ruler_active", False):
                self.view.left_toolbar.btn_ruler.setChecked(False)
                self.view.ruler_active = False
            if getattr(self.view, "angle_active", False):
                self.view.left_toolbar.btn_angle.setChecked(False)
                self.view.angle_active = False
            if getattr(self.view, "height_comp_active", False):
                self.view.left_toolbar.btn_height_comp.setChecked(False)
                self.view.height_comp_active = False
            if getattr(self.view, "circle_roi_active", False):
                self.view.left_toolbar.btn_circle_roi.setChecked(False)
                self.view.circle_roi_active = False
            if getattr(self.view, "square_roi_active", False):
                self.view.left_toolbar.btn_square_roi.setChecked(False)
                self.view.square_roi_active = False

            if hasattr(self.view.image_display, "ruler_overlay"):
                self.view.image_display.ruler_overlay.clear()
            if hasattr(self.view.image_display, "angle_overlay"):
                self.view.image_display.angle_overlay.clear()
            if hasattr(self.view.image_display, "height_comp_overlay"):
                self.view.image_display.height_comp_overlay.clear()
            if hasattr(self.view.image_display, "forms_overlay"):
                self.view.image_display.forms_overlay.clear()
                
            self.view.toggle_pipette_mode(True)
            self.image_before_pipette = self.main_controller._current_array.copy() if self.main_controller._current_array is not None else None
        else:
            print("Mode Pipette de niveau de gris désactivé.")
            self.view.toggle_pipette_mode(False)
            if self.image_before_pipette is not None:
                self.main_controller._current_array = self.image_before_pipette
                self.main_controller._display_numpy_array(self.image_before_pipette)
                self.image_before_pipette = None

        self.view.image_display.update()

    def deactivate_pipette(self):
        """Désactive proprement la pipette sans restaurer l'image."""
        self.image_before_pipette = None
        self.view.left_toolbar.btn_pipette.setChecked(False)
        self.view.toggle_pipette_mode(False)

    def handle_area_calculation(self):
        """Calcule et affiche l'aire des régions de la segmentation Watershed."""
        try:
            model = self.main_controller.model
            # Vérifier si le watershed a été appliqué avant
            if not hasattr(model, "watershed_labels") or model.watershed_labels is None:
                self.error_controller.show_error("Erreur", "Veuillez appliquer la segmentation Watershed avant de calculer les aires.")
                return

            import numpy as np
            import cv2
            labels = model.watershed_labels
            unique_labels = np.unique(labels)
            unique_labels = unique_labels[unique_labels != 0]

            if len(unique_labels) == 0:
                self.error_controller.show_error("Erreur", "Aucune zone d'intérêt détectée par le Watershed.")
                return

            # Régénérer l'image couleur du watershed pour récupérer les couleurs exactes
            image_affichage = cv2.normalize(labels, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            image_couleur = cv2.applyColorMap(image_affichage, cv2.COLORMAP_JET)

            html_lines = ["<html><body><p style='margin-top: 0px; margin-bottom: 6px; font-weight: bold;'>Aires du Watershed :</p>"]
            html_lines.append("<table border='0' cellspacing='0' cellpadding='2'>")
            for label in unique_labels:
                # Récupérer la couleur de ce label
                coords = np.argwhere(labels == label)
                if len(coords) > 0:
                    y, x = coords[0]
                    b, g, r = image_couleur[y, x]
                    color_hex = f"#{r:02x}{g:02x}{b:02x}"
                else:
                    color_hex = "#ffffff"

                area_px = np.sum(labels == label)
                # Utilisation d'un tableau HTML (pleinement supporté par le moteur de texte riche de Qt)
                html_lines.append(
                    f"<tr>"
                    f"<td bgcolor='{color_hex}' width='12' height='12' style='border: 1px solid #555555;'>&nbsp;</td>"
                    f"<td style='font-size: 11px; color: #e0e0e0; vertical-align: middle;'>&nbsp;&nbsp;{area_px} px²</td>"
                    f"</tr>"
                )
            html_lines.append("</table></body></html>")
            text = "".join(html_lines)
            
            # Afficher dans la zone de même largeur
            self.view.display_watershed_areas(text)

        except Exception as e:
            self.error_controller.handle_exception(e)
