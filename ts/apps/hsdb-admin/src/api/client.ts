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

import axios from 'axios';
import { HSDBBaseAPI } from '@teatype/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

// Configure the HSDB API client globally
HSDBBaseAPI.configure({
    baseUrl: API_BASE_URL,
    timeout: 10000,
});

// Legacy axios client for backward compatibility
export const apiClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor
apiClient.interceptors.request.use(
    (config) => {
        // Add auth token if needed
        const token = localStorage.getItem('auth_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
            // Also set on HSDB API
            HSDBBaseAPI.setAuthToken(token);
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Handle unauthorized
            localStorage.removeItem('auth_token');
            HSDBBaseAPI.setAuthToken(undefined);
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);
