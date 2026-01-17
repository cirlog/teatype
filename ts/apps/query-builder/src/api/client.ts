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

import axios, { AxiosRequestConfig, Method } from 'axios';

const DEFAULT_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

export const apiClient = axios.create({
    baseURL: DEFAULT_BASE_URL,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
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
            localStorage.removeItem('auth_token');
        }
        return Promise.reject(error);
    }
);

export interface ExecuteQueryParams {
    method: Method;
    baseUrl: string;
    endpoint: string;
    resource: string;
    queryParams?: Record<string, string>;
    body?: unknown;
}

export const executeQuery = async (params: ExecuteQueryParams) => {
    const { method, baseUrl, endpoint, resource, queryParams, body } = params;

    const url = `${endpoint}/${resource}`;

    const config: AxiosRequestConfig = {
        method,
        url,
        baseURL: baseUrl,
        params: queryParams,
        data: body,
    };

    const response = await axios(config);
    return response;
};

export default apiClient;
