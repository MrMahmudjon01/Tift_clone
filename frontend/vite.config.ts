import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// Lokal ishlashda /api va /media so'rovlari Django'ga yo'naltiriladi (CORS kerak emas).
// Backend manzili: frontend/.env.local -> BACKEND_URL=http://localhost:8000
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const target = env.BACKEND_URL || 'http://localhost:8000'
  return {
    plugins: [react()],
    server: {
      port: 5173,
      proxy: {
        '/api': { target },
        '/media': { target },
      },
    },
  }
})
