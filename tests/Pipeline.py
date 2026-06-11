import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cv2
import numpy as np
import scipy.ndimage as ndimage
from models.ImageConvertie import ImageConvertie
from models.FiltrageGaussien import FiltrageGaussien
from models.CLAHE import CLAHE
from models.FiltrageSobel import FiltrageSobel
from models.Seuillage import Seuillage
from models.MorphologieMathematique import MorphologieMathematique
from models.Watershed import SegmentationWatershed

image = ImageConvertie("brain2.png").convertirEnNumpyArray()
# image = ImageConvertie("dcm2.dcm").convertirEnNumpyArray()
image_filtree = FiltrageGaussien(2, image).filtrage()
# image_filtree = CLAHE(2.0, (16, 16), image_filtree).appliquer()
# image_filtree = FiltrageSobel(image_filtree).filtrage()
outil_seuillage = Seuillage(40)
masque, seuil_choisi = outil_seuillage.appliquer(image_filtree)

print(f"Seuil choisi : {seuil_choisi}")

# --- CORRECTION FINALE : OBTENIR LES CAVITÉS INTERNES ---
# Remplir les trous du masque original pour obtenir le masque de la tête
masque_rempli = ndimage.binary_fill_holes(masque > 0)
# Les cavités internes sont les pixels dans la tête mais sombres sur l'image d'origine
masque_poumons = ((masque_rempli * 255).astype(np.uint8) > 0) & (masque == 0)
masque_poumons = (masque_poumons * 255).astype(np.uint8) 

# 3. Nettoyer les petits artéfacts isolés
masque_propre = MorphologieMathematique(3).ouverture(masque_poumons)

# 4. Segmenter le poumon gauche et droit
labels = SegmentationWatershed(20, True).segmenter(masque_propre)

# 5. Préparer l'affichage en couleur
image_affichage = cv2.normalize(labels, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
image_couleur = cv2.applyColorMap(image_affichage, cv2.COLORMAP_JET)

# 6. Superposer l'image de base (niveaux de gris) et le résultat en couleur
img_8bit = (image * 255).astype(np.uint8)
img_bgr = cv2.cvtColor(img_8bit, cv2.COLOR_GRAY2BGR)

# Créer la superposition transparente (overlay) sur les zones segmentées
mask_roi = labels > 0
overlay = img_bgr.copy()
blended = cv2.addWeighted(img_bgr, 0.6, image_couleur, 0.4, 0)
overlay[mask_roi] = blended[mask_roi]

# cv2.imshow("Resultat seuillage - Masque", masque)
cv2.imshow("Resultat pipeline - Segments", image_couleur)
cv2.imshow("Resultat pipeline - Superposition", overlay)
cv2.waitKey(0)
cv2.destroyAllWindows()