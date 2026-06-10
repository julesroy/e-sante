#Ce fichier sert concretement a rien mais permet de voir ce que contient api.py qui est sur le serveur Oracle                                                                                                           
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from datetime import datetime
import os, shutil, hashlib

app = FastAPI()
IMAGES_DIR = "/home/ubuntu/esante/images"

# ---------------------------------------------------------------
# UPLOAD — reçoit un fichier et le sauvegarde dans IMAGES_DIR
# ---------------------------------------------------------------
@app.post("/upload")
async def upload(patient_id: int, file: UploadFile = File(...)):
    #Hash des dossiers des patients
    hash_patient = hashlib.sha256(str(patient_id).encode()).hexdigest()[:16]
    dossier = os.path.join(IMAGES_DIR, hash_patient)
    os.makedirs(dossier, exist_ok=True)
    #On ajout un timestamp unique a chaque fichier
    nom_original = os.path.basename(file.filename)
    nom_unique = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{nom_original}"
    chemin = os.path.join(dossier, nom_unique)
    with open(chemin, "wb") as f:
        shutil.copyfileobj(file.file, f)
    print(f"[API] Image sauvegardée")
    return {"chemin": chemin}

# ---------------------------------------------------------------
# DOWNLOAD — retourne un fichier depuis IMAGES_DIR
# ---------------------------------------------------------------
@app.get("/image")
async def get_image(chemin: str):
    if not chemin or not os.path.exists(chemin):
        raise HTTPException(status_code=404, detail="Fichier introuvable")
    return FileResponse(chemin)

# ---------------------------------------------------------------
# DELETE — supprime un fichier du disque serveur
# ---------------------------------------------------------------
@app.delete("/image")
async def delete_image(chemin: str):
    if not chemin or not os.path.exists(chemin):
        raise HTTPException(status_code=404, detail="Fichier introuvable")
    os.remove(chemin)
    return {"message": f"Fichier supprimé : {chemin}"}