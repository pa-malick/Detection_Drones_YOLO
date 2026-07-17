import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// base './' -> chemins relatifs, le build fonctionne sur n'importe quel hébergeur
// (Netlify, Vercel, GitHub Pages) sans configuration supplémentaire.
export default defineConfig({
  plugins: [vue()],
  base: './',
})
