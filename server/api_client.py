import os
import requests
from dotenv import load_dotenv

load_dotenv()

# L'IP du serveur doit être dans le .env : SERVER_URL=http://X.X.X.X:5000
_HOST = os.getenv("DB_HOST", "localhost")
SERVER_URL = f"http://{_HOST}:5000"

# Timeout global pour toutes les requêtes (secondes)
_TIMEOUT = 10


def upload_image(file_path: str, patient_id:int) -> str | None:
    """
    Envoie un fichier local vers le serveur qui sera stocke dans le dossier d'un patient.
    Le nom du dossier est hashé.
    Params:
        file_path : chemin local du fichier à uploader (ex: "home/ubuntu/esante/images/hash_dossier/radio.png")
    """
    try:
        with open(file_path, "rb") as f:
            response = requests.post(
                f"{SERVER_URL}/upload",
                params={"patient_id": patient_id},
                files={"file": (os.path.basename(file_path), f)},
                timeout=_TIMEOUT,
            )
        response.raise_for_status()
        chemin_distant = response.json().get("chemin")
        print(f"[API Client] Upload OK -> {chemin_distant}")
        return chemin_distant

    except requests.exceptions.ConnectionError:
        print("[API Client] Serveur injoignable (upload)")
        return None
    except Exception as e:
        print(f"[API Client] Erreur upload : {e}")
        return None


def download_image(chemin_distant: str, destination_locale: str) -> bool:
    """
    Télécharge une image depuis le serveur et la sauvegarde localement.
    Retourne True si OK, False si échec.

    Params:
        chemin_distant    : chemin sur le serveur (stocké en BDD)
        destination_locale: chemin local où sauvegarder le fichier
    """
    try:
        response = requests.get(
            f"{SERVER_URL}/image",
            params={"chemin": chemin_distant},
            timeout=_TIMEOUT,
            stream=True,
        )
        response.raise_for_status()

        with open(destination_locale, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"[API Client] Download OK -> {destination_locale}")
        return True

    except requests.exceptions.ConnectionError:
        print("[API Client] Serveur injoignable (download)")
        return False
    except Exception as e:
        print(f"[API Client] Erreur download : {e}")
        return False


def delete_image(chemin_distant: str) -> bool:
    """
    Supprime un fichier sur le serveur.
    Retourne True si OK, False si échec.

    Params:
        chemin_distant : chemin sur le serveur (stocké en BDD)
    """
    try:
        response = requests.delete(
            f"{SERVER_URL}/image",
            params={"chemin": chemin_distant},
            timeout=_TIMEOUT,
        )
        response.raise_for_status()
        print(f"[API Client] Delete OK -> {chemin_distant}")
        return True

    except requests.exceptions.ConnectionError:
        print("[API Client] Serveur injoignable (delete)")
        return False
    except Exception as e:
        print(f"[API Client] Erreur delete : {e}")
        return False