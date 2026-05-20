from PyQt6.QtWidgets import QFileDialog


class MainController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        # Connecte les signaux de l'interface aux fonctions du contrôleur
        self._connect_signals()

    def _connect_signals(self):
        # bouton d'upload
        self.view.btn_upload.clicked.connect(self.handle_upload)

    def handle_upload(self):
        """Gère la sélection du fichier et demande à la vue de l'afficher."""
        # explorateur de fichiers
        file_path, _ = QFileDialog.getOpenFileName(
            self.view,
            "Sélectionner une radiographie",
            "",
            "Images (*.png *.jpg *.jpeg)",
        )

        # Si image on l'affiche
        if file_path:
            self.view.display_medical_image(file_path)
