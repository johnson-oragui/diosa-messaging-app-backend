import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,  // Customize the dev server port
    open: true,  // Automatically open the browser
    // proxy: {
    //   '/api/v1': {
    //     target: 'http://localhost:7001',
    //     changeOrigin: true,
    //     rewrite: (path) => path.replace(/^\/api/, ''),
    //   },
    // },
  },
  build: {
    outDir: "dist",  // Customize the build output directory
    sourcemap: true,  // Enable source maps for debugging production code
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ["react", "react-dom"],  // Separate vendor code into its own chunk
        }
      }
    }
  },
  resolve: {
    alias: {
      "@": "/src",  // Allows imports like import { MyComponent } from '@/components/MyComponent'
    }
  }
})
