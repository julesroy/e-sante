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

# ===== IMPORTS PYQT6 =====
from PyQt6.QtWidgets import QFileDialog

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

            # Affichage immédiat depuis le PC local (pas besoin d'attendre le serveur)
            self.view.display_medical_image(file_path)

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

            self.view.display_medical_image(tmp_path)

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