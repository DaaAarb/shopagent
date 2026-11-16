import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// En desarrollo, Vite reenvía /api/* al backend (http://localhost:8000/*).
// Así el navegador ve un único origen y no hace falta CORS. En producción lo
// hará el servidor web que sirva el frontend.
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
