import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cv2
import numpy as np
from models.ImageConvertie import ImageConvertie
from models.FiltrageGaussien import FiltrageGaussien
from models.CLAHE import CLAHE
from models.FiltrageSobel import FiltrageSobel
from models.Seuillage import Seuillage
from models.MorphologieMathematique import MorphologieMathematique
from models.Watershed import SegmentationWatershed

image = ImageConvertie("COVID-1024.png").convertirEnNumpyArray()
# image = ImageConvertie("dcm2.dcm").convertirEnNumpyArray()
# image = CLAHE(5.0, (16, 16), image).appliquer()
image = FiltrageSobel(image).filtrage()
# outil_seuillage = Seuillage(seuil_manuel=None)
# masque, seuil_choisi = outil_seuillage.appliquer(image)

# --- CORRECTION FINALE : INVERSER LE MASQUE ---
# On veut que les poumons (sombres) deviennent blancs (255)
# masque_poumons = cv2.bitwise_not(masque) 

# 3. Nettoyer les petits artéfacts isolés
# masque_propre = MorphologieMathematique(3).ouverture(masque_poumons)

# 4. Segmenter le poumon gauche et droit
# labels = SegmentationWatershed(80).segmenter(masque_propre)

# 5. Préparer l'affichage en couleur
# image_affichage = cv2.normalize(labels, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
# image_couleur = cv2.applyColorMap(image_affichage, cv2.COLORMAP_JET)

cv2.imshow("Resultat pipeline", image)
cv2.waitKey(0)
cv2.destroyAllWindows()