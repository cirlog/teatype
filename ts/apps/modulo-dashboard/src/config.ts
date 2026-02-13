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

/**
 * API configuration for the Modulo Dashboard.
 * 
 * Supports multiple ways to configure the backend URL:
 * 1. Environment variable VITE_API_BASE_URL (build-time)
 * 2. window.__MODULO_CONFIG__.apiBaseUrl (runtime injection by backend)
 * 3. Same-origin relative paths (default, works with Vite proxy in dev)
 */

// Extend Window interface to include runtime config
declare global {
    interface Window {
        __MODULO_CONFIG__?: {
            apiBaseUrl?: string;
            backendPort?: number;
        };
    }
}

/**
 * Get the API base URL for making requests to the backend.
 * 
 * Resolution order:
 * 1. Runtime config injected by backend (window.__MODULO_CONFIG__.apiBaseUrl)
 * 2. Vite environment variable (import.meta.env.VITE_API_BASE_URL)
 * 3. Auto-detect from current page if backend port is configured
 * 4. Empty string (same-origin, uses Vite proxy in dev or same server in prod)
 */
export const getApiBaseUrl = (): string => {
    // Check runtime config first (injected by backend into index.html)
    if (typeof window !== 'undefined' && window.__MODULO_CONFIG__?.apiBaseUrl) {
        return window.__MODULO_CONFIG__.apiBaseUrl;
    }

    // Check Vite environment variable
    if (import.meta.env.VITE_API_BASE_URL) {
        return import.meta.env.VITE_API_BASE_URL;
    }

    // Check if backend port is configured, construct URL from current hostname
    if (typeof window !== 'undefined' && window.__MODULO_CONFIG__?.backendPort) {
        const port = window.__MODULO_CONFIG__.backendPort;
        return `${window.location.protocol}//${window.location.hostname}:${port}`;
    }

    // Default: same-origin (Vite proxy handles in dev, same server in prod)
    return '';
};

/**
 * Build a full API URL for an endpoint.
 * @param endpoint - The API endpoint path (e.g., '/status', '/api/logs')
 * @returns Full URL to the endpoint
 */
export const apiUrl = (endpoint: string): string => {
    const base = getApiBaseUrl();
    // Ensure proper joining (no double slashes)
    if (base && !base.endsWith('/') && !endpoint.startsWith('/')) {
        return `${base}/${endpoint}`;
    }
    return `${base}${endpoint}`;
};

/**
 * Configuration object for the dashboard.
 * Can be used to check available features or settings.
 */
export const getConfig = () => ({
    apiBaseUrl: getApiBaseUrl(),
    isDev: import.meta.env.DEV,
    isProd: import.meta.env.PROD,
});
