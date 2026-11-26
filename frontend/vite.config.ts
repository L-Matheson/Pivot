import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// In dev, /api is proxied to the FastAPI backend so the browser stays same-origin.
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': process.env.VITE_API_PROXY_TARGET ?? 'http://localhost:8000',
    },
  },
})
