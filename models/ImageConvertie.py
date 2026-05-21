import numpy as np
from PIL import Image


class ImageConvertie:
    """
    Classe pour convertir une image en Numpy array. En niveaux de gris et normalisée entre 0 et 1.
    Exemple d'instanciation : ImageConvertie('chemin/vers/image.png')
    """

    def __init__(self, imageChemin: str):
        """
        Initialise les paramètres pour la conversion de l'image.
        :param imageChemin: Chemin de l'image d'entrée.
        """
        self._imageChemin = imageChemin

    def convertirEnNumpyArray(self):
        """
        Permet de convertir l'image spécifiée en un Numpy array en niveaux de gris.
        La matrice résultante est normalisée entre 0 et 1 pour faciliter les traitements ultérieurs.
        :return: Matrice 2D de l'image convertie (Numpy 2D array).
        """
        # on utilise la bibliothèque PIL pour ouvrir l'image et la convertir en niveaux de gris
        image = Image.open(self._imageChemin).convert("L")  # 'L' pour convertir en niveaux de gris
        matrice = np.array(image).astype(np.float32) / 255.0  # on convertit l'image en un Numpy array 2D et on normalise les valeurs entre 0 et 1

        return matrice


# tests
# testImageConvertie = ImageConvertie("COVID-1024.png")
# matriceImage = testImageConvertie.convertirEnNumpyArray()
# print(matriceImage)  # affiche la matrice de l'image convertie
# print(type(matriceImage))  # type de la matrice de l'image convertie

# assert isinstance(matriceImage, np.ndarray), "La matrice de l'image convertie doit être un Numpy array."
# assert matriceImage.ndim == 2, "La matrice de l'image convertie doit être en 2D (niveaux de gris)."
