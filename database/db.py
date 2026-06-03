# ===== IMPORTS =====
import psycopg2
from dotenv import load_dotenv
import os

#Charge les variables du fichier .env
load_dotenv()

def get_connection():
    """
    Crée et retourne une connexion PostgreSQL
    Les credentials sont lus depuis le fichier .env à la racine du projet.
    À appeler à chaque fois qu'on a besoin d'interagir avec la BDD.
    """
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),          # IP du serveur Oracle
        port=os.getenv("DB_PORT"),          # 5432 par défaut
        dbname=os.getenv("DB_NAME"),        # esante
        user=os.getenv("DB_USER"),          # esante_user
        password=os.getenv("DB_PASSWORD")   # mdp
    )

def init_db():
    """
    Crée les tables si elles n'existent pas déjà.
    Appelée une seule fois au démarrage de l'application dans main.py
    Le IF NOT EXISTS garantit qu'on ne recrée pas les tables à chaque lancement.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Création de la table patients
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id              SERIAL PRIMARY KEY,
            nom             VARCHAR(100) NOT NULL,
            prenom          VARCHAR(100) NOT NULL,
            date_naissance  DATE,
            sexe            CHAR(1),                -- 'M' ou 'F'
            numero_patient  VARCHAR(50) UNIQUE,     -- identifiant hospitalier unique
            created_at      TIMESTAMP DEFAULT NOW()
        );
    """)

    # Création de la table images (liée à un patient)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id              SERIAL PRIMARY KEY,
            patient_id      INT REFERENCES patients(id) ON DELETE CASCADE,
            nom_fichier     VARCHAR(255) NOT NULL,  -- nom original du fichier
            chemin          TEXT NOT NULL,          -- chemin sur le disque du serveur
            modalite        VARCHAR(20),            -- 'CT', 'IRM', 'RX', 'PNG'...
            created_at      TIMESTAMP DEFAULT NOW()
        );
    """)

    # Validation des changements et fermeture propre
    conn.commit()
    cursor.close()
    conn.close()
    print("Base de donnée initialisée")

def test_connexion():
    """
    Teste la connexion à la BDD et affiche le résultat.
    Utile pendant le développement pour vérifier que le .env est correct.
    """
    try:
        conn = get_connection()
        print("Connexion BDD OK")
        conn.close()
    except Exception as e:
        print(f"Erreur de connexion : {e}")