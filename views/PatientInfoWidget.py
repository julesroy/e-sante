from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt

class PatientInfoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(200) # Largeur fixe pour le panneau d'infos
        self.setObjectName("PatientInfoPanel")
        
        # Layout principal
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 15, 10, 15)
        self.layout.setSpacing(12)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Titre du panneau
        self.title_label = QLabel("📋 FICHE PATIENT")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #00a2ed;")
        self.layout.addWidget(self.title_label)
        
        # Initialisation des labels d'information
        self.lbl_id = self._create_info_row("ID Interne :")
        self.lbl_num = self._create_info_row("N° Patient :")
        self.lbl_nom = self._create_info_row("Nom :")
        self.lbl_prenom = self._create_info_row("Prénom :")
        self.lbl_ddn = self._create_info_row("Né(e) le :")
        self.lbl_sexe = self._create_info_row("Sexe :")
        
        # Masqué par défaut tant qu'aucun patient n'est sélectionné
        self.hide()

    def _create_info_row(self, prefix: str) -> QLabel:
        """Crée une ligne d'information propre et renvoie le QLabel de valeur."""
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
            
        # Tuple: (id, nom, prenom, ddn, sexe, numero_patient)
        self.lbl_id.setText(str(patient_tuple[0]))
        self.lbl_nom.setText(str(patient_tuple[1]).upper())
        self.lbl_prenom.setText(str(patient_tuple[2]))
        self.lbl_ddn.setText(str(patient_tuple[3]) if patient_tuple[3] else "Non renseignée")
        self.lbl_sexe.setText(str(patient_tuple[4]) if patient_tuple[4] else "Non renseigné")
        self.lbl_num.setText(str(patient_tuple[5]) if patient_tuple[5] else "-")
        
        self.show()