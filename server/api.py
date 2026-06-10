from flask import Flask, request, send_file, jsonify
import os

app = Flask(__name__)
IMAGES_DIR = "/home/ubuntu/esante/images"

# ---------------------------------------------------------------
# UPLOAD — reçoit un fichier et le sauvegarde dans IMAGES_DIR
# ---------------------------------------------------------------
@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"erreur": "Aucun fichier reçu"}), 400

    f = request.files["file"]
    nom = os.path.basename(f.filename)
    chemin = os.path.join(IMAGES_DIR, nom)
    f.save(chemin)
    print(f"[API] Image sauvegardée : {chemin}")
    return jsonify({"chemin": chemin})

# ---------------------------------------------------------------
# DOWNLOAD — retourne un fichier depuis IMAGES_DIR
# ---------------------------------------------------------------
@app.route("/image", methods=["GET"])
def get_image():
    chemin = request.args.get("chemin")
    if not chemin or not os.path.exists(chemin):
        return jsonify({"erreur": "Fichier introuvable"}), 404
    return send_file(chemin)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)