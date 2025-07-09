import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import dotenv from 'dotenv'

// https://vite.dev/config/
dotenv.config()

export default defineConfig({
  base: './',
  plugins: [vue(), vueDevTools(), tailwindcss()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: process.env.VITE_PORT ? Number(process.env.VITE_PORT) : 3000,
    // proxy: {
    //   '/api': {
    //     target: process.env.VITE_API_PROXY_TARGET || 'http://localhost:8000',
    //     changeOrigin: true,
    //   },
    // },
  },
})
