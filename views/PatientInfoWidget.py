from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt

class PatientInfoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_view = parent
        self.setFixedWidth(200)
        self.setObjectName("PatientInfoPanel")
        
        # Layout principal
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 15, 10, 15)
        self.layout.setSpacing(12)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # --- HAUT DE PAGE : TITRE + BOUTON FERMER ---
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        self.title_label = QLabel("📋 FICHE PATIENT")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #00a2ed;")
        
        # Bouton de fermeture (croix)
        self.btn_close = QPushButton("✕")
        self.btn_close.setObjectName("PatientInfoCloseBtn")
        self.btn_close.setFixedSize(20, 20)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        # Connexion directe à la méthode de masquage
        self.btn_close.clicked.connect(self.hide_panel)
        
        header_layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignLeft)
        header_layout.addWidget(self.btn_close, alignment=Qt.AlignmentFlag.AlignRight)
        self.layout.addLayout(header_layout)
        
        # --- LABELS D'INFORMATION ---
        self.lbl_id = self._create_info_row("ID Interne :")
        self.lbl_num = self._create_info_row("N° Patient :")
        self.lbl_nom = self._create_info_row("Nom :")
        self.lbl_prenom = self._create_info_row("Prénom :")
        self.lbl_ddn = self._create_info_row("Né(e) le :")
        self.lbl_sexe = self._create_info_row("Sexe :")
        
        self.hide()

    def _create_info_row(self, prefix: str) -> QLabel:
        row = QVBoxLayout()
        row.setSpacing(2)
        
        title = QLabel(prefix)
        title.setStyleSheet("font-size: 10px; color: #888888; text-transform: uppercase;")
        
        value = QLabel("-")
        value.setStyleSheet("font-size: 12px; font-weight: bold; color: #ffffff;")
        value.setWordWrap(True)
        
        row.addWidget(title)
        row.addWidget(value)
        self.layout.addLayout(row)
        return value

    def display_patient(self, patient_tuple: tuple | None):
        """Met à jour les textes du panneau et l'affiche."""
        if not patient_tuple:
            self.hide()
            return
            
        self.lbl_id.setText(str(patient_tuple[0]))
        self.lbl_nom.setText(str(patient_tuple[1]).upper())
        self.lbl_prenom.setText(str(patient_tuple[2]))
        self.lbl_ddn.setText(str(patient_tuple[3]) if patient_tuple[3] else "Non renseignée")
        self.lbl_sexe.setText(str(patient_tuple[4]) if patient_tuple[4] else "Non renseigné")
        self.lbl_num.setText(str(patient_tuple[5]) if patient_tuple[5] else "-")
        
        self.show()

    def hide_panel(self):
        """Masque le panneau et désélectionne le patient dans la liste de gauche."""
        self.hide()
        # Sécurité : on nettoie la sélection graphique et l'ID courant du contrôleur
        if self.main_view and self.main_view.controller:
            self.main_view.controller._current_patient_id = None
            self.main_view.left_toolbar.patient_manager.patient_list.clearSelection()
            self.main_view.left_toolbar.patient_manager.image_list.clear()