#Ce fichier sert concretement a rien, il s'agit juste d'une copie du fichier existant sur le serveur Oracle.
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import os, shutil

app = FastAPI()
IMAGES_DIR = "/home/ubuntu/esante/images"

# ---------------------------------------------------------------
# UPLOAD — reçoit un fichier et le sauvegarde dans IMAGES_DIR
# ---------------------------------------------------------------
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    nom = os.path.basename(file.filename)
    chemin = os.path.join(IMAGES_DIR, nom)
    with open(chemin, "wb") as f:
        shutil.copyfileobj(file.file, f)
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