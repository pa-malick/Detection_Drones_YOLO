# -*- coding: utf-8 -*-
"""
Extrait des images depuis une ou plusieurs videos (etape de collecte, Projet 1).

Interet : une seule video de drone te donne des dizaines d'images sous des angles et
distances varies. C'est le moyen le plus rapide de constituer un dataset diversifie.

Ce qu'il fait :
  - prend une video (ou un dossier de videos)
  - garde une image toutes les N secondes (reglable)
  - evite les images quasi identiques grace a un hash perceptuel
  - enregistre le tout en JPG dans un dossier de sortie

Utilisation :
  python extraire_frames.py ma_video.mp4              # 1 image / seconde
  python extraire_frames.py mes_videos                # dossier entier
  python extraire_frames.py ma_video.mp4 --intervalle 2   # 1 image / 2 secondes
"""
import sys, argparse
from pathlib import Path
import cv2
from PIL import Image
import imagehash

SEUIL_DOUBLON = 4       # 0 = tres strict, plus grand = tolere des images plus proches


def extraire_video(chemin, sortie, intervalle_s, hashes):
    cap = cv2.VideoCapture(str(chemin))
    if not cap.isOpened():
        print("  impossible d'ouvrir :", chemin)
        return 0
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    pas = max(1, int(round(fps * intervalle_s)))   # nb de frames a sauter
    stem = chemin.stem.replace(" ", "_")

    idx, gardees = 0, 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if idx % pas == 0:
            # conversion BGR (OpenCV) -> RGB (PIL) pour le hash et la sauvegarde
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            im = Image.fromarray(rgb)
            h = imagehash.phash(im)
            if not any(abs(h - hh) <= SEUIL_DOUBLON for hh in hashes):
                hashes.append(h)
                gardees += 1
                nom = f"{stem}_frame{idx:06d}.jpg"
                im.save(sortie / nom, "JPEG", quality=92)
        idx += 1
    cap.release()
    print(f"  {chemin.name} : {gardees} images gardees ({idx} frames lues)")
    return gardees


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="fichier video OU dossier de videos")
    ap.add_argument("--intervalle", type=float, default=1.0,
                    help="secondes entre deux images gardees (defaut 1.0)")
    ap.add_argument("--sortie", default="frames_extraites", help="dossier de sortie")
    args = ap.parse_args()

    src = Path(args.source)
    sortie = Path(args.sortie); sortie.mkdir(exist_ok=True)

    exts = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".m4v"}
    if src.is_dir():
        videos = sorted([p for p in src.rglob("*") if p.suffix.lower() in exts])
    elif src.is_file():
        videos = [src]
    else:
        print("Source introuvable :", src); return

    print(f"{len(videos)} video(s) a traiter, 1 image toutes les {args.intervalle}s")
    hashes, total = [], 0
    for v in videos:
        total += extraire_video(v, sortie, args.intervalle, hashes)

    print("\n--- Resultat ---")
    print("Images extraites :", total)
    print("Dossier de sortie:", sortie.resolve())
    print("Etape suivante   : ajoute ces images a ton dossier images_brutes, "
          "puis lance preparer_images.py")


if __name__ == "__main__":
    main()
