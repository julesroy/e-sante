import numpy as np
from PIL import Image
import pydicom


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
        matrice = None

        if self._imageChemin.lower().endswith('.dcm'): # images DICOM
            # on utilise la bibliothèque pydicom pour ouvrir le fichier DICOM et extraire les données d'image
            dicom_image = pydicom.dcmread(self._imageChemin)
            pixel_array = dicom_image.pixel_array.astype(np.float32)

            # Normalisation des valeurs de pixel entre 0 et 1
            min_val = np.min(pixel_array)
            max_val = np.max(pixel_array)
            if max_val > min_val:  # éviter la division par zéro
                matrice = (pixel_array - min_val) / (max_val - min_val)
            else:
                matrice = np.zeros_like(pixel_array, dtype=np.float32)  # image uniforme si max == min
        else : # images classiques (png, jpg)
            # on utilise la bibliothèque PIL pour ouvrir l'image et la convertir en niveaux de gris
            image = Image.open(self._imageChemin).convert("L")  # 'L' pour convertir en niveaux de gris
            matrice = np.array(image).astype(np.float32) / 255.0  # on convertit l'image en un Numpy array 2D et on normalise les valeurs entre 0 et 1

        return matrice


# tests
# testImageConvertie = ImageConvertie("COVID-1024.png")
# testImageConvertie = ImageConvertie("dcm1.dcm")
# matriceImage = testImageConvertie.convertirEnNumpyArray()
# print(f"[DEBUG] Type de matrice: {matriceImage.dtype}")
# print(matriceImage)  # affiche la matrice de l'image convertie
# print(type(matriceImage))  # type de la matrice de l'image convertie

# assert isinstance(matriceImage, np.ndarray), "La matrice de l'image convertie doit être un Numpy array."
# assert matriceImage.ndim == 2, "La matrice de l'image convertie doit être en 2D (niveaux de gris)."
