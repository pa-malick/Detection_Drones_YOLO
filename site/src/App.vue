<script setup>
/**
 * App — assemblage de la page unique (one-page) :
 *   1. Hero     : image de fond (un drone réellement détecté par le modèle)
 *                 + maillage 3D subtil + titre en text-reveal
 *   2. BentoGrid: le contenu du projet en grille asymétrique
 *   3. Footer   : contact minimal
 */
import HeroScene from './components/HeroScene.vue'
import BentoGrid from './components/BentoGrid.vue'
import SiteFooter from './components/SiteFooter.vue'

// Chemin de base (fonctionne en local comme sur l'hébergeur).
const heroBg = `url(${import.meta.env.BASE_URL}hero.jpg)`
</script>

<template>
  <!-- ============================ HERO ============================ -->
  <section class="relative flex h-screen flex-col justify-center overflow-hidden px-6">
    <!-- Image de fond : un drone réellement détecté par YOLOv11 -->
    <div
      class="absolute inset-0 bg-cover bg-center"
      :style="{ backgroundImage: heroBg }"
    ></div>

    <!-- Voiles sombres : lisibilité du texte + ancrage à gauche et en bas -->
    <div class="absolute inset-0 bg-gradient-to-r from-ink via-ink/80 to-ink/20"></div>
    <div class="absolute inset-0 bg-gradient-to-t from-ink via-transparent to-ink/50"></div>

    <!-- Maillage 3D subtil par-dessus (desktop uniquement ; sur mobile on garde
         la photo seule, plus légère et plus nette) -->
    <div class="absolute inset-0 hidden opacity-40 md:block">
      <HeroScene />
    </div>

    <!-- Contenu du hero -->
    <div class="pointer-events-none relative z-10 mx-auto w-full max-w-6xl">
      <p class="mb-6 text-sm text-accent reveal-mask" style="animation-delay: 0.1s">
        // computer vision · yolov11
      </p>

      <!-- Titre massif, révélé ligne par ligne (taille progressive pour mobile) -->
      <h1 class="font-display text-4xl font-bold leading-[0.95] tracking-tightest sm:text-6xl md:text-8xl">
        <span class="block reveal-mask" style="animation-delay: 0.2s">La vision qui</span>
        <span class="block reveal-mask text-accent" style="animation-delay: 0.35s">traque les drones</span>
      </h1>

      <p class="mt-8 max-w-md text-sm leading-relaxed text-paper/80 reveal-mask" style="animation-delay: 0.55s">
        Détection de drones militaires par apprentissage profond. De l'annotation
        manuelle à l'export ONNX, difficultés réelles comprises.
      </p>
    </div>

    <!-- Indice de scroll -->
    <div class="absolute bottom-8 left-1/2 z-10 -translate-x-1/2 text-xs text-muted">
      <span class="animate-pulse">défiler ↓</span>
    </div>
  </section>

  <!-- ========================== CONTENU ========================== -->
  <BentoGrid />

  <!-- =========================== FOOTER ========================== -->
  <SiteFooter />
</template>
