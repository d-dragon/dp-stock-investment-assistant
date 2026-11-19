import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import react from '@vitejs/plugin-react'
import { defineConfig, type Plugin } from 'vite'

const workerFile = join(dirname(fileURLToPath(import.meta.url)), 'node_modules/msw/lib/mockServiceWorker.js')

function mswWorker(): Plugin {
  return {
    name: 'msw-worker-dev-only',
    configureServer(server) {
      server.middlewares.use('/mockServiceWorker.js', (_req, res) => {
        res.setHeader('content-type', 'text/javascript')
        res.end(readFileSync(workerFile))
      })
    },
  }
}

// The browser stays on this origin. Vite forwards /api to the Flask API.
// Credentialed CORS is not configured.
export default defineConfig({
  plugins: [react(), mswWorker()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
      },
    },
  },
})
