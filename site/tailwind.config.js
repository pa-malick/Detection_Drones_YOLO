/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      colors: {
        // Base sombre et profonde + un seul accent électrique.
        ink: '#020617',        // slate-950, le fond
        'ink-soft': '#0b1120', // panneaux légèrement plus clairs
        paper: '#E8E8E3',      // blanc cassé, le texte
        muted: '#8A93A6',      // texte secondaire
        accent: '#C6F135',     // Cyber Lime — l'unique couleur d'accent
        'accent-dim': '#9bbe1f',
      },
      fontFamily: {
        // Titres massifs géométriques + corps monospace « code ».
        display: ['"Space Grotesk"', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      letterSpacing: {
        tightest: '-0.05em',
      },
    },
  },
  plugins: [],
}
