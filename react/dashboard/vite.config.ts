import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
    plugins: [react()],
    build: {
        outDir: 'dist',
        sourcemap: true,
        rollupOptions: {
            output: {
                manualChunks: undefined
            }
        }
    },
    css: {
        preprocessorOptions: {
            scss: {
                additionalData: '@use "./src/styles/theme" as *;'
            }
        }
    }
});
