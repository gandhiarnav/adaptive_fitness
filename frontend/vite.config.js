import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    // This tells Vite to allow your Cloudflare tunnel.
    // Note: If you close the tunnel and get a new URL tomorrow, 
    // you will need to update this string!
    allowedHosts: ['mechanism-points-varies-prot.trycloudflare.com']
  }
})