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

import { useState, useCallback } from 'react';
import toast from 'react-hot-toast';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

import {
    QueryConfig,
    QueryCondition,
    QueryResponse,
    HttpMethod,
    SortOption,
    buildFullUrl,
} from '../api/query';

const DEFAULT_CONFIG: QueryConfig = {
    method: 'GET',
    baseUrl: 'http://localhost:8080',
    endpoint: 'api/v1',
    resource: '',
    conditions: [],
    sort: undefined,
    limit: undefined,
    offset: undefined,
    body: undefined,
};

export const useQueryBuilder = () => {
    const [config, setConfig] = useState<QueryConfig>(DEFAULT_CONFIG);
    const [response, setResponse] = useState<QueryResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [history, setHistory] = useState<{ config: QueryConfig; response: QueryResponse }[]>([]);

    // Setters
    const setMethod = useCallback((method: HttpMethod) => {
        setConfig((prev) => ({ ...prev, method }));
    }, []);

    const setBaseUrl = useCallback((baseUrl: string) => {
        setConfig((prev) => ({ ...prev, baseUrl }));
    }, []);

    const setEndpoint = useCallback((endpoint: string) => {
        setConfig((prev) => ({ ...prev, endpoint }));
    }, []);

    const setResource = useCallback((resource: string) => {
        setConfig((prev) => ({ ...prev, resource }));
    }, []);

    const setSort = useCallback((sort: SortOption | undefined) => {
        setConfig((prev) => ({ ...prev, sort }));
    }, []);

    const setLimit = useCallback((limit: number | undefined) => {
        setConfig((prev) => ({ ...prev, limit }));
    }, []);

    const setOffset = useCallback((offset: number | undefined) => {
        setConfig((prev) => ({ ...prev, offset }));
    }, []);

    const setBody = useCallback((body: Record<string, unknown> | undefined) => {
        setConfig((prev) => ({ ...prev, body }));
    }, []);

    // Condition management
    const addCondition = useCallback(() => {
        const newCondition: QueryCondition = {
            id: uuidv4(),
            field: '',
            operator: 'equals',
            value: '',
        };
        setConfig((prev) => ({
            ...prev,
            conditions: [...prev.conditions, newCondition],
        }));
    }, []);

    const updateCondition = useCallback((id: string, updates: Partial<QueryCondition>) => {
        setConfig((prev) => ({
            ...prev,
            conditions: prev.conditions.map((c) =>
                c.id === id ? { ...c, ...updates } : c
            ),
        }));
    }, []);

    const removeCondition = useCallback((id: string) => {
        setConfig((prev) => ({
            ...prev,
            conditions: prev.conditions.filter((c) => c.id !== id),
        }));
    }, []);

    const clearConditions = useCallback(() => {
        setConfig((prev) => ({ ...prev, conditions: [] }));
    }, []);

    // Execute query
    const execute = useCallback(async () => {
        if (!config.resource) {
            toast.error('Please select a resource first');
            return;
        }

        setLoading(true);
        setError(null);

        const startTime = performance.now();

        try {
            const url = buildFullUrl(config);

            const axiosConfig = {
                method: config.method,
                url,
                data: config.method !== 'GET' ? config.body : undefined,
                headers: {
                    'Content-Type': 'application/json',
                },
            };

            const res = await axios(axiosConfig);
            const endTime = performance.now();

            const queryResponse: QueryResponse = {
                data: res.data,
                status: res.status,
                statusText: res.statusText,
                headers: res.headers as Record<string, string>,
                timing: Math.round(endTime - startTime),
            };

            setResponse(queryResponse);
            setHistory((prev) => [...prev, { config: { ...config }, response: queryResponse }]);
            toast.success(`Query executed in ${queryResponse.timing}ms`);
        } catch (err) {
            const endTime = performance.now();
            const timing = Math.round(endTime - startTime);

            if (axios.isAxiosError(err)) {
                const errorResponse: QueryResponse = {
                    data: err.response?.data || { error: err.message },
                    status: err.response?.status || 0,
                    statusText: err.response?.statusText || 'Error',
                    headers: (err.response?.headers as Record<string, string>) || {},
                    timing,
                };
                setResponse(errorResponse);
                setError(err.message);
                toast.error(`Request failed: ${err.message}`);
            } else {
                const message = err instanceof Error ? err.message : 'Unknown error';
                setError(message);
                toast.error(message);
            }
        } finally {
            setLoading(false);
        }
    }, [config]);

    // Reset
    const reset = useCallback(() => {
        setConfig(DEFAULT_CONFIG);
        setResponse(null);
        setError(null);
    }, []);

    const clearResponse = useCallback(() => {
        setResponse(null);
        setError(null);
    }, []);

    const clearHistory = useCallback(() => {
        setHistory([]);
    }, []);

    // Get full URL preview
    const getFullUrl = useCallback(() => {
        return buildFullUrl(config);
    }, [config]);

    // Check if can execute
    const canExecute = config.resource.length > 0;

    return {
        config,
        response,
        loading,
        error,
        history,
        canExecute,
        // Setters
        setMethod,
        setBaseUrl,
        setEndpoint,
        setResource,
        setSort,
        setLimit,
        setOffset,
        setBody,
        // Condition management
        addCondition,
        updateCondition,
        removeCondition,
        clearConditions,
        // Actions
        execute,
        reset,
        clearResponse,
        clearHistory,
        getFullUrl,
    };
};
