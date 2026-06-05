# ===== IMPORTS =====
import psycopg2
from dotenv import load_dotenv
import os

from database.connection import get_connection, is_online

# ==============================================================
# CRUD
# FONCTIONNEMENT GÉNÉRAL D'UNE REQUÊTE PSYCOPG2 :
#
#   1. get_connection()  -> ouvre une connexion au serveur PostgreSQL
#   2. conn.cursor()     -> crée un "curseur", c'est l'objet qui
#                           permet d'envoyer des requêtes SQL et de
#                           lire les résultats. Une connexion peut
#                           avoir plusieurs curseurs en parallèle.
#   3. cursor.execute()  -> envoie la requête SQL au serveur.
#                           Les %s sont des paramètres sécurisés
#                           (protection injection SQL), psycopg2
#                           les remplace proprement côté serveur.
#   4. cursor.fetchone() -> récupère UNE seule ligne de résultat
#      cursor.fetchall() -> récupère TOUTES les lignes de résultat
#   5. conn.commit()     -> valide la transaction (INSERT/UPDATE/
#                           DELETE). Sans commit, rien n'est sauvé.
#                           Pas besoin de commit pour un SELECT.
#   6. cursor.close()    -> libère le curseur
#      conn.close()      -> ferme la connexion à la BDD
# ==============================================================

# Charge les variables du fichier .env
load_dotenv()


def init_db():
    """
    Crée les tables si elles n'existent pas déjà.
    Appelée une seule fois au démarrage de l'application dans main.py
    Le IF NOT EXISTS garantit qu'on ne recrée pas les tables à chaque lancement.
    """
    conn = get_connection()
    # Guard hors-ligne — pas besoin d'init si pas de BDD
    if conn is None:
        print("[DB] Hors-ligne. Veuillez vous connecter à Internet pour utiliser toutes les fonctionnalités.")
        return

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
    print("[DB] Base de donnée initialisée")


def test_connexion():
    """
    Teste la connexion à la BDD et affiche le résultat.
    Utilise get_connection() de connection.py pour mettre à jour DB_MODE.
    """
    conn = get_connection()
    if conn:
        print("[DB] Connexion BDD OK")
        conn.close()
    else:
        print("[DB] Hors-ligne")
