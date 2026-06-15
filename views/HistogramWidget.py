from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QGridLayout, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import numpy as np
import matplotlib.pyplot as plt
import io
from models.Histogramme import Histogramme


class HistogramWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName("HistogramWidget")

        # Style sombre assorti à la charte graphique de l'application
        self.setStyleSheet("""
            #HistogramWidget {
                background-color: rgba(32, 32, 32, 220);
                border: 1px solid #3c3c3c;
                border-radius: 5px;
            }
            QLabel {
                color: #e0e0e0;
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QCheckBox {
                color: #e0e0e0;
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: 11px;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
                background-color: #202020;
                border: 1px solid #555555;
                border-radius: 2px;
            }
            QCheckBox::indicator:checked {
                background-color: #00a2ed;
                border-color: #00a2ed;
            }
        """)

        self.image_array = None
        self.file_path = None
        self.linear_scale = True

        self.plot_data = None
        self.plot_range = (0, 255)

        # Layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(12, 12, 12, 12)
        self.main_layout.setSpacing(10)

        # --- EN-TÊTE D'ÉCHELLE ---
        self.header_layout = QHBoxLayout()
        self.header_layout.setSpacing(5)

        self.lbl_left_val = QLabel("0")
        self.lbl_left_val.setStyleSheet("color: #a0a0a0; font-size: 10px; font-weight: bold;")
        self.lbl_left_val.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.lbl_title = QLabel("Input Values")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_title.setStyleSheet("font-weight: bold; font-size: 11px; color: #ffffff;")

        self.lbl_right_val = QLabel("255")
        self.lbl_right_val.setStyleSheet("color: #a0a0a0; font-size: 10px; font-weight: bold;")
        self.lbl_right_val.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.header_layout.addWidget(self.lbl_left_val, 1)
        self.header_layout.addWidget(self.lbl_title, 2)
        self.header_layout.addWidget(self.lbl_right_val, 1)

        self.main_layout.addLayout(self.header_layout)

        # --- INTÉGRATION DE LA ZONE DE GRAPHique ---
        self.plot_label = QLabel()
        self.plot_label.setFixedSize(300, 120)
        self.plot_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.plot_label.setStyleSheet("background-color: #1a1a1a; border: 1px solid #2d2d2d; border-radius: 3px;")
        self.main_layout.addWidget(self.plot_label)

        # --- SÉPARATEUR DE SECTION ---
        self.sep = QFrame()
        self.sep.setFrameShape(QFrame.Shape.HLine)
        self.sep.setFrameShadow(QFrame.Shadow.Sunken)
        self.sep.setStyleSheet("background-color: #3c3c3c; max-height: 1px; border: none;")
        self.main_layout.addWidget(self.sep)

        # --- CASE À COCHER ÉCHELLE ---
        self.chk_linear = QCheckBox("Linear scale")
        self.chk_linear.setChecked(True)
        self.chk_linear.stateChanged.connect(self.on_scale_changed)
        self.main_layout.addWidget(self.chk_linear)

        # --- GRILLE DE STATISTIQUES ---
        self.stats_layout = QGridLayout()
        self.stats_layout.setHorizontalSpacing(15)
        self.stats_layout.setVerticalSpacing(4)

        self.lbl_min_title = QLabel("Min")
        self.lbl_min_title.setStyleSheet("color: #888888; font-size: 11px;")
        self.lbl_min_val = QLabel("-")
        self.lbl_min_val.setStyleSheet("font-weight: bold; font-size: 11px; color: #ffffff;")
        self.lbl_min_val.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.lbl_max_title = QLabel("Max")
        self.lbl_max_title.setStyleSheet("color: #888888; font-size: 11px;")
        self.lbl_max_val = QLabel("-")
        self.lbl_max_val.setStyleSheet("font-weight: bold; font-size: 11px; color: #ffffff;")
        self.lbl_max_val.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.lbl_mean_title = QLabel("Moy.")
        self.lbl_mean_title.setStyleSheet("color: #888888; font-size: 11px;")
        self.lbl_mean_val = QLabel("-")
        self.lbl_mean_val.setStyleSheet("font-weight: bold; font-size: 11px; color: #ffffff;")
        self.lbl_mean_val.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.lbl_std_title = QLabel("Ecart-type")
        self.lbl_std_title.setStyleSheet("color: #888888; font-size: 11px;")
        self.lbl_std_val = QLabel("-")
        self.lbl_std_val.setStyleSheet("font-weight: bold; font-size: 11px; color: #ffffff;")
        self.lbl_std_val.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Ajout des widgets dans la grille
        self.stats_layout.addWidget(self.lbl_min_title, 0, 0)
        self.stats_layout.addWidget(self.lbl_min_val, 0, 1)
        self.stats_layout.addWidget(self.lbl_max_title, 1, 0)
        self.stats_layout.addWidget(self.lbl_max_val, 1, 1)

        self.stats_layout.addWidget(self.lbl_mean_title, 0, 2)
        self.stats_layout.addWidget(self.lbl_mean_val, 0, 3)
        self.stats_layout.addWidget(self.lbl_std_title, 1, 2)
        self.stats_layout.addWidget(self.lbl_std_val, 1, 3)

        self.main_layout.addLayout(self.stats_layout)

        # Taille fixe du widget overlay
        self.setFixedSize(324, 250)

    def set_image_data(self, image_array: np.ndarray, file_path: str | None):
        """
        Met à jour les données de l'image, recalcule les statistiques
        et redessine le graphique de l'histogramme.
        """
        self.image_array = image_array
        self.file_path = file_path

        # Utiliser le modèle Histogramme pour calculer les statistiques
        histo_model = Histogramme(image_array, file_path)

        # Mise à jour des affichages textuels de l'en-tête et des statistiques
        self.lbl_left_val.setText(str(int(histo_model.left_val)))
        self.lbl_right_val.setText(str(int(histo_model.right_val)))

        self.lbl_min_val.setText(f"{int(histo_model.min_val)}")
        self.lbl_max_val.setText(f"{int(histo_model.max_val)}")
        self.lbl_mean_val.setText(f"{histo_model.mean_val:.1f}")
        self.lbl_std_val.setText(f"{histo_model.std_val:.2f}")

        # Récupération des données pour le tracé
        self.plot_data, self.plot_range = histo_model.obtenir_donnees_tracage()

        # Dessiner le graphique
        self.update_plot()

    def update_plot(self):
        if self.plot_data is None:
            return

        # Calculer l'histogramme avec 256 bacs (bins) pour l'affichage
        hist, bin_edges = np.histogram(self.plot_data, bins=256, range=self.plot_range)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

        dpi = 100
        # 300x120 pixels en pouces pour matplotlib
        fig, ax = plt.subplots(figsize=(300 / dpi, 120 / dpi), dpi=dpi, facecolor='#1a1a1a')
        ax.set_facecolor('#1a1a1a')

        # Tracé de la courbe et de son aire
        ax.plot(bin_centers, hist, color='#00a2ed', linewidth=1.2)
        ax.fill_between(bin_centers, hist, color='#00a2ed', alpha=0.25)

        # Gestion de l'échelle linéaire / logarithmique
        if not self.linear_scale:
            ax.set_yscale('log')
            # Fixer une valeur minimale pour éviter un rendu brisé si certains bacs sont vides
            ax.set_ylim(bottom=0.8)

        # Grille verticale uniquement (comme sur la capture utilisateur)
        ax.grid(True, which='both', axis='x', color='#3c3c3c', linestyle='-', linewidth=0.5, alpha=0.5)
        ax.grid(False, axis='y')

        # Masquer les bordures inutiles
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color('#3c3c3c')
        ax.spines['bottom'].set_linewidth(0.5)

        # Masquer les axes et graduations Y, n'afficher que des graduations X minimales
        ax.yaxis.set_visible(False)
        ax.tick_params(colors='#888888', labelsize=8, length=0)
        ax.set_xticklabels([])  # Pas de texte de graduations (géré par l'en-tête du widget)

        # Ajuster les espacements
        plt.tight_layout()

        # Exporter l'image au format PNG en mémoire
        buf = io.BytesIO()
        plt.savefig(buf, format='png', facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)

        # Charger dans un QPixmap et l'afficher
        pixmap = QPixmap()
        pixmap.loadFromData(buf.read())
        self.plot_label.setPixmap(pixmap)

    def on_scale_changed(self, state):
        self.linear_scale = self.chk_linear.isChecked()
        self.update_plot()
