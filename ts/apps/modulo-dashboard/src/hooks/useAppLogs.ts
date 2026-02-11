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

// React imports
import { useCallback, useEffect, useState } from 'react';

/**
 * Represents a single log entry from the application.
 */
export type tLogEntry = {
    timestamp: string;
    level: string;
    message: string;
    unit: string;
};

/**
 * Custom React hook that fetches and manages application logs.
 * Polls the /api/logs endpoint at a configurable interval.
 * 
 * @param endpoint - Optional custom endpoint URL
 * @param pollInterval - Polling interval in milliseconds (default: 5000)
 * @param limit - Maximum number of logs to fetch (default: 100)
 */
const useAppLogs = (endpoint?: string, pollInterval: number = 5000, limit: number = 100) => {
    const [logs, setLogs] = useState<tLogEntry[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Determine the target endpoint
    const targetEndpoint = endpoint || '/api/logs';

    const refresh = useCallback(async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await fetch(`${targetEndpoint}?limit=${limit}`, { cache: 'no-store' });
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            const data = await response.json();
            setLogs(data.logs || []);
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Unknown error';
            setError(message);
        } finally {
            setLoading(false);
        }
    }, [targetEndpoint, limit]);

    // Set up polling
    useEffect(() => {
        refresh();
        const interval = window.setInterval(refresh, pollInterval);
        return () => window.clearInterval(interval);
    }, [refresh, pollInterval]);

    return { logs, loading, error, refresh };
};

export { useAppLogs };
export default useAppLogs;
