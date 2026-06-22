import numpy as np
import pydicom
import os


class Histogramme:
    """
    Classe pour calculer les statistiques et la distribution d'une image en niveaux de gris.
    """

    def __init__(self, image_array: np.ndarray, original_file_path: str | None = None):
        """
        Initialise avec le tableau numpy de l'image et le chemin du fichier d'origine.
        :param image_array: Matrice numpy de l'image (normalisée [0, 1]).
        :param original_file_path: Chemin vers le fichier d'origine (DICOM ou PNG/JPG).
        """
        self.image_array = image_array
        self.original_file_path = original_file_path
        self._calculate_stats()

    def _calculate_stats(self):
        # Toujours utiliser la plage théorique [0, 255] peu importe le type de fichier (PNG ou DCM)
        self.original_min = 0.0
        self.original_max = 255.0
        self.bits = 8
        self.is_dicom = False

        self.scaled_data = self.image_array * 255.0
        self.left_val = 0
        self.right_val = 255

        self.min_val = float(np.min(self.scaled_data))
        self.max_val = float(np.max(self.scaled_data))
        self.mean_val = float(np.mean(self.scaled_data))
        self.std_val = float(np.std(self.scaled_data))

    def obtenir_donnees_tracage(self):
        """
        Retourne les données aplaties et la plage pour le tracé de l'histogramme.
        :return: (données aplaties, (min_plage, max_plage))
        """
        return self.scaled_data.ravel(), (self.left_val, self.right_val)
