import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    tailwindcss(),
    react({
      babel: {
        plugins: [['babel-plugin-react-compiler']],
      },
    }),
  ],
  server: {
    host: '0.0.0.0',  // Erlaube Zugriff von außerhalb des Containers
    port: 3000,
    proxy: {
      '/api': {
        // Im Docker-Netzwerk verwende den Container-Namen
        target: 'http://backend:5000',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})
