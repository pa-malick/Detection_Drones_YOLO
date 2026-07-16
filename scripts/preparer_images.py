# -*- coding: utf-8 -*-
"""
Outil de preparation des images de drones (a lancer sur ton PC, AVANT l'annotation).

Ce qu'il fait :
  - lit toutes les images d'un dossier "brutes"
  - ignore les fichiers illisibles et les images trop petites
  - repere et ecarte les doublons (meme image en double)
  - convertit tout en JPG propre et renomme en drone_0001.jpg, drone_0002.jpg, ...
  - copie le resultat dans un dossier propre, pret pour Label Studio
  - genere un fichier sources.csv ou tu notes d'ou vient chaque image (obligatoire pour le rapport)

Utilisation :
  1. Mets toutes tes images collectees dans un dossier, par exemple :  images_brutes
  2. Lance :   python preparer_images.py images_brutes
  3. Recupere le dossier "images_propres" et le fichier "sources.csv"
"""
import sys, csv
from pathlib import Path
from PIL import Image
import imagehash

MIN_COTE = 128          # on jette les images dont le plus petit cote est sous 128 px
SEUIL_DOUBLON = 3       # plus le chiffre est petit, plus la detection de doublon est stricte


def preparer(dossier_brut, dossier_propre="images_propres", csv_sources="sources.csv"):
    brut = Path(dossier_brut)
    if not brut.is_dir():
        print("Dossier introuvable :", brut)
        return

    propre = Path(dossier_propre)
    propre.mkdir(exist_ok=True)

    exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}
    fichiers = sorted([p for p in brut.rglob("*") if p.suffix.lower() in exts])
    print(f"{len(fichiers)} fichiers image trouves dans {brut}")

    hashes = []
    lignes_csv = []
    compteur = 0
    rejets = {"illisible": 0, "trop_petite": 0, "doublon": 0}

    for f in fichiers:
        try:
            im = Image.open(f).convert("RGB")
        except Exception:
            rejets["illisible"] += 1
            continue

        if min(im.size) < MIN_COTE:
            rejets["trop_petite"] += 1
            continue

        h = imagehash.phash(im)
        if any(abs(h - hh) <= SEUIL_DOUBLON for hh in hashes):
            rejets["doublon"] += 1
            continue
        hashes.append(h)

        compteur += 1
        nouveau_nom = f"drone_{compteur:04d}.jpg"
        im.save(propre / nouveau_nom, "JPEG", quality=92)
        # la colonne "source" est a remplir par toi (site, auteur, lien, licence)
        lignes_csv.append([nouveau_nom, f.name, "", ""])

    with open(csv_sources, "w", newline="", encoding="utf-8") as fcsv:
        w = csv.writer(fcsv)
        w.writerow(["image", "fichier_origine", "source_lien", "licence"])
        w.writerows(lignes_csv)

    print("\n--- Resultat ---")
    print("Images gardees   :", compteur)
    print("Rejets           :", rejets)
    print("Dossier propre   :", propre.resolve())
    print("Tableau sources  :", Path(csv_sources).resolve(), "(a completer)")


if __name__ == "__main__":
    dossier = sys.argv[1] if len(sys.argv) > 1 else "images_brutes"
    preparer(dossier)
