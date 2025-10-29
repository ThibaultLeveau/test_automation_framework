import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      '^/api$': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api$/, '')
      },
      '^/api/': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    },
    // Add this to handle Vue Router history mode in development
    fs: {
      allow: ['..']
    }
  },
  // Add this to handle Vue Router history mode in production
  build: {
    rollupOptions: {
      external: []
    }
  },
  // Add this to handle SPA fallback for Vue Router history mode
  preview: {
    port: 3000
  }
})
