import cv2
import numpy as np
from ImageConvertie import ImageConvertie
from TFD2D import TFD2D

class CLAHE:
    """
    Classe pour appliquer l'égalisation d'histogramme adaptative (CLAHE).
    L'image d'entrée doit être une matrice Numpy 2D (niveaux de gris).
    """

    def __init__(self, limitationContraste: float, tailleGrilleLocale: tuple):
        """
        Initialise les paramètres du CLAHE.
        :param limitationContraste: Seuil de limitation du contraste pour éviter d'amplifier le bruit.
        :param tailleGrilleLocale: Taille de la grille locale (nb_tuiles_hauteur, nb_tuiles_largeur).
        """
        self._limitationContraste = limitationContraste
        self._tailleGrilleLocale = tailleGrilleLocale

    def appliquer(self, imageNpArray: np.ndarray) -> np.ndarray:
        """
        Applique le traitement CLAHE sur la matrice passée en paramètre.
        :param imageNpArray: Matrice Numpy 2D de l'image d'origine.
        :return: Matrice Numpy 2D après égalisation locale du contraste.
        """
        if imageNpArray is None:
            raise ValueError("La matrice d'image fournie est vide.")

        # openCV a besoin d'une matrice en 8-bit (0-255) de type uint8 pour le CLAHE
        if imageNpArray.dtype != np.uint8:
            # si elle est entre 0 et 1, on multiplie par 255
            if imageNpArray.max() <= 1.0:
                img_8bit = (imageNpArray * 255).astype(np.uint8)
            # sinon on convertit simplement en uint8
            else:
                img_8bit = imageNpArray.astype(np.uint8)
        else:
            img_8bit = imageNpArray

        # on crée l'objet CLAHE avec les paramètres spécifiés
        clahe_obj = cv2.createCLAHE(
            clipLimit=self._limitationContraste, 
            tileGridSize=self._tailleGrilleLocale
        )

        matrice_clahe = clahe_obj.apply(img_8bit) # on applique le CLAHE à l'image en niveaux de gris

        return matrice_clahe
    

# tests
testCLAHEImage = ImageConvertie("COVID-1024.png").convertirEnNumpyArray()

# on applique le CLAHE à l'image d'origine pour améliorer le contraste avant de faire la TFD
outil_clahe = CLAHE(5.0, (16, 16))
imgContrastee = outil_clahe.appliquer(testCLAHEImage)

# passage à la TFD
analyseur_tfd = TFD2D(imgContrastee)
spectre = analyseur_tfd.calculerTFDSpectre()
# analyseur_tfd.afficher_spectre()
# analyseur_tfd.filtragePasseBas(90)  # appliquer un filtre passe-bas avec un rayon de coupure de 90 pixels
image_reconstruite = analyseur_tfd.calculerTFDInverse()
analyseur_tfd.afficher_image_reconstruite(image_reconstruite)