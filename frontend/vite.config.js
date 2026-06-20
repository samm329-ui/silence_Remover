import { defineConfig } from 'vite'  
import react from '@vitejs/plugin-react'  
  
const proxyTarget = "http://localhost:8000"  
  
const proxyOpts = {  
  target: proxyTarget,  
  changeOrigin: true,  
  timeout: 0,  
  proxyTimeout: 0,  
}  
  
export default defineConfig({  
  plugins: [react()],  
  server: {  
    port: 5173,  
    host: true,  
    proxy: {  
      '/upload': proxyOpts,  
      '/analyze': proxyOpts,  
      '/process': proxyOpts,  
      '/download': proxyOpts,  
      '/original': proxyOpts,  
    },  
  },  
})  
