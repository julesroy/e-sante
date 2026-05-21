import cv2
import numpy as np

class FiltrageGaussien:
    """
    Classe pour appliquer un filtrage gaussien à une image.
    Exemple d'instanciation :
    test = FiltrageGaussien((9, 9), 0, 'COVID-1024.png', 'FiltrageGaussien.png')
    """

    def __init__(self, kernel:tuple, sigma:int, imagePath:str):
        """
        Initialise les paramètres pour le filtrage gaussien.
        :param kernel: Tuple représentant la taille du noyau de convolution (ex: (9, 9)).
        :param sigma: Écart type pour la fonction gaussienne.
        :param imagePath: Chemin de l'image d'entrée.
        """
        self._kernel = kernel
        self._sigma = sigma
        self._imagePath = imagePath

    def filtrage(self):
        """
        Applique le filtrage gaussien à l'image spécifiée et sauvegarde le résultat.
        :return: Matrice de l'image filtrée en niveaux de gris (Numpy 2D array).
        """
        image = cv2.imread(self._imagePath, cv2.IMREAD_GRAYSCALE) # lit l'image en niveaux de gris (utile pour numpy)
        imageFloueMatrice = cv2.GaussianBlur(image, self._kernel, self._sigma) # applique le filtrage gaussien
        # cv2.imwrite(self._imagePath, imageFloueMatrice) # sauvegarde l'image filtrée

        return imageFloueMatrice

# matrice = FiltrageGaussien((5, 5), 0, 'COVID-1024.png')
# matriceFiltree = matrice.filtrage()
# print(matriceFiltree)
# print(type(matriceFiltree)) # type de la matrice
# print(matriceFiltree.ndim) # dimension de la matrice
# print(matriceFiltree.shape) # dimensions de la matrice (hauteur, largeur)