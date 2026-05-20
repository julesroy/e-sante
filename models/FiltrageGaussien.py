import cv2

class FiltrageGaussien:
    """
    Classe pour appliquer un filtrage gaussien à une image.
    Exemple d'instanciation :
    test = FiltrageGaussien((9, 9), 0, 'COVID-1024.png', 'FiltrageGaussien.png')
    """

    def __init__(self, kernel:tuple, sigma:int, imagePath:str, imagePathOutput:str):
        """
        Initialise les paramètres pour le filtrage gaussien.
        :param kernel: Tuple représentant la taille du noyau de convolution (ex: (9, 9)).
        :param sigma: Écart type pour la fonction gaussienne.
        :param imagePath: Chemin de l'image d'entrée.
        :param imagePathOutput: Chemin de l'image de sortie après filtrage.
        """
        self._kernel = kernel
        self._sigma = sigma
        self._imagePath = imagePath
        self._imagePathOutput = imagePathOutput

    def filtrage(self):
        """
        Applique le filtrage gaussien à l'image spécifiée et sauvegarde le résultat.
        """
        image = cv2.imread(self._imagePath) # charge l'image
        image_floue = cv2.GaussianBlur(image, self._kernel, self._sigma) # applique le filtrage gaussien
        cv2.imwrite(self._imagePathOutput, image_floue) # sauvegarde l'image filtrée

# test = FiltrageGaussien((9, 9), 0, 'COVID-1024.png', 'FiltrageGaussien.png')
# test.filtrage()