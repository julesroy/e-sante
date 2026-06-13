# ===== IMPORTS PYTHON STANDARD =====
from __future__ import annotations
import os
import tempfile

# ===== IMPORTS UNIQUEMENT POUR PYLANCE (jamais exécutés) =====
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np
    from views.MainView import MainView
    from controllers.MainController import MainController

# ===== IMPORTS DES MODÈLES =====
from models.ImageConvertie import ImageConvertie

# ===== IMPORTS PYQT6 =====
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtCore import QRect, Qt

# ===== IMPORTS BDD =====
from database.connection import is_online
from database.crud.images import (
    sauvegarder_image,
    get_images_patient,
    supprimer_image,
)

# ===== IMPORTS API SERVEUR =====
from server.api_client import upload_image, download_image, delete_image

# Message réutilisé dans tous les guards hors-ligne
_MSG_OFFLINE = "Cette fonctionnalité nécessite une connexion Internet"


class ImageController:
    def __init__(self, main_controller: MainController):
        self.main_controller = main_controller

    @property
    def view(self):
        return self.main_controller.view

    @property
    def error_handler(self):
        return self.main_controller.error_handler

    @property
    def _current_patient_id(self):
        return self.main_controller._current_patient_id

    @_current_patient_id.setter
    def _current_patient_id(self, value):
        self.main_controller._current_patient_id = value

    # ---------------------------------------------------------------
    # UPLOAD + SAUVEGARDE EN BDD
    # ---------------------------------------------------------------
    def handle_upload_et_sauvegarder(self, modalite: str | None = None) -> None:
        """
        Ouvre l'explorateur, affiche l'image dans la View,
        l'envoie sur le serveur via l'API
        ET sauvegarde le chemin serveur en BDD lié au patient courant.
        """
        # Guard hors-ligne
        if not is_online():
            self.error_handler.show_error("Mode hors-ligne", _MSG_OFFLINE)
            return None

        try:
            # Vérifie qu'un patient est bien sélectionné avant d'uploader
            if self._current_patient_id is None:
                self.error_handler.show_error("Aucun patient sélectionné", "Sélectionnez ou créez un patient avant d'importer une image.")
                return

            # Ouverture de l'explorateur de fichiers natif
            file_path, _ = QFileDialog.getOpenFileName(
                self.view,
                "Sélectionner une radiographie",
                "",
                "Images (*.png *.jpg *.jpeg *.dcm)",
            )

            if not file_path:
                return  # L'utilisateur a annulé

            # Enregistre le chemin du fichier chargé
            self.main_controller._last_file_path = file_path

            # Conversion en numpy array normalisé [0,1] pour les traitements ultérieurs
            self.main_controller._current_array = ImageConvertie(file_path).convertirEnNumpyArray()

            # Pour les DICOM, afficher via numpy array plutôt que QPixmap directement
            if file_path.lower().endswith(".dcm"):
                self.main_controller._display_numpy_array(self.main_controller._current_array)
            else:
                # Pour PNG/JPG, afficher directement et mémoriser
                self.view.display_medical_image(file_path)

            # Mémoriser le pixmap d'origine chargé depuis le fichier
            if getattr(self.view, "current_pixmap", None) is not None:
                self.main_controller._original_pixmap = self.view.current_pixmap.copy()

            nom_fichier = os.path.basename(file_path)

            # Envoi du fichier sur le serveur via l'API
            # -> retourne le chemin distant ex: /home/ubuntu/esante/images/radio.png
            chemin_serveur = upload_image(file_path, self._current_patient_id)

            if chemin_serveur is None:
                self.error_handler.show_error("Erreur serveur", "Impossible d'envoyer l'image au serveur.")
                return

            # Garde-fou parce que sauvegarder_image() attend un int et on envoie un int | None
            if self._current_patient_id is None:
                return

            # Sauvegarde en BDD avec le chemin SERVEUR (pas le chemin local)
            image_id = sauvegarder_image(
                patient_id=self._current_patient_id,
                nom_fichier=nom_fichier,
                chemin=chemin_serveur,
                modalite=modalite,
            )
            print(f"[ImageController] Image '{nom_fichier}' envoyée sur serveur et sauvegardée -> id={image_id}")

        except Exception as e:
            self.error_handler.handle_exception(e)

    # ---------------------------------------------------------------
    # CHARGER LES IMAGES D'UN PATIENT
    # ---------------------------------------------------------------
    def handle_charger_images_patient(self, patient_id: int) -> list:
        """
        Récupère toutes les images d'un patient depuis la BDD.
        Retourne une liste de tuples :
        (id, nom_fichier, chemin, modalite, created_at)
        Appelé quand on sélectionne un patient dans la liste.
        Retourne [] si hors-ligne ou erreur.
        """
        # Guard hors-ligne — silencieux (appelé automatiquement au chargement)
        if not is_online():
            return []

        try:
            images: list = get_images_patient(patient_id) or []
            print(f"[ImageController] {len(images)} image(s) trouvée(s) pour patient id={patient_id}")
            return images

        except Exception as e:
            self.error_handler.handle_exception(e)
            return []

    # ---------------------------------------------------------------
    # OUVRIR UNE IMAGE DEPUIS LA BDD (chemin serveur -> téléchargement API)
    # ---------------------------------------------------------------
    def handle_ouvrir_image_bdd(self, chemin: str) -> None:
        """
        Télécharge l'image depuis le serveur via l'API dans un fichier temporaire
        et l'affiche dans la View.
        Le chemin en BDD est un chemin serveur (ex: /home/ubuntu/esante/images/radio.png).
        """
        try:
            # Extension du fichier pour que Qt l'affiche correctement
            extension = os.path.splitext(chemin)[1] or ".png"

            # Téléchargement dans un fichier temporaire local
            # delete=False pour que le fichier survive après le with (Qt en a besoin)
            with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as tmp:
                tmp_path = tmp.name

            ok = download_image(chemin, tmp_path)

            if not ok:
                self.error_handler.show_error("Erreur serveur", f"Impossible de télécharger l'image depuis le serveur.")
                return

            # Enregistre le chemin du fichier chargé
            self.main_controller._last_file_path = tmp_path

            # Conversion en numpy array normalisé [0,1] pour les traitements ultérieurs
            self.main_controller._current_array = ImageConvertie(tmp_path).convertirEnNumpyArray()

            # Pour les DICOM, afficher via numpy array plutôt que QPixmap directement
            if tmp_path.lower().endswith(".dcm"):
                self.main_controller._display_numpy_array(self.main_controller._current_array)
            else:
                # Pour PNG/JPG, afficher directement
                self.view.display_medical_image(tmp_path)

            # Mémoriser le pixmap d'origine chargé depuis le fichier
            if getattr(self.view, "current_pixmap", None) is not None:
                self.main_controller._original_pixmap = self.view.current_pixmap.copy()

            # RESET le slider de contraste à 1 pour repartir proprement
            if self.view.contrast_slider is not None:
                self.view.contrast_slider.setValue(1)

            # Désactive les modes actifs pour éviter les états parasites
            if self.view.contrast_slider_active:
                self.view.toggle_contrast_slider_mode(False)
                self.view.left_toolbar.btn_contrast_slider.setChecked(False)

            print(f"[ImageController] Image ouverte depuis serveur : {chemin}")

        except Exception as e:
            self.error_handler.handle_exception(e)

    # ---------------------------------------------------------------
    # SUPPRIMER UNE IMAGE
    # ---------------------------------------------------------------
    def handle_supprimer_image(self, image_id: int, chemin_serveur: str | None = None) -> bool:
        """
        Supprime une image de la BDD et du disque serveur via l'API.
        Retourne True si OK, False si hors-ligne / erreur.
        """
        # Guard hors-ligne
        if not is_online():
            self.error_handler.show_error("Mode hors-ligne", _MSG_OFFLINE)
            return False

        try:
            # Suppression du fichier sur le serveur si le chemin est fourni
            if chemin_serveur:
                delete_image(chemin_serveur)

            supprimer_image(image_id)
            print(f"[ImageController] Image id={image_id} supprimée de la BDD et du serveur")
            return True

        except Exception as e:
            self.error_handler.handle_exception(e)
            return False

    # ---------------------------------------------------------------
    # EXPORTER L'IMAGE AVEC ANNOTATIONS
    # ---------------------------------------------------------------
    def handle_export_image(self) -> None:
        """
        Exporte l'image affichée à l'écran avec ses annotations, règles et formes superposées.
        Enregistre le résultat sous forme d'image (PNG, JPEG) ou document PDF.
        """
        try:
            # Vérifier qu'une image est bien chargée et affichée
            if self.main_controller._original_pixmap is None or self.view.current_pixmap is None:
                self.error_handler.show_error(
                    "Aucune image chargée", 
                    "Il n'y a aucune image à exporter."
                )
                return

            pixmap_displayed = self.view.image_display.pixmap()
            if not pixmap_displayed or pixmap_displayed.isNull():
                self.error_handler.show_error(
                    "Aucune image affichée", 
                    "Il n'y a pas d'image affichée à exporter."
                )
                return

            # Nom par défaut suggéré
            nom_defaut = "export_image.png"
            last_path = self.main_controller._last_file_path
            if last_path and last_path != "from_controller":
                base_name = os.path.splitext(os.path.basename(last_path))[0]
                nom_defaut = f"{base_name}_export.png"

            # Ouvre le dialogue de sauvegarde avec PDF inclus
            file_path, _ = QFileDialog.getSaveFileName(
                self.view,
                "Exporter l'image avec annotations",
                nom_defaut,
                "Images PNG (*.png);;Images JPEG (*.jpg *.jpeg);;Documents PDF (*.pdf);;Tous les fichiers (*)"
            )

            if not file_path:
                return  # Annulé par l'utilisateur

            # Capture le widget d'affichage (QLabel)
            full_pixmap = self.view.image_display.grab()

            # Calcul des marges pour ne rogner que la zone de l'image
            margin_x = (self.view.image_display.width() - pixmap_displayed.width()) // 2
            margin_y = (self.view.image_display.height() - pixmap_displayed.height()) // 2
            img_rect = QRect(margin_x, margin_y, pixmap_displayed.width(), pixmap_displayed.height())

            # Rogner pour garder l'image exacte
            cropped_pixmap = full_pixmap.copy(img_rect)

            success = False
            # Enregistrement
            if file_path.lower().endswith(".pdf"):
                try:
                    from PyQt6.QtGui import QPdfWriter, QPainter, QPageSize, QPageLayout
                    
                    writer = QPdfWriter(file_path)
                    writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
                    
                    if cropped_pixmap.width() > cropped_pixmap.height():
                        writer.setPageOrientation(QPageLayout.Orientation.Landscape)
                    else:
                        writer.setPageOrientation(QPageLayout.Orientation.Portrait)
                        
                    painter = QPainter(writer)
                    w = writer.width()
                    h = writer.height()
                    scaled = cropped_pixmap.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    x = (w - scaled.width()) // 2
                    y = (h - scaled.height()) // 2
                    painter.drawPixmap(x, y, scaled)
                    painter.end()
                    success = True
                except Exception as pdf_error:
                    print(f"Erreur lors de la génération du PDF : {pdf_error}")
                    success = False
            else:
                success = cropped_pixmap.save(file_path)

            if success:
                print(f"[ImageController] Image exportée avec succès : {file_path}")
                # Demander si l'utilisateur veut aussi l'ajouter au dossier patient
                from PyQt6.QtWidgets import QMessageBox
                reply = QMessageBox.question(
                    self.view,
                    "Enregistrer dans le dossier patient",
                    "L'image a été exportée localement.\nVoulez-vous également l'enregistrer dans le dossier médical de ce patient ?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.handle_save_to_patient_record(cropped_pixmap)
            else:
                self.error_handler.show_error(
                    "Erreur d'exportation", 
                    "Impossible d'enregistrer l'image ou le document PDF. Vérifiez les permissions."
                )

        except Exception as e:
            self.error_handler.handle_exception(e)

    # ---------------------------------------------------------------
    # ENREGISTRER DANS LE DOSSIER DU PATIENT
    # ---------------------------------------------------------------
    def handle_save_to_patient_record(self, cropped_pixmap=None) -> None:
        """
        Enregistre l'image annotée courante dans la base de données et sur le serveur
        pour le patient actuellement sélectionné.
        """
        # Guard hors-ligne
        if not is_online():
            self.error_handler.show_error("Mode hors-ligne", "Cette fonctionnalité nécessite une connexion Internet.")
            return

        try:
            # Vérifier qu'un patient est sélectionné
            if self._current_patient_id is None:
                self.error_handler.show_error(
                    "Aucun patient sélectionné", 
                    "Veuillez sélectionner un patient avant d'enregistrer l'image dans son dossier."
                )
                return

            # Si cropped_pixmap n'est pas fourni, on le capture à la volée
            if cropped_pixmap is None:
                if self.main_controller._original_pixmap is None or self.view.current_pixmap is None:
                    self.error_handler.show_error(
                        "Aucune image chargée", 
                        "Il n'y a aucune image à enregistrer."
                    )
                    return

                pixmap_displayed = self.view.image_display.pixmap()
                if not pixmap_displayed or pixmap_displayed.isNull():
                    self.error_handler.show_error(
                        "Aucune image affichée", 
                        "Il n'y a pas d'image affichée à enregistrer."
                    )
                    return

                # Capture le widget d'affichage (QLabel)
                full_pixmap = self.view.image_display.grab()

                # Calcul des marges pour ne rogner que la zone de l'image
                margin_x = (self.view.image_display.width() - pixmap_displayed.width()) // 2
                margin_y = (self.view.image_display.height() - pixmap_displayed.height()) // 2
                img_rect = QRect(margin_x, margin_y, pixmap_displayed.width(), pixmap_displayed.height())

                # Rogner pour garder l'image exacte
                cropped_pixmap = full_pixmap.copy(img_rect)

            # Demander le nom du fichier à l'utilisateur (ou générer un nom automatique)
            last_path = self.main_controller._last_file_path
            nom_defaut = "radio_annotee.png"
            if last_path and last_path != "from_controller":
                base_name = os.path.splitext(os.path.basename(last_path))[0]
                nom_defaut = f"{base_name}_annotee.png"

            # Boîte de dialogue simple pour saisir le nom de l'image dans le dossier
            from PyQt6.QtWidgets import QInputDialog
            nom_fichier, ok = QInputDialog.getText(
                self.view,
                "Enregistrer dans le dossier",
                "Nom de la radiographie annotée :",
                text=nom_defaut
            )
            if not ok or not nom_fichier.strip():
                return  # Annulé

            # S'assurer de l'extension .png par défaut si aucune extension d'image valide n'est saisie
            _, ext = os.path.splitext(nom_fichier)
            if not ext.lower() in [".png", ".jpg", ".jpeg"]:
                nom_fichier += ".png"

            # Sauvegarde temporaire locale du pixmap pour l'upload
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp_path = tmp.name

            cropped_pixmap.save(tmp_path)

            # Upload et sauvegarde BDD
            chemin_serveur = upload_image(tmp_path, self._current_patient_id)

            # Supprimer le fichier temporaire local
            try:
                os.unlink(tmp_path)
            except:
                pass

            if chemin_serveur is None:
                self.error_handler.show_error("Erreur serveur", "Impossible d'envoyer l'image au serveur.")
                return

            image_id = sauvegarder_image(
                patient_id=self._current_patient_id,
                nom_fichier=nom_fichier,
                chemin=chemin_serveur,
                modalite="ANNOTATED"
            )

            print(f"[ImageController] Image annotée '{nom_fichier}' enregistrée en BDD (id={image_id})")
            
            # Message de succès
            self.error_handler.show_info(
                "Enregistrement réussi", 
                f"L'image annotée '{nom_fichier}' a été ajoutée avec succès au dossier du patient."
            )

            # Rafraîchir la liste des images du patient dans la vue
            p_manager = self.view.left_toolbar.patient_manager
            images = self.handle_charger_images_patient(self._current_patient_id)
            p_manager.refresh_images(images)

        except Exception as e:
            self.error_handler.handle_exception(e)