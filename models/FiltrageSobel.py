import cv2
import numpy as np
from scipy.ndimage import sobel
from ImageConvertie import ImageConvertie


class FiltrageSobel:
    """
    Classe pour appliquer un filtre de sobel à une image.
    Exemple d'instanciation :
    test = testMatrice = FiltrageSobel(image)
    """

    def __init__(self, imageNpArray: np.ndarray):
        """
        Initialise les paramètres pour le filtrage sobel.
        :param imageNpArray: Matrice Numpy de l'image.
        """
        self._imageNpArray = imageNpArray

    def filtrage(self) -> np.ndarray:
        """
        Calcule les gradients de Sobel en X et Y, puis les combine.
        :return: Matrice du gradient de Sobel normalisée en uint8 (0-255).
        """
        gx = sobel(self._imageNpArray, axis=1)
        gy = sobel(self._imageNpArray, axis=0)
        magnitude = np.hypot(gx, gy)

        # clip percentile : ignore les 1% de valeurs extrêmes
        p_low  = np.percentile(magnitude, 1)
        p_high = np.percentile(magnitude, 99)
        magnitude = np.clip(magnitude, p_low, p_high)
        magnitude = (magnitude - p_low) / (p_high - p_low)

        return magnitude

    def afficher(self, imageFiltreeMatrice):
        """
        Affiche l'image filtrée.
        :param imageFiltreeMatrice: Matrice de l'image filtrée en niveaux de gris (Numpy 2D array).
        """
        cv2.imshow('Image Filtrée', imageFiltreeMatrice)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

# tests
# testImageConvertie = ImageConvertie("COVID-1024.png").convertirEnNumpyArray()
# testImageConvertie = ImageConvertie("dcm1.dcm").convertirEnNumpyArray()
# testMatrice = FiltrageSobel(testImageConvertie)
# testMatriceFiltree = testMatrice.filtrage()
# print(testMatriceFiltree)
# print(type(testMatriceFiltree))  # type de la matrice
# print(testMatriceFiltree.ndim)  # dimension de la matrice
# print(testMatriceFiltree.shape)  # dimensions de la matrice (hauteur, largeur)
# testMatrice.afficher(testMatriceFiltree)