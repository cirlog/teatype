/**
 * @license
 * Copyright (C) 2024-2026 Burak Günaydin
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 */

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig(({ command }) => ({
    plugins: [react()],
    root: '.',
    // Use /dashboard/ base path only for production builds, not for dev server
    base: command === 'build' ? '/dashboard/' : '/',
    build: {
        outDir: 'dist',
        emptyOutDir: true,
        rollupOptions: {
            input: resolve(__dirname, 'index.html'),
        },
    },
    resolve: {
        alias: {
            '@': resolve(__dirname, 'src'),
            '@teatype/style': resolve(__dirname, '../../style'),
        },
    },
    css: {
        preprocessorOptions: {
            scss: {
                additionalData: `@use "${resolve(__dirname, '../../style/globstyle').replace(/\\/g, '/')}" as *;\n`,
            },
        },
    },
    server: {
        cors: true,
        host: '0.0.0.0',
        port: parseInt(process.env.VITE_DASHBOARD_PORT || '5173'),
        open: false,
        // Proxy API requests to the FastAPI backend during development
        // Use VITE_BACKEND_PORT env var or default to 8080
        proxy: {
            '/api': {
                target: `http://127.0.0.1:${process.env.VITE_BACKEND_PORT || '8080'}`,
                changeOrigin: true,
            },
            '/status': {
                target: `http://127.0.0.1:${process.env.VITE_BACKEND_PORT || '8080'}`,
                changeOrigin: true,
            },
        },
    },
}));
