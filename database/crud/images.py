# ===== IMPORTS =====
from database.db import get_connection

# ===================================================
# TABLE DES IMAGES
# ===================================================

def sauvegarder_image(patient_id: int, nom_fichier: str, chemin: str, modalite: str | None = None) -> int | None:
    """
    Enregistre une image liée à un patient en BDD.
    Retourne l'id de l'image créée, ou None si l'insertion échoue.

    Params:
        patient_id  : id du patient auquel appartient l'image
        nom_fichier : nom du fichier (ex: "radio_poumon.png")
        chemin      : chemin absolu sur le disque (ex: "C:/images/...")
        modalite    : type d'imagerie optionnel (ex: "IRM", "Scanner")
    """
    conn = get_connection()
    cursor = conn.cursor()

    # RETURNING id demande à PostgreSQL de nous renvoyer l'id auto-généré juste après l'insertion
    cursor.execute("""
        INSERT INTO images (patient_id, nom_fichier, chemin, modalite)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (patient_id, nom_fichier, chemin, modalite))

    row = cursor.fetchone()  # Récupère la ligne (id,) renvoyée par RETURNING

    conn.commit()    # Valide l'INSERT en base
    cursor.close()
    conn.close()

    return row[0] if row else None


def get_images_patient(patient_id: int) -> list:
    """
    Retourne toutes les images d'un patient, triées de la plus récente.
    Chaque élément = tuple (id, nom_fichier, chemin, modalite, created_at)
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nom_fichier, chemin, modalite, created_at
        FROM images
        WHERE patient_id = %s
        ORDER BY created_at DESC
    """, (patient_id,))

    images = cursor.fetchall()  # Liste de tuples, vide [] si aucun résultat

    # Pas de commit nécessaire : un SELECT ne modifie pas la BDD
    cursor.close()
    conn.close()

    return images


def supprimer_image(image_id: int) -> None:
    """Supprime une image par son id."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM images WHERE id = %s", (image_id,))

    conn.commit()
    cursor.close()
    conn.close()