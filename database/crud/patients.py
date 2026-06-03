# ===== IMPORTS =====
from database.db import get_connection

# ===================================================
# TABLE DES PATIENTS
# ===================================================

def creer_patient(nom: str, prenom: str, date_naissance: str | None, sexe: str | None, numero_patient: str | None) -> int | None:
    """
    Insère un nouveau patient dans la BDD.
    Retourne l'id du patient crée.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO patients (nom, prenom, date_naissance, sexe, numero_patient)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """, (nom, prenom, date_naissance, sexe, numero_patient))

    row = cursor.fetchone()
    patient_id = row[0] if row else None
    conn.commit()
    cursor.close()
    conn.close()

    return patient_id


def rechercher_patient(query: str) -> list | None:
    """
    Recherche des patients par nom ou prénom (recherche partielle).
    Retourne une liste de tuples (id, nom, prenom, date_naissance, sexe, numero_patient).
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nom, prenom, date_naissance, sexe, numero_patient
        FROM patients
        WHERE LOWER(nom) LIKE LOWER(%s) OR LOWER(prenom) LIKE LOWER(%s)
        ORDER BY nom, prenom
    """, (f"%{query}%", f"%{query}%"))

    patients = cursor.fetchall()
    cursor.close()
    conn.close()
    return patients or []


def get_tous_les_patients() -> list | None:
    """
    Retourne tous les patients de la BDD.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nom, prenom, date_naissance, sexe, numero_patient
        FROM patients
        ORDER BY nom, prenom
    """)

    patients = cursor.fetchall()
    cursor.close()
    conn.close()
    return patients or []


def supprimer_patient(patient_id: int) -> None:
    """
    Efface toutes les informations d'un patient à partir de son identifiant patient.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM patients WHERE id = %s", (patient_id,))
    conn.commit()
    cursor.close()
    conn.close()
