"""
Démo interactive — Détection de drones militaires (YOLOv11).

Projet Computer Vision de Papa Malick NDIAYE.
L'utilisateur dépose une image, le modèle entoure les drones détectés.

Lancement local :
    pip install -r requirements.txt
    python app.py

Sur Hugging Face Spaces : placer ce dossier (app.py, requirements.txt, best.pt)
à la racine d'un Space de type Gradio. Le fichier best.pt (~19 Mo) doit être
suivi par Git LFS.
"""

from pathlib import Path

import gradio as gr
from PIL import Image
from ultralytics import YOLO

# --- Chargement du modèle -------------------------------------------------
# best.pt est attendu dans ce dossier (copié depuis ../modele/best.pt).
MODEL_PATH = Path(__file__).parent / "best.pt"
if not MODEL_PATH.exists():
    # Repli : le modèle du projet, un niveau au-dessus.
    MODEL_PATH = Path(__file__).parent.parent / "modele" / "best.pt"

model = YOLO(str(MODEL_PATH))
CLASS_NAMES = model.names  # {0: 'drone', ...}


def detecter(image: Image.Image, seuil_confiance: float):
    """Lance la détection et renvoie l'image annotée + un récapitulatif texte."""
    if image is None:
        return None, "Déposez une image pour lancer la détection."

    resultats = model.predict(source=image, conf=seuil_confiance, verbose=False)
    r = resultats[0]

    # Image annotée (BGR -> RGB pour l'affichage)
    annotee = Image.fromarray(r.plot()[:, :, ::-1])

    n = len(r.boxes)
    if n == 0:
        resume = (
            f"Aucun drone détecté au seuil de confiance {seuil_confiance:.2f}.\n"
            "Astuce : baissez le seuil pour révéler les détections les moins sûres."
        )
    else:
        lignes = [f"{n} drone(s) détecté(s) :"]
        for i, box in enumerate(r.boxes, 1):
            cls = CLASS_NAMES[int(box.cls)]
            conf = float(box.conf)
            lignes.append(f"  {i}. {cls} — confiance {conf:.0%}")
        resume = "\n".join(lignes)

    return annotee, resume


# --- Interface ------------------------------------------------------------
DESCRIPTION = """
# 🛸 Détection de drones militaires — YOLOv11

Modèle **YOLOv11s** ré-entraîné par transfert d'apprentissage sur un jeu de drones
militaires annoté à la main.

**Résultats sur le jeu de test :** Precision 0.93 · Recall 0.81 · mAP@50 0.86 · mAP@50-95 0.54.

Déposez une image ci-dessous, ajustez le seuil de confiance, et le modèle entoure les drones.
"""

ARTICLE = """
---
**À propos du projet.** Chaîne complète : collecte et annotation (Roboflow), entraînement,
évaluation et export ONNX. Deux difficultés réelles ont été traitées : une **fuite de données**
(des frames vidéo quasi identiques se retrouvaient à la fois en entraînement et en test, gonflant
le mAP@50 à un faux 0.976 ; le vrai chiffre après correction est 0.86) et des **faux positifs**
corrigés par l'ajout d'images négatives.

Projet réalisé par **Papa Malick NDIAYE** — Master 2 Data Science.
"""

exemples_dir = Path(__file__).parent / "examples"
exemples = sorted(str(p) for p in exemples_dir.glob("*") if p.suffix.lower() in {".jpg", ".jpeg", ".png"})

with gr.Blocks(title="Détection de drones — YOLOv11") as demo:
    gr.Markdown(DESCRIPTION)
    with gr.Row():
        with gr.Column():
            entree = gr.Image(type="pil", label="Image à analyser")
            seuil = gr.Slider(0.05, 0.95, value=0.25, step=0.05,
                              label="Seuil de confiance")
            bouton = gr.Button("Détecter les drones", variant="primary")
            if exemples:
                gr.Examples(examples=[[e] for e in exemples], inputs=entree,
                            label="Exemples")
        with gr.Column():
            sortie_img = gr.Image(type="pil", label="Détections")
            sortie_txt = gr.Textbox(label="Récapitulatif", lines=6)

    bouton.click(detecter, inputs=[entree, seuil], outputs=[sortie_img, sortie_txt])
    entree.change(detecter, inputs=[entree, seuil], outputs=[sortie_img, sortie_txt])
    gr.Markdown(ARTICLE)


if __name__ == "__main__":
    demo.launch()
