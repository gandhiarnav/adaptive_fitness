import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    // This tells Vite to allow your Cloudflare tunnel.
    // Note: If you close the tunnel and get a new URL tomorrow, 
    // you will need to update this string!
    allowedHosts: ['mechanism-points-varies-prot.trycloudflare.com'],
    // Proxy API requests to the backend
    // This allows the tunnel to serve both frontend and API requests
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})