import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig(({ command }) => ({
  plugins: [vue(), vueDevTools(), tailwindcss()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  // django-vite loads dev files from STATIC_URL + "dist/". Built files link to each other with
  // relative URLs, so they work wherever STATIC_URL points: local static files or a cloud bucket.
  base: command === 'serve' ? '/static/dist/' : './',
  server: {
    port: 5173,
    strictPort: true,
    // Assets such as fonts load from the dev server, not from Django
    origin: 'http://localhost:5173',
    // File change events don't reach containers through every Docker file sharing (e.g. Colima, WSL2),
    // so the Docker node service polls instead. Polling costs CPU, hence opt-in.
    watch: { usePolling: process.env.WATCH_POLLING === 'true' },
  },
  build: {
    // Collected by Django's collectstatic with the project's other static files
    outDir: '../{{ cookiecutter.project_slug }}/static/dist',
    emptyOutDir: true,
    manifest: true,
    rolldownOptions: {
      input: 'src/main.ts',
    },
  },
}))
