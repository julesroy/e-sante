from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QObject, pyqtSignal
import traceback
import logging

# configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('error.log'),
        logging.StreamHandler()
    ]
)

class ErrorController(QObject):
    """Gestionnaire centralisé des erreurs avec popup"""
    error_occurred = pyqtSignal(str)  # signal pour les observateurs
    
    def __init__(self, parent_window=None):
        super().__init__()
        self.parent_window = parent_window
    
    def show_error(self, title: str, message: str, error_details: str = ""):
        """Affiche une popup d'erreur et la log"""
        # on log l'erreur
        full_message = f"{title}: {message}"
        if error_details:
            full_message += f"\n\nDétails: {error_details}"
        
        logging.error(full_message)
        
        # affiche la popup avec le message d'erreur
        QMessageBox.critical(
            self.parent_window,
            title,
            message,
            QMessageBox.StandardButton.Ok
        )
        
        # emet le signal
        self.error_occurred.emit(full_message)
    
    def show_warning(self, title: str, message: str):
        """Affiche un avertissement"""
        logging.warning(f"{title}: {message}")
        QMessageBox.warning(
            self.parent_window,
            title,
            message,
            QMessageBox.StandardButton.Ok
        )
    
    def handle_exception(self, exception: Exception):
        """Gère automatiquement une exception"""
        error_type = type(exception).__name__
        error_msg = str(exception)
        traceback_str = traceback.format_exc()
        
        self.show_error(
            f"Erreur: {error_type}",
            error_msg,
            traceback_str
        )