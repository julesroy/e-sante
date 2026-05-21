from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtGui import QImage, QPixmap
import numpy as np
import sys, os

# j'ajoute le dossier model au path pour pouvoir importer depuis controllers/
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "models"))

from ImageConvertie import ImageConvertie
from FiltrageGaussien import FiltrageGaussien


class MainController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        # Stockage de l'image courante sous forme numpy (float32 [0,1])
        # None tant qu'aucune image n'est chargee
        self._current_array: np.array | None = None

        self._connect_signals()

    def _connect_signals(self):
        # bouton d'upload
        self.view.btn_upload.clicked.connect(self.handle_upload)

    def handle_upload(self):
        """
        Ouvre l'explorateur de fichiers, affiche l'image dans la View
        et stocke sa matrice numpy normalisée pour les traitements ultérieurs.
        """
        # explorateur de fichiers
        file_path, _ = QFileDialog.getOpenFileName(
            self.view,
            "Sélectionner une radiographie",
            "",
            "Images (*.png *.jpg *.jpeg)",
        )

        # Si image on l'affiche
        if file_path:
            # affichage brut de l'image
            self.view.display_medical_image(file_path)

            self._current_array = ImageConvertie(file_path).convertirEnNumpyArray()

    def _display_numpy_array(self, array: np.ndarray):
        """
        Convertit un np.ndarray float32 2D [0,1] en QPixmap
        et l'envoie directement au QLabel de la View.

        :param array: Matrice 2D numpy float32, valeurs entre 0 et 1.
        """
        # on denormalise : on repasse de [0,1] a [0,255] pour QImage
        img_uint8 = (array * 255).astype(np.uint8)

        h, w = img_uint8.shape  # hauteur et largeur de l'image

        # QImage attend : data, largeur, hauteur, bytes_per_line, format
        # Format_Grayscale8 = 1 octet par pixel ce qui est parfait pour les images medicales
        qimage = QImage(img_uint8.data, w, h, w, QImage.Format.Format_Grayscale8)

        # Conversion QImage -> QPixmap pour l'affichage dans un QLabel
        pixmap = QPixmap.fromImage(qimage)

        # Activation du zoom (current_file_path doit etre non-None)
        self.view.current_file_path = "from_controller"

        # Envoie a la View : on set le pixmap directement sur le QLabel
        self.view.image_display.setPixmap(pixmap)

        # Recalcul du rendu avec zoom si necessaire
        self.view.update_image_render()

    def handle_gaussian(self):
        """
        Applique le filtre gaussien sur l'image courante
        et affiche le résultat dans la View.
        Nécessite qu'une image soit chargée (_current_array != None).
        """

        # on ne fait rien si aucune image n'est chargee
        if self._current_array is None:
            return

        # Kernel 9×9 (noyau de convolution) — sigma=0 = auto calculé par OpenCV
        kernel_size = 9
        filtre = FiltrageGaussien((kernel_size, kernel_size), 0, self._current_array)

        # Application du filtre -> retourne un np.ndarray
        result_array = filtre.filtrage()

        # Affichage du resultat via notre methode centrale
        self._display_numpy_array(result_array)
