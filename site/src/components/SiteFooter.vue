<script setup>
/**
 * SiteFooter — contact minimal, style télégraphique.
 * Titre d'accroche massif + liens de contact discrets (l'e-mail est un bouton,
 * plus affiché en géant).
 */
const EMAIL = 'njaymika@gmail.com'
const LINKS = [
  { label: 'GitHub', url: 'https://github.com/pa-malick' },
  { label: 'LinkedIn', url: 'https://www.linkedin.com/in/papa-malick-ndiaye-b58b22309' },
  { label: 'Portfolio', url: 'https://pa-malick.github.io/portfolio/' },
]
</script>

<template>
  <footer id="contact" class="border-t border-white/10 px-6 py-20 md:py-28">
    <div class="mx-auto max-w-6xl">
      <p class="mb-6 text-sm text-accent">// contact</p>

      <!-- Titre neutre (plus d'e-mail géant) -->
      <h2 class="max-w-3xl font-display text-4xl font-bold leading-[1.05] tracking-tightest md:text-6xl">
        Restons en <span class="text-accent">contact</span>.
      </h2>

      <!-- Boutons de contact -->
      <div class="mt-10 flex flex-wrap items-center gap-4">
        <a
          :href="`mailto:${EMAIL}`"
          class="rounded-full bg-accent px-6 py-3 text-sm font-medium text-ink transition-transform duration-300 hover:-translate-y-0.5"
        >
          Me contacter →
        </a>
        <a
          v-for="l in LINKS"
          :key="l.label"
          :href="l.url"
          target="_blank"
          class="rounded-full border border-white/15 px-6 py-3 text-sm transition-colors duration-300 hover:border-accent hover:text-accent"
        >{{ l.label }}</a>
      </div>

      <div class="mt-16 border-t border-white/10 pt-8 text-sm text-muted">
        <p>Papa Malick NDIAYE — M2 Data Science, UADB</p>
      </div>
    </div>
  </footer>
</template>
