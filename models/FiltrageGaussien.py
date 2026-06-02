import cv2
import numpy as np
from ImageConvertie import ImageConvertie


class FiltrageGaussien:
    """
    Classe pour appliquer un filtrage gaussien à une image.
    Exemple d'instanciation :
    FiltrageGaussien((5, 5), 0, testImageConvertie)
    """

    def __init__(self, kernel: tuple, sigma: int, imageNpArray: np.ndarray):
        """
        Initialise les paramètres pour le filtrage gaussien.
        :param kernel: Tuple représentant la taille du noyau de convolution (ex: (9, 9)).
        :param sigma: Écart type pour la fonction gaussienne.
        :param imageNpArray: Matrice Numpy de l'image.
        """
        self._kernel = kernel
        self._sigma = sigma
        self._imageNpArray = imageNpArray

    def filtrage(self):
        """
        Applique le filtrage gaussien à l'image spécifiée et sauvegarde le résultat.
        :return: Matrice de l'image filtrée en niveaux de gris (Numpy 2D array).
        """
        image = self._imageNpArray  # utilise la matrice Numpy de l'image
        imageFloueMatrice = cv2.GaussianBlur(image, self._kernel, self._sigma)  # applique le filtrage gaussien

        return imageFloueMatrice


# tests
# testImageConvertie = ImageConvertie("COVID-1024.png").convertirEnNumpyArray()
# testMatrice = FiltrageGaussien((5, 5), 0, testImageConvertie)
# testMatriceFiltree = testMatrice.filtrage()
# print(testMatriceFiltree)
# print(type(testMatriceFiltree))  # type de la matrice
# print(testMatriceFiltree.ndim)  # dimension de la matrice
# print(testMatriceFiltree.shape)  # dimensions de la matrice (hauteur, largeur)

# assert isinstance(testMatriceFiltree, np.ndarray), "La matrice filtrée doit être un Numpy array."
# assert testMatriceFiltree.ndim == 2, "La matrice filtrée doit être en 2D (niveaux de gris)."
