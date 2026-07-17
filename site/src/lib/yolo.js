/**
 * yolo.js — inférence YOLOv11 100 % dans le navigateur (ONNX Runtime Web).
 *
 * Aucun serveur : le modèle best.onnx est téléchargé une fois puis exécuté
 * côté client. Pipeline identique à Ultralytics :
 *   letterbox 640×640  →  normalisation /255  →  run  →  décodage  →  NMS.
 *
 * Le modèle exporté produit un tenseur [1, 4+nc, 8400] :
 *   lignes 0..3 = cx, cy, w, h (en pixels sur l'entrée 640)
 *   lignes 4..  = score par classe (déjà entre 0 et 1)
 */
import * as ort from 'onnxruntime-web'

// Binaires WASM servis depuis un CDN : évite tout souci de bundling Vite.
ort.env.wasm.wasmPaths = 'https://cdn.jsdelivr.net/npm/onnxruntime-web@1.20.1/dist/'
// Un seul thread : pas besoin d'isolation cross-origin (COOP/COEP) côté hébergeur.
ort.env.wasm.numThreads = 1

const MODEL_URL = import.meta.env.BASE_URL + 'best.onnx'
const INPUT_SIZE = 640
const LABELS = ['drone'] // le modèle ne détecte qu'une classe

let session = null
let loading = null

/** Charge le modèle une seule fois (mis en cache par le navigateur ensuite). */
export function loadModel() {
  if (session) return Promise.resolve(session)
  if (loading) return loading
  loading = ort.InferenceSession
    .create(MODEL_URL, { executionProviders: ['wasm'], graphOptimizationLevel: 'all' })
    .then((s) => { session = s; return s })
  return loading
}

/** Redimensionne en gardant le ratio (letterbox gris 114) et renvoie le tenseur. */
function preprocess(img) {
  const w = img.naturalWidth || img.width
  const h = img.naturalHeight || img.height
  const scale = Math.min(INPUT_SIZE / w, INPUT_SIZE / h)
  const nw = Math.round(w * scale)
  const nh = Math.round(h * scale)
  const dw = (INPUT_SIZE - nw) / 2
  const dh = (INPUT_SIZE - nh) / 2

  const canvas = document.createElement('canvas')
  canvas.width = INPUT_SIZE
  canvas.height = INPUT_SIZE
  const ctx = canvas.getContext('2d')
  ctx.fillStyle = 'rgb(114,114,114)'
  ctx.fillRect(0, 0, INPUT_SIZE, INPUT_SIZE)
  ctx.drawImage(img, 0, 0, w, h, dw, dh, nw, nh)

  const { data } = ctx.getImageData(0, 0, INPUT_SIZE, INPUT_SIZE)
  const area = INPUT_SIZE * INPUT_SIZE
  const float = new Float32Array(3 * area) // format CHW, RGB, normalisé
  for (let i = 0; i < area; i++) {
    float[i] = data[i * 4] / 255            // R
    float[i + area] = data[i * 4 + 1] / 255 // G
    float[i + 2 * area] = data[i * 4 + 2] / 255 // B
  }
  const tensor = new ort.Tensor('float32', float, [1, 3, INPUT_SIZE, INPUT_SIZE])
  return { tensor, scale, dw, dh, ow: w, oh: h }
}

function iou(a, b) {
  const x1 = Math.max(a.x1, b.x1)
  const y1 = Math.max(a.y1, b.y1)
  const x2 = Math.min(a.x2, b.x2)
  const y2 = Math.min(a.y2, b.y2)
  const inter = Math.max(0, x2 - x1) * Math.max(0, y2 - y1)
  const areaA = (a.x2 - a.x1) * (a.y2 - a.y1)
  const areaB = (b.x2 - b.x1) * (b.y2 - b.y1)
  return inter / (areaA + areaB - inter)
}

/** Suppression des boîtes redondantes (Non-Maximum Suppression). */
function nms(boxes, iouThr) {
  boxes.sort((a, b) => b.score - a.score)
  const kept = []
  const dropped = new Array(boxes.length).fill(false)
  for (let i = 0; i < boxes.length; i++) {
    if (dropped[i]) continue
    kept.push(boxes[i])
    for (let j = i + 1; j < boxes.length; j++) {
      if (!dropped[j] && iou(boxes[i], boxes[j]) > iouThr) dropped[j] = true
    }
  }
  return kept
}

/**
 * Détecte les drones dans une image (HTMLImageElement).
 * @returns {Promise<Array<{x1,y1,x2,y2,score,label}>>} boîtes en coordonnées
 *          de l'image d'origine.
 */
export async function detect(img, confThr = 0.25, iouThr = 0.45) {
  const s = await loadModel()
  const { tensor, scale, dw, dh, ow, oh } = preprocess(img)

  const outputs = await s.run({ [s.inputNames[0]]: tensor })
  const out = outputs[s.outputNames[0]]
  const [, ch, na] = out.dims // [1, 4+nc, 8400]
  const d = out.data

  const boxes = []
  for (let i = 0; i < na; i++) {
    // Meilleure classe pour cette ancre
    let best = 0
    let bestC = 0
    for (let c = 4; c < ch; c++) {
      const v = d[c * na + i]
      if (v > best) { best = v; bestC = c - 4 }
    }
    if (best < confThr) continue

    const cx = d[i]
    const cy = d[na + i]
    const ww = d[2 * na + i]
    const hh = d[3 * na + i]

    // xywh (centre) → xyxy, puis retrait du letterbox → coords image d'origine
    let x1 = (cx - ww / 2 - dw) / scale
    let y1 = (cy - hh / 2 - dh) / scale
    let x2 = (cx + ww / 2 - dw) / scale
    let y2 = (cy + hh / 2 - dh) / scale

    // On borne aux limites de l'image
    x1 = Math.max(0, Math.min(ow, x1))
    y1 = Math.max(0, Math.min(oh, y1))
    x2 = Math.max(0, Math.min(ow, x2))
    y2 = Math.max(0, Math.min(oh, y2))

    boxes.push({ x1, y1, x2, y2, score: best, label: LABELS[bestC] || 'objet' })
  }

  return nms(boxes, iouThr)
}
