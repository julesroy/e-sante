import cv2
import numpy as np
import matplotlib.pyplot as plt
from ImageConvertie import ImageConvertie
from TFD2D import TFD2D

class Seuillage:
    """
    Classe pour binariser une image par seuillage (Simple ou Otsu).
    L'image d'entrée doit être une matrice Numpy 2D (uint8, 0-255).
    """

    def __init__(self, seuil_manuel: int | None = None):
        """
        :param seuil_manuel: Valeur fixe entre 0 et 255. Si None, Otsu est utilisé.
        """
        self._seuil_manuel = seuil_manuel

    def appliquer(self, imageNpArray: np.ndarray) -> tuple[np.ndarray, float]:
            if imageNpArray is None:
                raise ValueError("La matrice d'image fournie est vide.")

            # on recale dynamiquement le minimum à 0 et le maximum à 255
            img_min = imageNpArray.min()
            img_max = imageNpArray.max()
            
            if img_max - img_min == 0:
                # on évite la division par zéro si l'image est déjà complètement uniforme
                img_8bit = np.zeros(imageNpArray.shape, dtype=np.uint8)
            else:
                # formule de normalisation Min-Max
                img_8bit = (255 * (imageNpArray - img_min) / (img_max - img_min)).astype(np.uint8)
            # ----------------------------------------------------

            if self._seuil_manuel is not None:
                seuil_calcule, masque_binaire = cv2.threshold(
                    img_8bit, self._seuil_manuel, 255, cv2.THRESH_BINARY
                )
            else:
                seuil_calcule, masque_binaire = cv2.threshold(
                    img_8bit, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
                )

            return masque_binaire, seuil_calcule

# tests
# testImageConvertie = ImageConvertie("COVID-1024.png").convertirEnNumpyArray()
# testTFD2D = TFD2D(testImageConvertie)
# testMatriceTFD2D = testTFD2D.calculerTFDSpectre()
# testTFD2D.filtragePasseBas(90)  # appliquer un filtre passe-bas avec un rayon de coupure de 90 pixels
# testTFD2D.filtragePasseHaut(10)  # appliquer un filtre passe-haut avec un rayon de coupure de 10 pixels
# testImageReconstruite = testTFD2D.calculerTFDInverse()
# testTFD2D.afficher_image_reconstruite(testImageReconstruite)

# instancier le seuillage automatique d'Otsu (Fortement recommandé en médical)
# outil_seuillage = Seuillage(seuil_manuel=None)
# masque, seuil_choisi = outil_seuillage.appliquer(testImageReconstruite)

# print(f"Le seuil optimal calculé par Otsu est : {seuil_choisi}")
# fig, ax = plt.subplots(1, 1, figsize=(6, 6))
# ax.imshow(masque, cmap="gray")
# ax.set_title(f"Masque Binaire Otsu (Seuil: {seuil_choisi})")
# ax.axis("off")
# plt.show()