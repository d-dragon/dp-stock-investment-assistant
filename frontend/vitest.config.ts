import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/storage-shim.ts', './src/test/setup.ts', './src/test/rtl-cleanup.ts'],
    exclude: ['e2e/**', 'node_modules/**'],
  },
})
