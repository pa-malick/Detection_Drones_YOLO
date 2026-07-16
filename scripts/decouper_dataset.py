# -*- coding: utf-8 -*-
"""
Prepare le jeu de donnees pour l'entrainement YOLO (a lancer APRES l'annotation).

Ce qu'il fait :
  - reprend l'export Roboflow (images 640x640 + labels au format YOLO)
  - refait le decoupage train / valid / test sans fuite de donnees
  - ajoute les images negatives (sans drone) a l'entrainement
  - ecrit dataset/ (structure YOLO + data.yaml) et dataset.zip pour Colab
  - ecrit split_audit.csv : d'ou vient chaque image et dans quel sous-ensemble

Pourquoi refaire le decoupage :
  Roboflow decoupe au hasard. Or 53 de mes images sont des frames prises dans 2 videos,
  espacees de 1 a 2 secondes. Le tirage au sort mettait donc en test des frames quasi
  identiques a des frames d'entrainement. Le modele les reconnaissait au lieu de generaliser,
  et les scores etaient trop beaux (mAP@50 de 0.976 au lieu de 0.884).

Les 3 regles du decoupage :
  1. toutes les frames d'une video restent en train (valid et test = photos independantes)
  2. les photos sont reparties par modele de drone, pour garder chaque sous-ensemble varie
  3. les drones qui n'ont qu'une seule photo restent en train (les tester n'aurait aucun sens)

Les negatifs :
  Une image negative = une image sans drone, avec un fichier de labels VIDE. Ca apprend au
  modele a ne rien detecter. Sans elles, il encadrait un navire ou une salle de controle.
  J'en mets 10 (8 % du jeu). A 25 (20 %), le modele devenait trop prudent : sa confiance sur
  un drone evident tombait de 0.98 a 0.38.

Utilisation :
  python decouper_dataset.py
"""
import csv, random, re, shutil, zipfile
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent   # le script vit dans scripts/
EXPORT = BASE / "annotations" / "export_roboflow_yolov11.zip"
NEGATIFS = BASE / "donnees" / "negatifs"
SOURCES = BASE / "donnees" / "images_propres.csv"
SORTIE = BASE / "dataset"

GRAINE = 42
PART_VALID = 0.20
PART_TEST = 0.20

# Les 10 negatifs gardes, un par erreur que le modele faisait vraiment.
NEGATIFS_GARDES = [
    "neg_navire_01.jpg", "neg_navire_02.jpg",          # il prenait le navire pour un drone
    "neg_salle_01.jpg", "neg_salle_02.jpg",            # fausse alerte sur la salle de controle
    "neg_avion_ligne_01.jpg", "neg_avion_ligne_02.jpg",  # confusion avion / drone
    "neg_chasseur_01.jpg",                             # la confusion la plus proche
    "neg_oiseau_02.jpg",                               # confusion oiseau / drone
    "neg_hangar_02.jpg", "neg_hangar_03.jpg",          # boites parasites dans les hangars
]


def modele_drone(origine):
    """Retrouve le modele de drone (ou la video) a partir du nom du fichier d'origine."""
    o = origine.upper()
    if "FRAME" in o:
        return "video_Triton" if "MQ4C" in o else "video_Reaper"
    for cle, nom in [("MQ4C", "MQ-4C"), ("TRITON", "MQ-4C"),
                     ("MQ-9", "MQ-9"), ("MQ9", "MQ-9"), ("REAPER", "MQ-9"),
                     ("MQ-1", "MQ-1"), ("MQ1", "MQ-1"), ("PREDATOR", "MQ-1"),
                     ("RQ4", "RQ-4"), ("GLOBALHAWK", "RQ-4"),
                     ("SCANEAGLE", "ScanEagle"), ("TANAN", "Tanan"), ("PERVIER", "Epervier")]:
        if cle in o:
            return nom
    return "autre"


def decouper(paires, origines):
    """Applique les 3 regles et rend un dictionnaire image -> train / valid / test."""
    tirage = random.Random(GRAINE)
    par_modele = defaultdict(list)
    for ident in paires:
        par_modele[modele_drone(origines[ident])].append(ident)

    choix = {}
    for modele, idents in sorted(par_modele.items()):
        idents = sorted(idents)
        tirage.shuffle(idents)

        # regles 1 et 3 : les frames video et les drones a photo unique restent en train
        if modele.startswith("video_") or len(idents) < 4:
            choix.update({i: "train" for i in idents})
            continue

        # regle 2 : on repartit les photos de ce modele entre les trois sous-ensembles
        n_test = max(1, round(len(idents) * PART_TEST))
        n_valid = max(1, round(len(idents) * PART_VALID))
        for i in idents[:n_test]:
            choix[i] = "test"
        for i in idents[n_test:n_test + n_valid]:
            choix[i] = "valid"
        for i in idents[n_test + n_valid:]:
            choix[i] = "train"
    return choix


def main():
    origines = {l["image"].replace(".jpg", ""): l["fichier_origine"]
                for l in csv.DictReader(open(SOURCES, encoding="utf-8"))}

    with zipfile.ZipFile(EXPORT) as z:
        # Roboflow renomme les fichiers : drone_0001_jpg.rf.<hash>.jpg
        paires = {}
        for nom in z.namelist():
            m = re.match(r"(?:train|valid|test)/images/(drone_\d+)_jpg\.rf\.\w+\.jpg$", nom)
            if m:
                paires[m.group(1)] = (nom, nom.replace("/images/", "/labels/").replace(".jpg", ".txt"))
        print(f"{len(paires)} images annotees dans l'export Roboflow")

        choix = decouper(paires, origines)

        if SORTIE.exists():
            shutil.rmtree(SORTIE)
        for s in ("train", "valid", "test"):
            (SORTIE / s / "images").mkdir(parents=True)
            (SORTIE / s / "labels").mkdir(parents=True)

        audit = []
        for ident, (img, lbl) in sorted(paires.items()):
            s = choix[ident]
            (SORTIE / s / "images" / f"{ident}.jpg").write_bytes(z.read(img))
            (SORTIE / s / "labels" / f"{ident}.txt").write_bytes(z.read(lbl))
            origine = origines[ident]
            audit.append([f"{ident}.jpg", s, modele_drone(origine),
                          "oui" if "frame" in origine.lower() else "non", origine])

    # les negatifs : 8 en train, 2 en valid, jamais en test (le test doit rester comparable)
    negatifs = [NEGATIFS / n for n in NEGATIFS_GARDES]
    manquants = [p.name for p in negatifs if not p.exists()]
    if manquants:
        raise SystemExit(f"Images negatives introuvables : {manquants}")
    random.Random(GRAINE).shuffle(negatifs)
    for i, img in enumerate(negatifs):
        s = "valid" if i < 2 else "train"
        shutil.copy(img, SORTIE / s / "images" / img.name)
        (SORTIE / s / "labels" / f"{img.stem}.txt").write_text("", encoding="utf-8")  # label vide
        audit.append([img.name, s, "negatif", "non", img.name])

    (SORTIE / "data.yaml").write_text(
        "train: ../train/images\nval: ../valid/images\ntest: ../test/images\n\n"
        "nc: 1\nnames: ['drone-militaire']\n", encoding="utf-8")

    with open(BASE / "split_audit.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["image", "sous_ensemble", "modele", "issue_video", "fichier_origine"])
        w.writerows(audit)

    # controle : aucune frame video ne doit avoir atterri en valid ou en test
    fuites = [a for a in audit if a[1] in ("valid", "test") and a[3] == "oui"]
    if fuites:
        raise SystemExit(f"ECHEC : {len(fuites)} frames video hors du train")

    archive = BASE / "dataset.zip"
    if archive.exists():
        archive.unlink()
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(SORTIE.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(BASE))

    print("\n--- Resultat ---")
    print("Controle anti-fuite : aucune frame video en valid ni en test")
    for s in ("train", "valid", "test"):
        labels = list((SORTIE / s / "labels").glob("*.txt"))
        vides = [p for p in labels if not p.read_text().strip()]
        print(f"  {s:6s}: {len(labels):3d} images, dont {len(vides):2d} sans drone")
    print("\nRepartition par modele de drone :")
    for m in sorted({a[2] for a in audit}):
        c = Counter(a[1] for a in audit if a[2] == m)
        print(f"  {m:12s} train {c['train']:3d}  valid {c['valid']:2d}  test {c['test']:2d}")
    print(f"\nArchive pour Colab : {archive.name} ({archive.stat().st_size / 1e6:.1f} Mo)")
    print("Detail image par image : split_audit.csv")


if __name__ == "__main__":
    main()
