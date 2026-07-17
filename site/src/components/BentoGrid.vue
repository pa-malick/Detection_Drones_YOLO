<script setup>
/**
 * BentoGrid — grille asymétrique (verre dépoli) présentant le projet.
 * Cellules : métriques, l'histoire de la fuite de données, stack, méthodo,
 * et la démo live (inférence YOLOv11 100 % navigateur, composant DemoDetector).
 */
import DemoDetector from './DemoDetector.vue'

const GITHUB_URL = 'https://github.com/pa-malick/Detection_Drones_YOLO'

const metrics = [
  { label: 'Precision', value: '0.93' },
  { label: 'Recall', value: '0.81' },
  { label: 'mAP@50', value: '0.86' },
  { label: 'mAP@50-95', value: '0.54' },
]

const stack = ['YOLOv11', 'ONNX Runtime Web', 'Ultralytics', 'Roboflow', 'Python', 'Vue']
</script>

<template>
  <section id="projet" class="mx-auto max-w-6xl px-6 py-24 md:py-32">
    <!-- Intitulé de section -->
    <p class="mb-3 text-sm text-accent">// le projet</p>
    <h2 class="mb-6 max-w-2xl font-display text-3xl font-bold tracking-tightest md:text-5xl">
      De l'annotation à l'export ONNX, une chaîne complète.
    </h2>

    <!-- Métriques en ligne discrète (sous le titre) -->
    <div class="mb-16 flex flex-wrap items-baseline gap-x-6 gap-y-2 text-sm text-muted">
      <span v-for="(m, i) in metrics" :key="m.label" class="flex items-baseline gap-2">
        <span class="font-display font-bold text-accent">{{ m.value }}</span>
        <span>{{ m.label }}</span>
        <span v-if="i < metrics.length - 1" class="ml-4 text-white/15">·</span>
      </span>
    </div>

    <!-- Bento : 4 colonnes, cellules de tailles inégales -->
    <div class="grid grid-cols-2 gap-4 md:grid-cols-4">
      <!-- L'histoire de la fuite de données (l'argument signature) -->
      <div class="glass col-span-2 rounded-2xl p-6 transition-all duration-500 ease-out hover:-translate-y-1 hover:border-accent/40">
        <p class="mb-3 text-xs text-accent">// le vrai défi</p>
        <h3 class="mb-2 font-display text-xl font-bold">La fuite de données</h3>
        <p class="text-sm leading-relaxed text-muted">
          Des frames quasi identiques polluaient le jeu de test : le mAP@50 affichait
          un faux <span class="text-paper">0.976</span>. Après un découpage propre,
          le vrai chiffre est <span class="text-accent">0.86</span>.
        </p>
      </div>

      <!-- Démo live : inférence YOLOv11 100 % dans le navigateur -->
      <div class="glass col-span-2 row-span-2 flex min-h-[520px] flex-col rounded-2xl p-6 transition-all duration-500 ease-out hover:border-accent/40">
        <div class="mb-4 flex items-center justify-between">
          <div>
            <p class="text-xs text-accent">// démo live · dans ton navigateur</p>
            <h3 class="font-display text-xl font-bold">Teste le modèle</h3>
          </div>
          <span class="h-2 w-2 animate-pulse rounded-full bg-accent"></span>
        </div>
        <DemoDetector class="flex-1" />
      </div>

      <!-- Méthodologie -->
      <div class="glass col-span-2 rounded-2xl p-6 transition-all duration-500 ease-out hover:-translate-y-1 hover:border-accent/40">
        <p class="mb-3 text-xs text-accent">// méthodo</p>
        <p class="text-sm leading-relaxed text-muted">
          Transfert d'apprentissage depuis YOLOv11s pré-entraîné sur COCO. Optimiseur
          <span class="text-paper">SGD</span> avec warmup, backbone gelé
          (<span class="text-paper">freeze=10</span>) et augmentation géométrique
          allégée — pour spécialiser le modèle sans dégrader ses représentations,
          malgré un petit jeu de données.
        </p>
        <a
          :href="GITHUB_URL"
          target="_blank"
          class="mt-5 inline-flex items-center gap-2 text-sm text-accent transition-opacity hover:opacity-70"
        >Voir le code sur GitHub →</a>
      </div>
    </div>

    <!-- Stack technique en ligne discrète (sous le bento) -->
    <div class="mt-8 flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-muted">
      <span class="mr-2 text-accent">// stack</span>
      <template v-for="(tech, i) in stack" :key="tech">
        <span class="text-paper/80">{{ tech }}</span>
        <span v-if="i < stack.length - 1" class="text-white/15">·</span>
      </template>
    </div>
  </section>
</template>
