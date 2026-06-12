# tests/test_db.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.crud.patients import (
    creer_patient,
    get_tous_les_patients,
    rechercher_patient,
    supprimer_patient,
)
from database.crud.images import (
    sauvegarder_image,
    get_images_patient,
)

def sep(titre: str):
    print(f"\n{'='*40}")
    print(f"  {titre}")
    print('='*40)

# -------------------------------------------------------
# INSERT patient
# -------------------------------------------------------
sep("Création patient")
pid = creer_patient("Durand", "TestPrenom", "2005-07-01", "M", "TEST_001")
print(f"✅ Patient créé -> id={pid}")
assert pid is not None, "❌ creer_patient() a retourné None"

# -------------------------------------------------------
# SELECT tous
# -------------------------------------------------------
sep("Tous les patients")
patients = get_tous_les_patients()
assert patients is not None and len(patients) > 0, "❌ Aucun patient trouvé"
for p in patients:
    marker = " ← TEST" if p[0] == pid else ""
    print(f"  id={p[0]} | {p[1]} {p[2]} | {p[3]} | {p[4]} | num={p[5]}{marker}")

# -------------------------------------------------------
# RECHERCHE
# -------------------------------------------------------
sep("Recherche 'Durand'")
resultats = rechercher_patient("Durand")
assert resultats is not None and any(r[0] == pid for r in resultats), \
    "❌ Le patient créé n'apparaît pas dans la recherche"
print(f"✅ {len(resultats)} résultat(s) trouvé(s)")
for r in resultats:
    print(f"  id={r[0]} | {r[1]} {r[2]}")

# -------------------------------------------------------
# SAUVEGARDE IMAGE
# -------------------------------------------------------
sep("Sauvegarde image")
iid = sauvegarder_image(pid, "radio_test.png", "/home/ubuntu/esante/images/radio_test.png", "RX")
print(f"✅ Image créée -> id={iid}")
assert iid is not None, "❌ sauvegarder_image() a retourné None"

images = get_images_patient(pid)
assert images is not None and len(images) == 1, f"❌ Attendu 1 image, trouvé {len(images) if images else 0}"
img = images[0]
print(f"  id={img[0]} | fichier={img[1]} | chemin={img[2]} | modalite={img[3]} | date={img[4]}")

# -------------------------------------------------------
# NETTOYAGE (CASCADE supprime aussi l'image)
# -------------------------------------------------------
sep("Nettoyage")
supprimer_patient(pid)
reste = get_images_patient(pid)
assert reste == [] or reste is None, "❌ Les images n'ont pas été supprimées par CASCADE"
print(f"✅ Patient id={pid} supprimé, images supprimées par CASCADE")

print("\n" + "="*40)
print("  RÉSULTAT : TOUS LES TESTS OK ✅")
print("="*40 + "\n")