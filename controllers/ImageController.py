# ===== IMPORTS PYTHON STANDARD =====
from __future__ import annotations
import os

# ===== IMPORTS UNIQUEMENT POUR PYLANCE (jamais exécutés) =====
from typing import TYPE_CHECKING
from collections.abc import Callable
if TYPE_CHECKING:
    import numpy as np
    from views.MainView import MainView
    from controllers.ErrorController import ErrorController

# ===== IMPORTS PYQT6 =====
from PyQt6.QtWidgets import QFileDialog

# ===== IMPORTS BDD =====
from database.connection import is_online
from database.crud import (
    sauvegarder_image,
    get_images_patient,
    supprimer_image,
)

# Message réutilisé dans tous les guards hors-ligne
_MSG_OFFLINE = "Cette fonctionnalité nécessite une connexion Internet"

class ImageController:
    # Attributs déclarés pour Pylance (définis dans MainController)
    view: MainView
    error_handler: ErrorController
    _current_patient_id: int | None

    # ---------------------------------------------------------------
    # UPLOAD + SAUVEGARDE EN BDD
    # ---------------------------------------------------------------
    def handle_upload_et_sauvegarder(self, modalite: str | None = None) -> None:
        """
        Ouvre l'explorateur, affiche l'image dans la View
        ET la sauvegarde en BDD liée au patient courant.

        Remplace handle_upload() de UploadController quand un patient
        est sélectionné dans l'UI.
        """
        # Guard hors-ligne
        if not is_online():
            self.error_handler.show_error("Mode hors-ligne", _MSG_OFFLINE)
            return None

        try:
            # Vérifie qu'un patient est bien sélectionné avant d'uploader
            if self._current_patient_id is None:
                self.error_handler.show_error(
                    "Aucun patient sélectionné",
                    "Sélectionnez ou créez un patient avant d'importer une image."
                )
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

            # Affichage dans la View (réutilise la logique existante)
            self.view.display_medical_image(file_path)

            # Sauvegarde en BDD
            nom_fichier = os.path.basename(file_path)

            # Garde-fou parce que sauvegarder_image() attend un int et on envoie un int | None
            if self._current_patient_id is None:
                return

            image_id = sauvegarder_image(
                patient_id=self._current_patient_id,
                nom_fichier=nom_fichier,
                chemin=file_path,
                modalite=modalite,
            )
            print(f"[ImageController] Image '{nom_fichier}' sauvegardée → id={image_id}")

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
    # OUVRIR UNE IMAGE DEPUIS LA BDD (chemin disque)
    # ---------------------------------------------------------------
    def handle_ouvrir_image_bdd(self, chemin: str) -> None:
        """
        Affiche une image déjà enregistrée en BDD à partir de son chemin disque.
        Appelé depuis la liste des images d'un patient (double-clic ou bouton).
        """
        # Pas de guard hors-ligne ici — ouvrir un fichier local ne nécessite pas la BDD, seulement le chemin disque
        try:
            if not os.path.exists(chemin):
                self.error_handler.show_error(
                    "Fichier introuvable",
                    f"Le fichier n'existe plus à l'emplacement :\n{chemin}"
                )
                return

            self.view.display_medical_image(chemin)
            print(f"[ImageController] Image ouverte depuis BDD : {chemin}")

        except Exception as e:
            self.error_handler.handle_exception(e)

    # ---------------------------------------------------------------
    # SUPPRIMER UNE IMAGE
    # ---------------------------------------------------------------
    def handle_supprimer_image(self, image_id: int) -> bool:
        """
        Supprime une image de la BDD (pas du disque).
        Retourne True si OK, False si hors-ligne / erreur.
        """
        # Guard hors-ligne
        if not is_online():
            self.error_handler.show_error("Mode hors-ligne", _MSG_OFFLINE)
            return False

        try:
            supprimer_image(image_id)
            print(f"[ImageController] Image id={image_id} supprimée de la BDD")
            return True

        except Exception as e:
            self.error_handler.handle_exception(e)
            return False