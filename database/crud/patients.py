# ===== IMPORTS =====
from database.db import get_connection

# ===================================================
# TABLE DES PATIENTS
# ===================================================


def creer_patient(nom: str, prenom: str, date_naissance: str | None, sexe: str | None, numero_patient: str | None) -> int | None:
    """
    Insère un nouveau patient dans la BDD.
    Retourne l'id du patient créé.
    """
    conn = get_connection()
    if conn is None:
        return None

    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO patients (nom, prenom, date_naissance, sexe, numero_patient)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """,
                    (nom, prenom, date_naissance, sexe, numero_patient),
                )
                row = cursor.fetchone()
                return row[0] if row else None
    except Exception as e:
        print(f"[DB Error] Erreur dans creer_patient : {e}")
        return None
    finally:
        conn.close()


def rechercher_patient(query: str) -> list:
    """
    Recherche des patients par nom ou prénom (recherche partielle).
    Retourne une liste de tuples (id, nom, prenom, date_naissance, sexe, numero_patient).
    """
    conn = get_connection()
    if conn is None:
        return []

    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, nom, prenom, date_naissance, sexe, numero_patient
                    FROM patients
                    WHERE LOWER(nom) LIKE LOWER(%s) OR LOWER(prenom) LIKE LOWER(%s)
                    ORDER BY nom, prenom
                """,
                    (f"%{query}%", f"%{query}%"),
                )
                patients = cursor.fetchall()
                return patients or []
    except Exception as e:
        print(f"[DB Error] Erreur dans rechercher_patient : {e}")
        return []
    finally:
        conn.close()


def get_tous_les_patients() -> list:
    """
    Retourne tous les patients de la BDD.
    """
    conn = get_connection()
    if conn is None:
        return []

    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, nom, prenom, date_naissance, sexe, numero_patient
                    FROM patients
                    ORDER BY nom, prenom
                """)
                patients = cursor.fetchall()
                return patients or []
    except Exception as e:
        print(f"[DB Error] Erreur dans get_tous_les_patients : {e}")
        return []
    finally:
        conn.close()


def supprimer_patient(patient_id: int) -> None:
    """
    Efface toutes les informations d'un patient à partir de son identifiant patient.
    """
    conn = get_connection()
    if conn is None:
        return

    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM patients WHERE id = %s", (patient_id,))
    except Exception as e:
        print(f"[DB Error] Erreur dans supprimer_patient : {e}")
    finally:
        conn.close()
