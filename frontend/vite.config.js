import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,        // ou qualquer porta que quiser
    open: true         // abre automaticamente no navegador
  },
  resolve: {
    alias: {
      '@': '/src'      // facilita imports usando @
    }
  }
});
