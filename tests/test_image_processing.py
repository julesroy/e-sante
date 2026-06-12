import numpy as np
import pytest
from models.FiltrageGaussien import FiltrageGaussien
from models.FiltrageSobel import FiltrageSobel
from models.Seuillage import Seuillage
from models.TFD2D import TFD2D
from models.CLAHE import CLAHE
from models.Watershed import SegmentationWatershed


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


def test_watershed():
    # Crée un masque binaire factice avec un objet au centre et un objet sur le bord
    masque = np.zeros((128, 128), dtype=np.uint8)
    masque[40:80, 40:80] = 255  # Objet central
    masque[0:20, 0:20] = 255    # Objet sur la bordure

    outil = SegmentationWatershed(min_distance_marqueurs=10)
    labels = outil.segmenter(masque)

    assert isinstance(labels, np.ndarray)
    assert labels.shape == (128, 128)
    # L'objet sur la bordure doit être segmenté (valeurs > 0)
    assert np.any(labels[0:20, 0:20] > 0)
    # L'objet au centre doit être segmenté (valeurs > 0)
    assert np.any(labels[40:80, 40:80] > 0)


def test_area_calculation():
    # Crée un faux masque de labels
    labels = np.zeros((10, 10), dtype=np.int32)
    labels[1:3, 1:3] = 1  # Zone 1 de taille 2x2 = 4 pixels
    labels[5:8, 5:8] = 2  # Zone 2 de taille 3x3 = 9 pixels

    unique_labels = np.unique(labels)
    unique_labels = unique_labels[unique_labels != 0]

    assert len(unique_labels) == 2
    assert np.sum(labels == 1) == 4
    assert np.sum(labels == 2) == 9


def test_histogramme(dummy_image):
    from models.Histogramme import Histogramme
    histo = Histogramme(dummy_image)
    plot_data, plot_range = histo.obtenir_donnees_tracage()

    assert isinstance(plot_data, np.ndarray)
    assert len(plot_data) == 128 * 128
    assert plot_range == (0, 255)
    assert histo.min_val >= 0.0
    assert histo.max_val <= 255.0
    assert isinstance(histo.mean_val, float)
    assert isinstance(histo.std_val, float)



