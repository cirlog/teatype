import { useCallback, useEffect, useMemo, useState } from 'react';

export type StatusSnapshot = {
    unit: string;
    designation: string;
    status: string;
    loop_iter: number;
    type: string;
};

const DEFAULT_STATUS: StatusSnapshot = {
    unit: 'unknown',
    designation: '—',
    status: 'initializing',
    loop_iter: 0,
    type: 'modulo'
};

const HISTORY_LIMIT = 5;

export function useStatusPulse(endpoint?: string) {
    const [status, setStatus] = useState<StatusSnapshot>(DEFAULT_STATUS);
    const [history, setHistory] = useState<string[]>(['Waiting for first update …']);
    const [updating, setUpdating] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const targetEndpoint = useMemo(() => {
        if (endpoint) return endpoint;
        if (typeof window !== 'undefined') {
            return (window as any).__statusEndpoint || '/status';
        }
        return '/status';
    }, [endpoint]);

    const refresh = useCallback(async () => {
        if (!targetEndpoint) {
            setError('No status endpoint configured');
            return;
        }
        setUpdating(true);
        setError(null);
        try {
            const response = await fetch(targetEndpoint, { cache: 'no-store' });
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            const payload = await response.json();
            setStatus(payload);
            const ts = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            setHistory((prev) => {
                const next = [`${ts} · ${payload.status}`, ...prev.filter((item) => item !== 'Waiting for first update …')];
                return next.slice(0, HISTORY_LIMIT);
            });
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Unknown error';
            setError(message);
            setHistory((prev) => [`Error · ${message}`, ...prev].slice(0, HISTORY_LIMIT));
        } finally {
            setUpdating(false);
        }
    }, [targetEndpoint]);

    useEffect(() => {
        refresh();
        const interval = window.setInterval(refresh, 15000);
        return () => window.clearInterval(interval);
    }, [refresh]);

    return { status, history, updating, error, refresh };
}
