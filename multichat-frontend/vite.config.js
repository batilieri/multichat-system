import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  // Configurações para evitar processar arquivos do sistema
  optimizeDeps: {
    exclude: ['@vite/client', '@vite/env'],
  },
  // Ignorar arquivos específicos
  build: {
    rollupOptions: {
      external: [
        // Ignorar arquivos de extensões do navegador
        /.*edge.*/,
        /.*chrome.*/,
        /.*firefox.*/,
        /.*extension.*/,
        /.*AppData.*/,
        /.*Configurações Locais.*/,
        /.*OneDrive.*/,
        /.*Desktop.*/,
        /.*Documents.*/,
        /.*Downloads.*/,
        /.*Program Files.*/,
        /.*Windows.*/,
        /.*System32.*/,
        /.*CapCut.*/,
        /.*PyCharm.*/,
        /.*JetBrains.*/,
        /.*Microsoft.*/,
        /.*Google.*/,
        /.*Adobe.*/,
        /.*node_modules.*/,
      ],
    },
  },
  // Configuração para ignorar arquivos durante o desenvolvimento
  clearScreen: false,
  // Configuração para evitar escaneamento desnecessário
  css: {
    devSourcemap: false,
  },
})
