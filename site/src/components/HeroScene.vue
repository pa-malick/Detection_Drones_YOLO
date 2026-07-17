<script setup>
/**
 * HeroScene — l'objet 3D central du hero.
 *
 * Concept « Le Scanner » : un icosaèdre en wireframe entouré d'un nuage de
 * points. Il tourne lentement, suit la souris (parallax lissé), et se
 * « désassemble » quand on scrolle (les points s'écartent) — métaphore de la
 * vision qui analyse une scène.
 *
 * Performance :
 *  - une seule géométrie, réutilisée pour le wireframe et les points ;
 *  - boucle requestAnimationFrame unique, arrêtée et nettoyée au démontage ;
 *  - pixelRatio plafonné à 2.
 *
 * Accessibilité / responsive :
 *  - si WebGL est absent, si l'écran est petit, ou si l'utilisateur préfère
 *    les mouvements réduits → on n'initialise PAS Three.js et on affiche un
 *    fallback CSS (dégradé mesh animé). Le site reste fluide partout.
 */
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as THREE from 'three'

const container = ref(null)   // div qui reçoit le <canvas>
const use3D = ref(true)       // bascule vers le fallback CSS si false

// Variables de scène gardées hors du render Vue (pas besoin de réactivité).
let renderer, scene, camera, group, points, frameId
let basePositions = null      // positions d'origine des points
const mouse = { x: 0, y: 0 }        // cible (souris normalisée)
const rot = { x: 0, y: 0 }          // rotation lissée courante
let dispersion = 0                  // 0 = compact, 1 = éclaté (piloté par le scroll)
let targetDispersion = 0

/** Décide si l'appareil peut/doit afficher la 3D. */
function canRender3D() {
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  const smallScreen = window.matchMedia('(max-width: 767px)').matches
  let webgl = false
  try {
    const c = document.createElement('canvas')
    webgl = !!(c.getContext('webgl2') || c.getContext('webgl'))
  } catch (e) {
    webgl = false
  }
  return webgl && !reduced && !smallScreen
}

function initScene() {
  const el = container.value
  const w = el.clientWidth
  const h = el.clientHeight

  scene = new THREE.Scene()

  camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 100)
  camera.position.z = 6

  renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true })
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.setSize(w, h)
  el.appendChild(renderer.domElement)

  group = new THREE.Group()
  scene.add(group)

  // Géométrie de base (detail 3 = assez de sommets pour un joli nuage).
  const geometry = new THREE.IcosahedronGeometry(2.1, 3)

  // 1) Wireframe blanc discret : la « cage » de l'objet.
  const wire = new THREE.LineSegments(
    new THREE.WireframeGeometry(geometry),
    new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.12 }),
  )
  group.add(wire)

  // 2) Nuage de points en accent lime : la matière « scannée ».
  const pointsGeo = new THREE.BufferGeometry()
  basePositions = geometry.attributes.position.array.slice() // copie figée
  pointsGeo.setAttribute(
    'position',
    new THREE.BufferAttribute(basePositions.slice(), 3),
  )
  const pointsMat = new THREE.PointsMaterial({
    color: 0xc6f135,
    size: 0.045,
    sizeAttenuation: true,
    transparent: true,
    opacity: 0.9,
  })
  points = new THREE.Points(pointsGeo, pointsMat)
  group.add(points)

  window.addEventListener('pointermove', onPointerMove)
  window.addEventListener('scroll', onScroll, { passive: true })
  window.addEventListener('resize', onResize)

  animate()
}

/** Souris → cible de rotation, normalisée entre -1 et 1. */
function onPointerMove(e) {
  mouse.x = (e.clientX / window.innerWidth) * 2 - 1
  mouse.y = (e.clientY / window.innerHeight) * 2 - 1
}

/** Scroll dans le hero → niveau de dispersion des points (0 à 1). */
function onScroll() {
  const hero = container.value?.offsetHeight || window.innerHeight
  targetDispersion = Math.min(window.scrollY / hero, 1)
}

function onResize() {
  if (!renderer) return
  const el = container.value
  const w = el.clientWidth
  const h = el.clientHeight
  camera.aspect = w / h
  camera.updateProjectionMatrix()
  renderer.setSize(w, h)
}

/** Petit bruit déterministe (évite d'ajouter une dépendance). */
function noise(i, t) {
  return Math.sin(i * 12.9898 + t) * 0.5 + Math.cos(i * 78.233 - t) * 0.5
}

function animate() {
  frameId = requestAnimationFrame(animate)
  const t = performance.now() * 0.0004

  // Rotation lissée : lerp vers la cible souris + dérive lente continue.
  rot.y += ((mouse.x * 0.6 + t) - rot.y) * 0.05
  rot.x += ((mouse.y * 0.4) - rot.x) * 0.05
  group.rotation.y = rot.y
  group.rotation.x = rot.x

  // Dispersion lissée : les points s'écartent le long de leur normale.
  dispersion += (targetDispersion - dispersion) * 0.06
  const pos = points.geometry.attributes.position.array
  for (let i = 0; i < pos.length; i += 3) {
    const push = 1 + dispersion * (0.35 + 0.5 * noise(i, t * 6))
    pos[i] = basePositions[i] * push
    pos[i + 1] = basePositions[i + 1] * push
    pos[i + 2] = basePositions[i + 2] * push
  }
  points.geometry.attributes.position.needsUpdate = true

  renderer.render(scene, camera)
}

/** Libère toutes les ressources GPU et les écouteurs. */
function dispose() {
  cancelAnimationFrame(frameId)
  window.removeEventListener('pointermove', onPointerMove)
  window.removeEventListener('scroll', onScroll)
  window.removeEventListener('resize', onResize)
  if (renderer) {
    scene.traverse((o) => {
      if (o.geometry) o.geometry.dispose()
      if (o.material) o.material.dispose()
    })
    renderer.dispose()
    renderer.domElement?.remove()
    renderer = null
  }
}

onMounted(() => {
  use3D.value = canRender3D()
  if (use3D.value) initScene()
})

onBeforeUnmount(dispose)
</script>

<template>
  <!-- Conteneur 3D. En fallback, on affiche un dégradé mesh animé. -->
  <div ref="container" class="absolute inset-0 h-full w-full">
    <div v-if="!use3D" class="mesh-fallback absolute inset-0 h-full w-full"></div>
  </div>
</template>
