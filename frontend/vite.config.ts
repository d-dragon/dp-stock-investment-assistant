import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// The browser stays on this origin. Vite forwards /api to the Flask API.
// Credentialed CORS is not configured.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
      },
    },
  },
})
