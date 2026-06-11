from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np
    from PyQt6.QtGui import QPixmap


class MainModel:
    def __init__(self):
        # État applicatif (Session)
        self.current_array: np.ndarray | None = None
        self.original_pixmap: QPixmap | None = None
        self.contrast_base_array: np.ndarray | None = None
        self.current_patient_id: int | None = None
        self.last_file_path: str | None = None
        self.watershed_labels: np.ndarray | None = None
