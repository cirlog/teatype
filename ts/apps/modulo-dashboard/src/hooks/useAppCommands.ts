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
import { useCallback, useState } from 'react';

/**
 * Hook for sending commands to the application via the API.
 */
const useAppCommands = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [lastResult, setLastResult] = useState<any>(null);

    /**
     * Send a command to the application.
     */
    const sendCommand = useCallback(async (command: string, payload?: Record<string, any>) => {
        setLoading(true);
        setError(null);

        try {
            const response = await fetch('/api/app/command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ command, payload: payload || {} }),
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const result = await response.json();
            setLastResult(result);
            return result;
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Unknown error';
            setError(message);
            return { success: false, error: message };
        } finally {
            setLoading(false);
        }
    }, []);

    /**
     * Stop the application.
     */
    const stopApp = useCallback(async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await fetch('/api/app/stop', {
                method: 'POST',
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const result = await response.json();
            setLastResult(result);
            return result;
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Unknown error';
            setError(message);
            return { success: false, error: message };
        } finally {
            setLoading(false);
        }
    }, []);

    /**
     * Reboot the application.
     */
    const rebootApp = useCallback(async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await fetch('/api/app/reboot', {
                method: 'POST',
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const result = await response.json();
            setLastResult(result);
            return result;
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Unknown error';
            setError(message);
            return { success: false, error: message };
        } finally {
            setLoading(false);
        }
    }, []);

    return { sendCommand, stopApp, rebootApp, loading, error, lastResult };
};

export { useAppCommands };
export default useAppCommands;
