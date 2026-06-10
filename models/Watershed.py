import numpy as np
import scipy.ndimage as ndimage
import matplotlib.pyplot as plt
from skimage.segmentation import watershed
from skimage.feature import peak_local_max


class SegmentationWatershed:
    """
    Classe pour séparer les régions qui se touchent (ex: poumon gauche et droit)
    en utilisant l'algorithme géomorphologique du Watershed.
    """

    def __init__(self, min_distance_marqueurs: int = 20):
        """
        :param min_distance_marqueurs: Distance minimale en pixels séparant deux marqueurs (poumons).
        """
        self._min_distance = min_distance_marqueurs

    def segmenter(self, masque_binaire: np.ndarray) -> np.ndarray:
        """
        Calcule la carte des distances, extrait les marqueurs et applique le Watershed.
        :param masque_binaire: Matrice 2D (0 ou 255) nettoyée par morphologie.
        :return: Matrice d'étiquettes (labels) où chaque région a son propre numéro (1, 2, etc.)
        """
        if masque_binaire is None:
            raise ValueError("Le masque binaire fourni est vide.")

        # S'assurer d'avoir un masque booléen pur (True pour les poumons, False pour le fond)
        masque_bool = masque_binaire > 0

        # 1. Calcul de la transformée en distance (Distance Transform)
        # Chaque pixel blanc reçoit une valeur égale à sa distance au pixel noir le plus proche
        carte_distances = ndimage.distance_transform_edt(masque_bool)

        # 2. Extraction des maxima locaux (Les centres des poumons / Les sources d'inondation)
        # On extrait les coordonnées des pics de distance
        coordonnees_pics = peak_local_max(
            carte_distances, 
            min_distance=self._min_distance, 
            labels=masque_bool
        )
        
        # Création de la matrice des marqueurs unique pour l'inondation
        masque_marqueurs = np.zeros(carte_distances.shape, dtype=int)
        for idx, (y, x) in enumerate(coordonnees_pics):
            masque_marqueurs[y, x] = idx + 1  # Le poumon 1 aura le tag 1, le poumon 2 le tag 2, etc.

        # 3. Application du Watershed (Ligne de partage des eaux)
        # On inverse la carte des distances car le watershed cherche à remplir des "vallées" (minima)
        img_relief = -carte_distances
        
        # Inondation à partir des marqueurs en restant confiné dans le masque des poumons
        labels_segmentes = watershed(img_relief, masque_marqueurs, mask=masque_bool)

        return labels_segmentes