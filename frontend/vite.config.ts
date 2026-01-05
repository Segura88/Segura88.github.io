import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ command, mode }) => ({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // proxy API requests to backend (adjust if backend runs elsewhere)
      '/weeks': 'http://localhost:8000',
      '/weekly-memory': 'http://localhost:8000',
      '/token': 'http://localhost:8000',
    }
  }
}))
