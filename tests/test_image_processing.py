import numpy as np
import pytest
from models.FiltrageGaussien import FiltrageGaussien
from models.FiltrageSobel import FiltrageSobel
from models.Seuillage import Seuillage
from models.TFD2D import TFD2D
from models.CLAHE import CLAHE


@pytest.fixture
def dummy_image():
    # Crée une image factice de 128x128 normalisée [0, 1]
    np.random.seed(42)
    return np.random.rand(128, 128).astype(np.float32)


def test_filtrage_gaussien(dummy_image):
    filtre = FiltrageGaussien(sigma=2, imageNpArray=dummy_image)
    res = filtre.filtrage()

    assert isinstance(res, np.ndarray)
    assert res.shape == (128, 128)
    assert res.dtype == np.float32


def test_filtrage_sobel(dummy_image):
    filtre = FiltrageSobel(imageNpArray=dummy_image)
    res = filtre.filtrage()

    assert isinstance(res, np.ndarray)
    assert res.shape == (128, 128)
    # Sobel renvoie une image normalisée entre 0 et 1 (dtype float32/float64)
    assert res.min() >= 0.0
    assert res.max() <= 1.0


def test_seuillage_otsu(dummy_image):
    outil = Seuillage(seuil_manuel=None)  # Otsu
    masque, seuil = outil.appliquer(dummy_image)

    assert isinstance(masque, np.ndarray)
    assert masque.shape == (128, 128)
    assert masque.dtype == np.uint8
    assert isinstance(seuil, (int, float))


def test_seuillage_manuel(dummy_image):
    outil = Seuillage(seuil_manuel=128)
    masque, seuil = outil.appliquer(dummy_image)

    assert isinstance(masque, np.ndarray)
    assert masque.shape == (128, 128)
    assert masque.dtype == np.uint8
    assert seuil == 128


def test_tfd2d(dummy_image):
    tfd = TFD2D(dummy_image)

    # 1. Calcul du spectre
    spectre = tfd.calculerTFDSpectre()
    assert isinstance(spectre, np.ndarray)
    assert spectre.shape == (128, 128)

    # 2. Filtrage passe bas
    tfd.filtragePasseBas(20)

    # 3. Reconstruction
    reconstruite = tfd.calculerTFDInverse()
    assert isinstance(reconstruite, np.ndarray)
    assert reconstruite.shape == (128, 128)


def test_clahe(dummy_image):
    # CLAHE attend des valeurs entre 0 et 1, ou en 8-bit
    outil = CLAHE(limitationContraste=4.0, tailleGrilleLocale=(8, 8), imageNpArray=dummy_image)
    res = outil.appliquer()

    assert isinstance(res, np.ndarray)
    assert res.shape == (128, 128)
    assert res.dtype == np.float32
    assert res.min() >= 0.0
    assert res.max() <= 1.0
