/// <reference types="vitest" />
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    watch: process.env.VITE_USE_POLLING ? { usePolling: true, interval: 300 } : undefined,
    proxy: {
      '/api': process.env.VITE_API_PROXY_TARGET ?? 'http://localhost:8000',
    },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test-setup.ts'],
  },
})
