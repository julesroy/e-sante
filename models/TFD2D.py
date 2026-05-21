import numpy as np
import matplotlib.pyplot as plt
from FiltrageGaussien import FiltrageGaussien


class TFD2D:
    """
    Classe pour calculer la TFD 2D d'une image et visualiser le spectre.
    Exemple d'instanciation :
    testTFD2D = TFD2D('COVID-1024.png')
    """

    def __init__(self, imagePath: str):
        """
        Initialise les paramètres pour la FFT 2D.
        :param imagePath: Chemin de l'image d'entrée.
        """
        self._imagePath = imagePath
        self._spectre = None

    def calculerTFDSpectre(self):
        """
        Permet de calculer la TFD 2D de l'image spécifiée et de retourner le spectre.
        Pour la magnitude du spectre, on utilise une échelle logarithmique pour une meilleure visualisation.
        La formule est : Spectre = 20 * log(|TFD| + 1) pour éviter les problèmes de log(0).
        :return: Matrice du spectre de la TFD 2D (Numpy 2D array).
        """
        # on applique un filtrage gaussien à l'image pour réduire le bruit avant de calculer la TFD
        matrice = FiltrageGaussien((5, 5), 0, self._imagePath)
        matriceFiltree = matrice.filtrage()  # la matrice filtrée est une matrice 2D de type numpy.ndarray, représentant l'image filtrée en niveaux de gris (hauteur x largeur)

        f = np.fft.fft2(matriceFiltree)  # on applique la TFD 2D à la matrice filtrée
        fshift = np.fft.fftshift(f)  # on déplace la fréquence zéro (les basses fréquences) au centre du spectre
        self._spectre = 20 * np.log(np.abs(fshift) + 1)  # on calcule la magnitude (le spectre) et on utilise l'échelle logarithmique pour la visualisation

        return self._spectre

    # pas utile directement mais je voulais voir si ça ressemblait bien à une TFD et pas autre chose ahaha
    def afficher_spectre(self):
        """
        Affiche le spectre calculé.
        """
        # paramètres pour l'affichage du spectre
        axes = plt.subplots(1, 1, figsize=(12, 6))
        axes.imshow(self._spectre, cmap="gray")
        axes.set_title("Spectre FFT 2D (Echelle Log)")
        axes.axis("off")

        plt.tight_layout()  # ajuste automatiquement la disposition
        plt.show()  # affiche


# testTFD2D = TFD2D('COVID-1024.png')
# matriceTFD2D = testTFD2D.calculerTFDSpectre()
# print(type(matriceTFD2D)) # type de la matrice du spectre
# testTFD2D.afficher_spectre() # à utiliser uniquement pour visualiser le spectre
