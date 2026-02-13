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

import { defineConfig, mergeConfig } from 'vite';
import { resolve } from 'path';
import { getBaseViteConfig } from '../../baseconfig/vite.config';

export default defineConfig(({ command }) => {
    const baseConfig = getBaseViteConfig(__dirname);

    return mergeConfig(baseConfig, {
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
        server: {
            port: parseInt(process.env.VITE_DASHBOARD_PORT || '5173'),
            // Proxy API requests to the FastAPI backend during development
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
    });
});
