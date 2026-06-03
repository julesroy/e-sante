# ===== IMPORTS PYTHON STANDARD =====
from __future__ import annotations

# ===== IMPORTS UNIQUEMENT POUR PYLANCE (jamais exécutés) =====
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from views.MainView import MainView
    from controllers.ErrorController import ErrorController

# ===== IMPORTS DES CRUDS =====
from database.crud.patients import (
    creer_patient,
    get_tous_les_patients,
    rechercher_patient,
    supprimer_patient,
)

class PatientController:
    #Attributs pour Pylance
    view: MainView
    error_handler: ErrorController

    # ---------------------------------------------------------------
    # CRÉER UN PATIENT
    # ---------------------------------------------------------------
    def handle_nouveau_patient(self, nom: str, prenom: str, date_naissance: str | None = None, sexe: str | None = None, numero_patient: str | None = None,) -> int | None:
        """
        Insère un nouveau patient en BDD.
        Retourne son id, ou None si l'insertion échoue.
        Appelé depuis le formulaire de création dans la View.
        """
        try:
            if not nom.strip() or not prenom.strip():
                self.error_handler.show_error(
                    "Champs manquants",
                    "Le nom et le prénom sont obligatoires."
                )
                return None

            patient_id = creer_patient(nom.strip(), prenom.strip(), date_naissance, sexe, numero_patient)
            print(f"[PatientController] Patient créé -> id={patient_id}")
            return patient_id

        except Exception as e:
            self.error_handler.handle_exception(e)
            return None

    # ---------------------------------------------------------------
    # CHARGER TOUS LES PATIENTS
    # ---------------------------------------------------------------
    def handle_charger_patients(self) -> list:
        """
        Récupère tous les patients depuis la BDD.
        Retourne une liste de tuples :
        (id, nom, prenom, date_naissance, sexe, numero_patient)
        Appelé au démarrage ou après une modification pour rafraîchir la liste.
        """
        try:
            patients = get_tous_les_patients()
            patients = patients or []
            print(f"[PatientController] {len(patients)} patient(s) chargé(s)")
            return patients

        except Exception as e:
            self.error_handler.handle_exception(e)
            return []

    # ---------------------------------------------------------------
    # RECHERCHER DES PATIENTS
    # ---------------------------------------------------------------
    def handle_recherche_patient(self, query: str) -> list:
        """
        Recherche des patients par nom ou prénom (recherche partielle).
        Retourne la liste filtrée de tuples patients.
        Appelé à chaque frappe dans la barre de recherche.
        """
        try:
            if not query.strip():
                # Champ vide -> on retourne tous les patients
                resultats = get_tous_les_patients()
            else:
                resultats = rechercher_patient(query.strip())

            # On garantit explicitement une list, jamais None
            resultats = resultats if resultats is not None else []

            print(f"[PatientController] Recherche '{query}' → {len(resultats)} résultat(s)")
            return resultats

        except Exception as e:
            self.error_handler.handle_exception(e)
            return []
        
    # ---------------------------------------------------------------
    # SUPPRIMER UN PATIENT
    # ---------------------------------------------------------------
    def handle_supprimer_patient(self, patient_id: int) -> bool:
        """
        Supprime un patient et toutes ses images (CASCADE BDD).
        Retourne True si OK, False si erreur.
        Appelé depuis le bouton Supprimer dans la View.
        """
        try:
            supprimer_patient(patient_id)
            print(f"[PatientController] Patient id={patient_id} supprimé")
            return True

        except Exception as e:
            self.error_handler.handle_exception(e)
            return False