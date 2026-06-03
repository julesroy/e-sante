import cv2
import numpy as np
from ImageConvertie import ImageConvertie
from FiltrageGaussien import FiltrageGaussien
from CLAHE import CLAHE
from FiltrageSobel import FiltrageSobel
from Seuillage import Seuillage

image = ImageConvertie("COVID-1024.png").convertirEnNumpyArray()
# image = ImageConvertie("dcm1.dcm").convertirEnNumpyArray()
image = CLAHE(5.0, (16, 16), image).appliquer()
image = FiltrageSobel(3, image).filtrage()


cv2.imshow('Image après application de la pipeline', image)
cv2.waitKey(0)
cv2.destroyAllWindows()