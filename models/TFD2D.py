import numpy as np
import matplotlib.pyplot as plt
from FiltrageGaussien import FiltrageGaussien
from ImageConvertie import ImageConvertie


class TFD2D:
    """
    Classe pour calculer la TFD 2D d'une image et visualiser le spectre.
    L'image d'entrée doit être une matrice Numpy 2D normalisée entre 0 et 1 (niveaux de gris).
    Exemple d'instanciation :
    imageConvertie = ImageConvertie('COVID-1024.png').convertirEnNumpyArray()
    testTFD2D = TFD2D(imageConvertie)
    """

    def __init__(self, imageNpArray: np.ndarray):
        """
        Initialise les paramètres pour la FFT 2D.
        :param imageNpArray: Matrice Numpy de l'image.
        """
        self._imageNpArray = imageNpArray
        self._spectre = None

    def calculerTFDSpectre(self):
        """
        Permet de calculer la TFD 2D de l'image spécifiée et de retourner le spectre.
        Pour la magnitude du spectre, on utilise une échelle logarithmique pour une meilleure visualisation.
        La formule est : Spectre = 20 * log(|TFD| + 1) pour éviter les problèmes de log(0).
        :return: Matrice du spectre de la TFD 2D (Numpy 2D array).
        """
        f = np.fft.fft2(self._imageNpArray)  # on applique la TFD 2D à la matrice filtrée
        fshift = np.fft.fftshift(f)  # on déplace la fréquence zéro (les basses fréquences) au centre du spectre
        self._spectre = 20 * np.log(np.abs(fshift) + 1)  # on calcule la magnitude (le spectre) et on utilise l'échelle logarithmique pour la visualisation

        return self._spectre

    # pas utile directement mais je voulais voir si ça ressemblait bien à une TFD et pas autre chose ahaha
    def afficher_spectre(self):
        """
        Affiche le spectre calculé.
        """
        # paramètres pour l'affichage du spectre
        fig, axes = plt.subplots(1, 1, figsize=(12, 6))
        axes.imshow(self._spectre, cmap="gray")
        axes.set_title("Spectre TFD2D (Echelle Log)")
        axes.axis("off")

        plt.tight_layout()  # ajuste automatiquement la disposition
        plt.show()  # affiche


# tests
# testImageConvertie = ImageConvertie("COVID-1024.png").convertirEnNumpyArray()
# testImageConvertie = FiltrageGaussien((5, 5), 0, testImageConvertie).filtrage() # uniquement si on veut appliquer un filtre avant de calculer la TFD
# testTFD2D = TFD2D(testImageConvertie)
# testMatriceTFD2D = testTFD2D.calculerTFDSpectre()
# print(type(testMatriceTFD2D))  # type de la matrice du spectre
# testTFD2D.afficher_spectre()  # à utiliser uniquement pour visualiser le spectre

# assert isinstance(testMatriceTFD2D, np.ndarray), "La matrice du spectre doit être un Numpy array."
# assert testMatriceTFD2D.ndim == 2, "La matrice du spectre doit être en 2D."
