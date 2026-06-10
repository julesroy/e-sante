from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLineEdit, QListWidget, QListWidgetItem, QDialog, 
                             QLabel, QFormLayout, QComboBox, QMessageBox)
from PyQt6.QtCore import Qt

class PatientManagerWidget(QWidget):
    def __init__(self, main_view, parent=None):
        super().__init__(parent)
        self.main_view = main_view
        self.controller = None  # Lié dynamiquement dans le MainController
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)

        # 🔍 BARRE DE RECHERCHE
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Rechercher patient...")
        self.search_bar.textChanged.connect(self.on_search_changed)
        layout.addWidget(self.search_bar)

        # 👥 LISTE DES PATIENTS
        layout.addWidget(QLabel("Patients :"))
        self.patient_list = QListWidget()
        self.patient_list.itemSelectionChanged.connect(self.on_patient_selected)
        layout.addWidget(self.patient_list)

        # 🛠️ BOUTONS PATIENT
        btn_patient_layout = QHBoxLayout()
        self.btn_add_patient = QPushButton("Nouveau")
        self.btn_add_patient.clicked.connect(self.open_create_patient_dialog)
        self.btn_del_patient = QPushButton("Supprimer")
        self.btn_del_patient.clicked.connect(self.delete_selected_patient)
        
        btn_patient_layout.addWidget(self.btn_add_patient)
        btn_patient_layout.addWidget(self.btn_del_patient)
        layout.addLayout(btn_patient_layout)

        # 📷 LISTE DES IMAGES DU PATIENT SÉLECTIONNÉ
        layout.addWidget(QLabel("Radiographies :"))
        self.image_list = QListWidget()
        self.image_list.itemDoubleClicked.connect(self.on_image_double_clicked)
        layout.addWidget(self.image_list)

        # 🛠️ BOUTONS IMAGES
        btn_image_layout = QHBoxLayout()
        self.btn_upload_img = QPushButton("Importer")
        self.btn_upload_img.clicked.connect(self.upload_and_save_image)
        self.btn_del_img = QPushButton("Supprimer")
        self.btn_del_img.clicked.connect(self.delete_selected_image)
        
        btn_image_layout.addWidget(self.btn_upload_img)
        btn_image_layout.addWidget(self.btn_del_img)
        layout.addLayout(btn_image_layout)

    # ----------------------------------------------------------------     
    # LOGIQUE PATIENTS
    # ----------------------------------------------------------------     
    def refresh_results(self, patients_list):
        """Remplit la liste des patients à partir des tuples de la BDD."""
        self.patient_list.clear()
        self.image_list.clear()
        for p in patients_list:
            # Tuple: (id, nom, prenom, ddn, sexe, num)
            item = QListWidgetItem(f"{p[1].upper()} {p[2]} ({p[5]})")
            item.setData(Qt.ItemDataRole.UserRole, p[0])  # Stocke l'ID masqué
            self.patient_list.addItem(item)

    def on_search_changed(self, text):
        if self.main_view.controller:
            res = self.main_view.controller.patient_ctrl.handle_recherche_patient(text)
            self.refresh_results(res)

    def on_patient_selected(self):
        selected_items = self.patient_list.selectedItems()
        if not selected_items:
            self.main_view.controller._current_patient_id = None
            self.image_list.clear()
            # Masquer le volet si plus rien n'est sélectionné
            self.main_view.patient_info_panel.display_patient(None)
            return

        patient_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        self.main_view.controller._current_patient_id = patient_id
        
        if self.main_view.controller:
            # 1. On va chercher la liste complète de tous les patients en cache ou BDD
            # pour retrouver le tuple correspondant à notre ID
            tous_les_patients = self.main_view.controller.patient_ctrl.handle_charger_patients()
            patient_trouve = next((p for p in tous_les_patients if p[0] == patient_id), None)
            
            # 2. On transmet le tuple trouvé au panneau d'affichage à droite de la barre d'outils
            self.main_view.patient_info_panel.display_patient(patient_trouve)
            
            # 3. On charge les images normalement
            images = self.main_view.controller.image_ctrl.handle_charger_images_patient(patient_id)
            self.refresh_images(images)

    def open_create_patient_dialog(self):
        """Ouvre la boîte de dialogue pour créer un patient (Style déporté dans le QSS)."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Créer un Patient")
        
        # On donne un nom d'objet pour le cibler spécifiquement dans le fichier .qss
        dialog.setObjectName("PatientDialog")

        form_layout = QFormLayout(dialog)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(12)

        nom_input = QLineEdit()
        prenom_input = QLineEdit()
        ddn_input = QLineEdit()
        ddn_input.setPlaceholderText("AAAA-MM-JJ")
        
        sexe_input = QComboBox()
        sexe_input.addItems(["M", "F"])
        num_input = QLineEdit()

        form_layout.addRow("Nom :", nom_input)
        form_layout.addRow("Prénom :", prenom_input)
        form_layout.addRow("Date de naissance :", ddn_input)
        form_layout.addRow("Sexe :", sexe_input)
        form_layout.addRow("N° Patient :", num_input)

        btn_save = QPushButton("Enregistrer")
        form_layout.addWidget(btn_save)

        def save():
            if nom_input.text().strip() and prenom_input.text().strip():
                if self.main_view.controller:
                    p_id = self.main_view.controller.patient_ctrl.handle_nouveau_patient(
                        nom_input.text(), prenom_input.text(),
                        ddn_input.text() or None, sexe_input.currentText(), num_input.text() or None
                    )
                    if p_id:
                        self.refresh_results(self.main_view.controller.patient_ctrl.handle_charger_patients())
                dialog.accept()

        btn_save.clicked.connect(save)
        dialog.exec()
        
    def delete_selected_patient(self):
        selected_items = self.patient_list.selectedItems()
        if not selected_items:
            return
        
        item = selected_items[0]
        patient_id = item.data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(self, "Suppression", "Supprimer ce patient et TOUTES ses images en BDD ?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes and self.main_view.controller:
            if self.main_view.controller.patient_ctrl.handle_supprimer_patient(patient_id):
                self.refresh_results(self.main_view.controller.patient_ctrl.handle_charger_patients())
                self.main_view.patient_info_panel.display_patient(None)

    # ----------------------------------------------------------------     
    # LOGIQUE IMAGES
    # ----------------------------------------------------------------     
    def refresh_images(self, images_list):
        """Remplit la liste des images liées à un patient."""
        self.image_list.clear()
        for img in images_list:
            # Tuple: (id, nom_fichier, chemin, modalite, created_at)
            item = QListWidgetItem(f"📷 {img[1]}")
            item.setData(Qt.ItemDataRole.UserRole, img[0])  # ID unique Image
            item.setToolTip(img[2])                         # Cache le chemin d'accès local
            self.image_list.addItem(item)

    def upload_and_save_image(self):
        if self.main_view.controller:
            self.main_view.controller.image_ctrl.handle_upload_et_sauvegarder()
            p_id = self.main_view.controller._current_patient_id
            if p_id:
                self.refresh_images(self.main_view.controller.image_ctrl.handle_charger_images_patient(p_id))

    def on_image_double_clicked(self, item):
        chemin_disque = item.toolTip()
        if self.main_view.controller:
            self.main_view.controller.image_ctrl.handle_ouvrir_image_bdd(chemin_disque)

    def delete_selected_image(self):
        selected_items = self.image_list.selectedItems()
        if not selected_items:
            return
        
        item = selected_items[0]
        image_id = item.data(Qt.ItemDataRole.UserRole)
        chemin_serveur = item.toolTip()
        
        if self.main_view.controller:
            if self.main_view.controller.image_ctrl.handle_supprimer_image(image_id, chemin_serveur):
                p_id = self.main_view.controller._current_patient_id
                if p_id:
                    self.refresh_images(self.main_view.controller.image_ctrl.handle_charger_images_patient(p_id))