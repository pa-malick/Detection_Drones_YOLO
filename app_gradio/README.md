---
title: Détection de Drones YOLOv11
emoji: 🛸
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: mit
---

# Détection de drones militaires — YOLOv11

Démo interactive du projet de Computer Vision. Déposez une image, le modèle
YOLOv11s entoure les drones détectés.

**Test :** Precision 0.93 · Recall 0.81 · mAP@50 0.86 · mAP@50-95 0.54.

## Déployer sur Hugging Face Spaces

1. Crée un Space : https://huggingface.co/new-space → SDK **Gradio**.
2. Copie `best.pt` du dossier `../modele/` dans **ce** dossier `app_gradio/`.
3. Envoie les 3 fichiers à la racine du Space :
   ```bash
   cp ../modele/best.pt .
   git lfs install
   git lfs track "*.pt"
   git add .gitattributes app.py requirements.txt best.pt README.md
   git commit -m "Démo détection de drones YOLOv11"
   git push
   ```
   (`best.pt` fait ~19 Mo → **Git LFS obligatoire**, d'où le `git lfs track`.)

## Lancer en local

```bash
cp ../modele/best.pt .
pip install -r requirements.txt
python app.py
```

## Images d'exemple (facultatif)

Dépose quelques images dans `examples/` : elles apparaîtront comme exemples
cliquables dans la démo.
