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

import { HSDBBaseAPI, HSDBAPIRegistry } from '@teatype/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

// Configure the HSDB API client globally
HSDBBaseAPI.configure({
    baseUrl: API_BASE_URL,
    timeout: 10000,
});

/**
 * Initialize auth token from localStorage if available
 */
export function initializeAuth(): void {
    const token = localStorage.getItem('auth_token');
    if (token) {
        HSDBBaseAPI.setAuthToken(token);
    }
}

/**
 * Set auth token and persist to localStorage
 */
export function setAuthToken(token: string | undefined): void {
    if (token) {
        localStorage.setItem('auth_token', token);
        HSDBBaseAPI.setAuthToken(token);
    } else {
        localStorage.removeItem('auth_token');
        HSDBBaseAPI.setAuthToken(undefined);
    }
}

/**
 * Clear auth and redirect to login
 */
export function handleUnauthorized(): void {
    setAuthToken(undefined);
    window.location.href = '/login';
}

/**
 * Initialize the API registry from the server
 * This fetches all available APIs based on registered models
 */
export async function initializeAPIRegistry(): Promise<void> {
    try {
        await HSDBAPIRegistry.initialize();
        console.log('API Registry initialized:', HSDBAPIRegistry.getResourceNames());
    } catch (error) {
        console.error('Failed to initialize API registry:', error);
    }
}

// Initialize auth on module load
initializeAuth();
