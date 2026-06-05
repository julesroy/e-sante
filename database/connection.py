# ============================================================
# Gestion de la connexion à la base de données.
# Tente une connexion PostgreSQL au démarrage.
# Si échec -> mode hors-ligne (DB_MODE = "offline").
# ============================================================

import os
from dotenv import load_dotenv

# Chargement des variables d'environnement (.env)
load_dotenv()

# Mode global : "online" si connecté, "offline" sinon
# Initialisé à "offline", mis à jour par get_connection()
DB_MODE = "offline"


def get_connection():
    """
    Tente d'établir une connexion PostgreSQL.
    - Timeout de 3 secondes pour ne pas bloquer l'UI au démarrage.
    - Si succès  → DB_MODE = "online", retourne la connexion.
    - Si échec   → DB_MODE = "offline", retourne None.
    """
    global DB_MODE

    # TEST HORS-LIGNE — décommenter pour simuler le mode offline
    DB_MODE = "offline"
    return None

    try:
        import psycopg2

        # Lecture des variables séparées
        host = os.getenv("DB_HOST")
        port = os.getenv("DB_PORT")
        dbname = os.getenv("DB_NAME")
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")

        # Vérifie que les variables essentielles sont présentes
        if not all([host, dbname, user, password]):
            print("[DB] Variables .env manquantes (DB_HOST/DB_NAME/DB_USER/DB_PASSWORD) -> hors-ligne")
            DB_MODE = "offline"
            return None

        conn = psycopg2.connect(host=host, port=port, dbname=dbname, user=user, password=password, connect_timeout=10)
        DB_MODE = "online"
        print("[DB] Connexion PostgreSQL réussie")
        return conn

    except Exception as e:
        DB_MODE = "offline"
        print(f"[DB] Connexion impossible -> mode hors-ligne ({e})")
        return None


def is_online() -> bool:
    """
    Retourne True si la BDD est accessible, False sinon.
    À appeler dans les controllers avant toute opération BDD.
    """
    return DB_MODE == "online"


def check_connection() -> bool:
    """
    Teste activement la connexion.
    Remet à jour DB_MODE et retourne le nouvel état.
    """
    conn = get_connection()
    if conn:
        conn.close()
        return True
    return False
