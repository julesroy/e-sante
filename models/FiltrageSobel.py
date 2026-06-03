import cv2
import numpy as np
from ImageConvertie import ImageConvertie


class FiltrageSobel:
    """
    Classe pour appliquer un filtre de sobel à une image.
    Exemple d'instanciation :
    test = testMatrice = FiltrageSobel(3, image)
    """

    def __init__(self, ksize: int, imageNpArray: np.ndarray):
        """
        Initialise les paramètres pour le filtrage sobel.
        :param ksize: Taille du noyau de convolution (ex: 9).
        :param imageNpArray: Matrice Numpy de l'image.
        """
        self._ksize = ksize
        self._imageNpArray = imageNpArray

    def filtrage(self) -> np.ndarray:
        """
        Calcule les gradients de Sobel en X et Y, puis les combine.
        :return: Matrice du gradient de Sobel normalisée en uint8 (0-255).
        """
        # on s'assure que l'image est en uint8
        if self._imageNpArray.dtype != np.uint8:
            if self._imageNpArray.max() <= 1.0:
                img_8bit = (self._imageNpArray * 255).astype(np.uint8)
            else:
                img_8bit = self._imageNpArray.astype(np.uint8)
        else:
            img_8bit = self._imageNpArray

        # on calcule le gradient horizontal (X)
        sobelx = cv2.Sobel(img_8bit, cv2.CV_64F, 1, 0, ksize=self._ksize)
        
        # on calcule le gradient vertical (Y)
        sobely = cv2.Sobel(img_8bit, cv2.CV_64F, 0, 1, ksize=self._ksize)

        # on combine les deux (Magnitude du gradient)
        # on prend la valeur absolue pour capturer les transitions du noir vers le blanc ET du blanc vers le noir
        sobel_combine = np.sqrt(sobelx**2 + sobely**2)
        
        # on normalise la matrice
        sobel_normalise = cv2.normalize(sobel_combine, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)

        return sobel_normalise

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
# testMatrice = FiltrageSobel(3, testImageConvertie)
# testMatriceFiltree = testMatrice.filtrage()
# print(testMatriceFiltree)
# print(type(testMatriceFiltree))  # type de la matrice
# print(testMatriceFiltree.ndim)  # dimension de la matrice
# print(testMatriceFiltree.shape)  # dimensions de la matrice (hauteur, largeur)
# testMatrice.afficher(testMatriceFiltree)