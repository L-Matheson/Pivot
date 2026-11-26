import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// In dev, /api is proxied to the FastAPI backend so the browser stays same-origin.
// In Docker, bind mounts from Windows don't emit file events, so polling is enabled there.
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    watch: process.env.VITE_USE_POLLING ? { usePolling: true, interval: 300 } : undefined,
    proxy: {
      '/api': process.env.VITE_API_PROXY_TARGET ?? 'http://localhost:8000',
    },
  },
})
