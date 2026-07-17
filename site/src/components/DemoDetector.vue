<script setup>
/**
 * DemoDetector — la démo interactive, entièrement dans le navigateur.
 * L'utilisateur dépose une image → YOLOv11 (ONNX) détecte les drones → on
 * dessine les boîtes sur un canvas. Aucun serveur.
 */
import { ref, onMounted } from 'vue'
import { loadModel, detect } from '../lib/yolo.js'

const ACCENT = '#C6F135'

const canvas = ref(null)        // zone de rendu (image + boîtes)
const conf = ref(0.25)          // seuil de confiance
const status = ref('init')      // init | loading | ready | detecting | done | error
const message = ref('')
const count = ref(0)
let currentImg = null           // dernière image chargée (pour re-détecter au slider)

// Précharge le modèle dès le montage : le premier essai est ainsi instantané.
onMounted(async () => {
  try {
    status.value = 'loading'
    message.value = 'Chargement du modèle (~38 Mo, une seule fois)…'
    await loadModel()
    status.value = 'ready'
    message.value = 'Dépose une image de drone pour lancer la détection.'
  } catch (e) {
    status.value = 'error'
    message.value = 'Impossible de charger le modèle : ' + e.message
  }
})

function onFile(e) {
  const file = e.target.files?.[0]
  if (file) loadImage(file)
}
function onDrop(e) {
  const file = e.dataTransfer.files?.[0]
  if (file && file.type.startsWith('image/')) loadImage(file)
}

function loadImage(file) {
  const img = new Image()
  img.onload = () => { currentImg = img; runDetection() }
  img.src = URL.createObjectURL(file)
}

async function runDetection() {
  if (!currentImg) return
  status.value = 'detecting'
  message.value = 'Analyse en cours…'
  try {
    const boxes = await detect(currentImg, conf.value)
    draw(currentImg, boxes)
    count.value = boxes.length
    status.value = 'done'
    message.value = boxes.length
      ? `${boxes.length} drone(s) détecté(s).`
      : 'Aucun drone détecté (baisse le seuil pour voir les détections incertaines).'
  } catch (e) {
    status.value = 'error'
    message.value = 'Erreur pendant la détection : ' + e.message
  }
}

/** Dessine l'image (ajustée à la largeur du canvas) + les boîtes en accent. */
function draw(img, boxes) {
  const cv = canvas.value
  const maxW = cv.parentElement.clientWidth
  const scale = maxW / img.naturalWidth
  cv.width = maxW
  cv.height = img.naturalHeight * scale

  const ctx = cv.getContext('2d')
  ctx.drawImage(img, 0, 0, cv.width, cv.height)

  ctx.lineWidth = Math.max(2, cv.width * 0.004)
  ctx.strokeStyle = ACCENT
  ctx.fillStyle = ACCENT
  ctx.font = `${Math.max(12, cv.width * 0.02)}px 'JetBrains Mono', monospace`

  for (const b of boxes) {
    const x = b.x1 * scale
    const y = b.y1 * scale
    const w = (b.x2 - b.x1) * scale
    const h = (b.y2 - b.y1) * scale
    ctx.strokeRect(x, y, w, h)
    const tag = `${b.label} ${(b.score * 100).toFixed(0)}%`
    const tw = ctx.measureText(tag).width + 10
    const th = parseInt(ctx.font) + 6
    ctx.fillRect(x, Math.max(0, y - th), tw, th)
    ctx.fillStyle = '#020617'
    ctx.fillText(tag, x + 5, Math.max(th - 6, y - 6))
    ctx.fillStyle = ACCENT
  }
}
</script>

<template>
  <div class="flex h-full flex-col">
    <!-- Zone de dépôt / résultat -->
    <div
      class="relative flex flex-1 items-center justify-center overflow-hidden rounded-xl border border-dashed border-white/15 bg-black/20 transition-colors duration-300 hover:border-accent/50"
      @dragover.prevent
      @drop.prevent="onDrop"
    >
      <canvas ref="canvas" class="max-h-full max-w-full"></canvas>

      <!-- Overlay quand aucune image n'est encore chargée -->
      <label
        v-if="status !== 'done' && status !== 'detecting'"
        class="absolute inset-0 flex cursor-pointer flex-col items-center justify-center gap-3 p-6 text-center"
      >
        <span class="text-3xl">🛸</span>
        <span class="text-sm text-muted">{{ message }}</span>
        <span v-if="status === 'ready'" class="rounded-full border border-accent px-4 py-1 text-xs text-accent">
          Choisir une image
        </span>
        <span v-if="status === 'loading'" class="text-xs text-accent">⏳ patiente…</span>
        <input type="file" accept="image/*" class="hidden" @change="onFile" :disabled="status === 'loading'" />
      </label>
    </div>

    <!-- Contrôles -->
    <div class="mt-4 flex flex-wrap items-center gap-4">
      <label class="flex min-w-[180px] flex-1 items-center gap-3 text-xs text-muted">
        Seuil
        <input
          type="range" min="0.05" max="0.9" step="0.05"
          v-model.number="conf" @change="runDetection"
          class="flex-1 accent-accent"
        />
        <span class="w-8 text-accent">{{ conf.toFixed(2) }}</span>
      </label>
      <label class="cursor-pointer rounded-full border border-white/15 px-4 py-1 text-xs transition-colors hover:border-accent hover:text-accent">
        Changer d'image
        <input type="file" accept="image/*" class="hidden" @change="onFile" />
      </label>
    </div>

    <p v-if="status === 'done'" class="mt-3 text-xs text-muted">{{ message }}</p>
  </div>
</template>
