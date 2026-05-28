import numpy as np
import matplotlib.pyplot as plt
from FiltrageGaussien import FiltrageGaussien
from ImageConvertie import ImageConvertie


class TFD2D:
    """
    Classe pour calculer la TFD 2D d'une image et visualiser le spectre.
    L'image d'entrée doit être une matrice Numpy 2D normalisée entre 0 et 1 (niveaux de gris).
    Exemple d'utilisation :
    imageConvertie = ImageConvertie('COVID-1024.png').convertirEnNumpyArray()
    testTFD2D = TFD2D(imageConvertie)
    spectre = testTFD2D.calculerTFDSpectre()
    testTFD2D.afficher_spectre()
    image_reconstruite = testTFD2D.calculerTFDInverse()
    testTFD2D.afficher_image_reconstruite(image_reconstruite)
    """

    def __init__(self, imageNpArray: np.ndarray):
        """
        Initialise les paramètres pour la FFT 2D.
        :param imageNpArray: Matrice Numpy de l'image.
        """
        self._imageNpArray = imageNpArray
        self._spectre = None
        self._fshift_complexe = None

    def calculerTFDSpectre(self):
        """
        Permet de calculer la TFD 2D de l'image spécifiée et de retourner le spectre.
        Pour la magnitude du spectre, on utilise une échelle logarithmique pour une meilleure visualisation.
        La formule est : Spectre = 20 * log(|TFD| + 1) pour éviter les problèmes de log(0).
        :return: Matrice du spectre de la TFD 2D (Numpy 2D array).
        """
        f = np.fft.fft2(self._imageNpArray)  # on applique la TFD 2D à la matrice filtrée
        fshift = np.fft.fftshift(f)  # on déplace la fréquence zéro (les basses fréquences) au centre du spectre
        self._fshift_complexe = fshift  # on stocke la TFD complexe pour pouvoir faire la TFD inverse plus tard
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

    def calculerTFDInverse(self):
        """
        Permet de calculer la TFD inverse à partir de la TFD complexe stockée précédemment.
        :return: Matrice de l'image reconstruite à partir de la TFD inverse (Numpy 2D array).
        """
        f_ishift = np.fft.ifftshift(self._fshift_complexe)  # on inverse le décalage pour remettre les basses fréquences à leur position d'origine
        img_complexe = np.fft.ifft2(f_ishift)  # on applique la TFD inverse pour reconstruire l'image à partir de la TFD complexe
        img_reconstruite = np.abs(img_complexe)  # on prend la partie réelle de l'image reconstruite

        return img_reconstruite

    # pareil pas utile directement mais je voulais voir si l'image reconstruite ressemblait bien à l'image d'origine
    def afficher_image_reconstruite(self, image_reconstruite: np.ndarray):
        """
        Affiche l'image reconstruite après la TFD Inverse.
        :param image_reconstruite: Matrice Numpy 2D retournée par calculerTFDInverse().
        """
        fig, axes = plt.subplots(1, 2, figsize=(12, 6))

        axes[0].imshow(self._imageNpArray, cmap="gray")
        axes[0].set_title("Image d'Origine")
        axes[0].axis("off")

        axes[1].imshow(image_reconstruite, cmap="gray")
        axes[1].set_title("Image Reconstruite (TFDI)")
        axes[1].axis("off")

        plt.tight_layout()
        plt.show()

    def filtragePasseBas(self, rayon_coupure: int):
        """
        Applique un filtre passe-bas dit 'idéal' en ne gardant que les fréquences
        situées dans un cercle central de rayon 'rayon_coupure'.
        :param rayon_coupure: Rayon du cercle en pixels (plus il est petit, plus le flou est fort).
        :return: Matrice de l'image filtrée.
        """
        if self._fshift_complexe is None:
            raise ValueError("Le spectre doit être calculé avec calculerTFDSpectre().")

        hauteur, largeur = self._fshift_complexe.shape  # on récupère les dimensions de la TFD pour créer le masque
        centre_y, centre_x = (
            hauteur // 2,
            largeur // 2,
        )  # on calcule les coordonnées du centre du spectre (où se trouvent les basses fréquences) pour centrer notre cercle de filtrage autour de ce point

        y, x = np.ogrid[
            :hauteur, :largeur
        ]  # on crée des grilles de coordonnées pour chaque pixel du spectre, ce qui nous permettra de calculer la distance de chaque pixel au centre du spectre et de déterminer s'il est à l'intérieur ou à l'extérieur du cercle de filtrage

        # équation d'un cercle : (x - x0)^2 + (y - y0)^2 <= R^2
        masque_circulaire = ((x - centre_x) ** 2 + (y - centre_y) ** 2 <= rayon_coupure**2).astype(
            float
        )  # on crée un masque binaire où les pixels à l'intérieur du cercle de rayon 'rayon_coupure' sont égaux à 1 (conservés) et les pixels à l'extérieur sont égaux à 0 (filtrés)

        self._fshift_complexe = (
            self._fshift_complexe * masque_circulaire
        )  # on applique le masque de filtrage à la TFD complexe en multipliant élément par élément, ce qui conserve les fréquences à l'intérieur du cercle et supprime les fréquences à l'extérieur

        return self._fshift_complexe

    def filtragePasseHaut(self, rayon_coupure: int):
        """
        Applique un filtre passe-haut en ne gardant que les fréquences situées à l'extérieur d'un cercle de rayon 'rayon_coupure'.
        :param rayon_coupure: Rayon du cercle en pixels (plus il est grand, plus le filtrage est fort).
        :return: Matrice de l'image filtrée.
        """
        if self._fshift_complexe is None:
            raise ValueError("Le spectre doit être calculé avec calculerTFDSpectre().")

        hauteur, largeur = self._fshift_complexe.shape
        centre_y, centre_x = hauteur // 2, largeur // 2

        y, x = np.ogrid[:hauteur, :largeur]

        masque_circulaire = ((x - centre_x) ** 2 + (y - centre_y) ** 2 >= rayon_coupure**2).astype(
            float
        )  # on inverse la condition pour créer un masque qui conserve les fréquences à l'extérieur du cercle et supprime les fréquences à l'intérieur

        self._fshift_complexe = self._fshift_complexe * masque_circulaire

        return self._fshift_complexe


# tests
# testImageConvertie = ImageConvertie("COVID-1024.png").convertirEnNumpyArray()
# testImageConvertie = FiltrageGaussien((5, 5), 0, testImageConvertie).filtrage() # uniquement si on veut appliquer un filtre Gaussien avant de calculer la TFD
# testTFD2D = TFD2D(testImageConvertie)
# testMatriceTFD2D = testTFD2D.calculerTFDSpectre()
# print(type(testMatriceTFD2D))  # type de la matrice du spectre
# testTFD2D.afficher_spectre()  # à utiliser uniquement pour visualiser le spectre
# testTFD2D.filtragePasseBas(90)  # appliquer un filtre passe-bas avec un rayon de coupure de 90 pixels
# testTFD2D.filtragePasseHaut(10)  # appliquer un filtre passe-haut avec un rayon de coupure de 10 pixels
# testImageReconstruite = testTFD2D.calculerTFDInverse()
# testTFD2D.afficher_image_reconstruite(testImageReconstruite)

# assert isinstance(testMatriceTFD2D, np.ndarray), "La matrice du spectre doit être un Numpy array."
# assert testMatriceTFD2D.ndim == 2, "La matrice du spectre doit être en 2D."
