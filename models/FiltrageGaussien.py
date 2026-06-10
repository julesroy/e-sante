import cv2
import numpy as np
from scipy.ndimage import gaussian_filter
from .ImageConvertie import ImageConvertie


class FiltrageGaussien:
    """
    Classe pour appliquer un filtrage gaussien à une image.
    Exemple d'instanciation :
    FiltrageGaussien(4, testImageConvertie)
    """

    def __init__(self, sigma: float | int, imageNpArray: np.ndarray):
        """
        Initialise les paramètres pour le filtrage gaussien.
        :param sigma: Écart type pour la fonction gaussienne.
        :param imageNpArray: Matrice Numpy de l'image.
        """
        self._sigma = sigma
        self._imageNpArray = imageNpArray

    def filtrage(self):
        """
        Applique le filtrage gaussien à l'image spécifiée et sauvegarde le résultat.
        :return: Matrice de l'image filtrée en niveaux de gris (Numpy 2D array).
        """
        return gaussian_filter(self._imageNpArray, sigma=self._sigma)

    def afficher(self, imageFiltreeMatrice):
        """
        Affiche l'image filtrée.
        :param imageFiltreeMatrice: Matrice de l'image filtrée en niveaux de gris (Numpy 2D array).
        """
        cv2.imshow("Image Filtrée Gaussienne", imageFiltreeMatrice)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
