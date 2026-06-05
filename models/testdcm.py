import numpy as np
import pydicom
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter, sobel


def load_dicom(path: str) -> np.ndarray:
    ds = pydicom.dcmread(path)
    image = ds.pixel_array.astype(np.float32)
    image -= image.min()
    image /= image.max()
    return image


def apply_gaussian(image: np.ndarray, sigma: float = 5.0) -> np.ndarray:
    return gaussian_filter(image, sigma=sigma)


def apply_sobel(image: np.ndarray) -> np.ndarray:
    gx = sobel(image, axis=1)
    gy = sobel(image, axis=0)
    magnitude = np.hypot(gx, gy)

    # ✅ Clip percentile : ignore les 1% de valeurs extrêmes
    p_low = np.percentile(magnitude, 1)
    p_high = np.percentile(magnitude, 99)
    magnitude = np.clip(magnitude, p_low, p_high)
    magnitude = (magnitude - p_low) / (p_high - p_low)
    return magnitude


def process_and_display(path: str, sigma: float = 5.0):
    original = load_dicom(path)
    gaussienne = apply_gaussian(original, sigma=sigma)
    sobel_brut = apply_sobel(original)
    sobel_after_gaussian = apply_sobel(gaussienne)

    # Différence pour rendre le flou visible
    diff_gaussien = np.abs(original - gaussienne)
    diff_gaussien /= diff_gaussien.max()

    fig, axes = plt.subplots(1, 5, figsize=(25, 5))
    images = [original, gaussienne, diff_gaussien, sobel_brut, sobel_after_gaussian]
    titles = [
        "Original",
        f"Gaussien (σ={sigma})",
        "Diff (flou - original)",  # ← rend le flou explicite
        "Sobel (brut)",
        "Sobel après Gaussien",
    ]
    for ax, img, title in zip(axes, images, titles):
        ax.imshow(img, cmap="gray")
        ax.set_title(title)
        ax.axis("off")

    plt.tight_layout()
    plt.savefig("output_filtres.png", dpi=150)
    plt.show()


if __name__ == "__main__":
    process_and_display("dcm1.dcm", sigma=8.0)
