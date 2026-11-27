import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Proxy de /api/* al backend: un único origen, sin CORS.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
