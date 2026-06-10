import numpy as np
import scipy.ndimage as ndimage

class MorphologieMathematique:
    """
    Classe pour nettoyer les masques binaires à l'aide de la morphologie mathématique.
    Utilise SciPy pour exécuter l'érosion, la dilatation, l'ouverture et la fermeture.
    """

    def __init__(self, taille_noyau: int = 3):
        """
        Initialise l'élément structurant (le noyau de convolution).
        :param taille_noyau: Taille de la matrice carrée du noyau (ex: 3 pour une matrice 3x3).
        """
        if taille_noyau % 2 == 0:
            raise ValueError("La taille du noyau doit être un entier impair.")
        
        # Génère un noyau carré rempli de True (équivalent à un élément structurant cv2.MORPH_RECT)
        self._structure = np.ones((taille_noyau, taille_noyau), dtype=bool)

    def erosion(self, masque_binaire: np.ndarray) -> np.ndarray:
        """Affinage des structures et suppression des points isolés."""
        # ndimage.binary_erosion retourne des booléens, on reconvertit en uint8 (0 ou 255)
        res = ndimage.binary_erosion(masque_binaire, structure=self._structure)
        return (res * 255).astype(np.uint8)

    def dilatation(self, masque_binaire: np.ndarray) -> np.ndarray:
        """Élargissement des bords et rebouchage des trous internes."""
        res = ndimage.binary_dilation(masque_binaire, structure=self._structure)
        return (res * 255).astype(np.uint8)

    def ouverture(self, masque_binaire: np.ndarray) -> np.ndarray:
        """Érosion puis Dilatation : supprime les parasites extérieurs sans changer la taille globale."""
        res = ndimage.binary_opening(masque_binaire, structure=self._structure)
        return (res * 255).astype(np.uint8)

    def fermeture(self, masque_binaire: np.ndarray) -> np.ndarray:
        """Dilatation puis Érosion : boche les trous internes sans changer la taille globale."""
        res = ndimage.binary_closing(masque_binaire, structure=self._structure)
        return (res * 255).astype(np.uint8)