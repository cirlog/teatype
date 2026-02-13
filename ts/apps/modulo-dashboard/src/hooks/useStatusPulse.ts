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
import { useCallback, useEffect, useMemo, useState } from 'react';

// Config
import { apiUrl } from '../config';

/**
 * Represents a snapshot of the current system status at a point in time.
 * Contains information about the unit state, designation, status message,
 * loop iteration count, and the type of status tracking being used.
 */
type tStatusSnapshot = {
    unit: string;
    designation: string;
    status: string;
    loop_iter: number;
    type: string;
};

// Initial default status state used when the hook first mounts before any real data is fetched
const DEFAULT_STATUS: tStatusSnapshot = {
    unit: 'unknown',
    designation: '—',
    status: 'initializing',
    loop_iter: 0,
    type: 'modulo'
};

// Maximum number of historical status entries to keep in the history array
const HISTORY_LIMIT = 5;

/**
 * Custom React hook that manages periodic polling of a status endpoint.
 * Maintains current status snapshot, historical log of status changes, loading state, and error handling.
 * Automatically starts polling on mount with a 15-second interval and cleans up on unmount.
 * 
 * @param {string} [endpoint] - Optional custom endpoint URL. If not provided, uses window.__statusEndpoint or defaults to '/status'
 * @returns {Object} Object containing:
 *   - status: Current StatusSnapshot
 *   - history: Array of timestamped status strings (max 5 entries)
 *   - updating: Boolean indicating if a fetch is in progress
 *   - error: Error message string or null if no error
 *   - refresh: Function to manually trigger a status update
 */
const useStatusPulse = (endpoint?: string) => {
    // State for the most recent status snapshot
    const [status, setStatus] = useState<tStatusSnapshot>(DEFAULT_STATUS);
    // State for the timestamped history of status changes, initialized with a waiting message
    const [history, setHistory] = useState<string[]>(['Waiting for first update …']);
    // State to track whether an update request is currently in flight
    const [updating, setUpdating] = useState(false);
    // State to store any error message from the last failed request, null if no error
    const [error, setError] = useState<string | null>(null);

    // Memoized endpoint URL resolution: prioritizes explicit endpoint prop, then config-based URL
    // Only recalculates when the endpoint prop changes, preventing unnecessary refresh callback recreations
    const targetEndpoint = useMemo(() => {
        if (endpoint) return endpoint;
        return apiUrl('/status');
    }, [endpoint]);

    // Memoized callback function that fetches the latest status from the endpoint
    // Wrapped in useCallback to maintain referential equality across re-renders, essential for the useEffect dependency
    const refresh = useCallback(async () => {
        // Validate that an endpoint is available before attempting fetch
        if (!targetEndpoint) {
            setError('No status endpoint configured');
            return;
        }
        // Set updating flag to true to indicate request is in progress
        setUpdating(true);
        // Clear any previous errors when starting a new request
        setError(null);
        try {
            // Fetch status data with cache disabled to always get fresh data
            const response = await fetch(targetEndpoint, { cache: 'no-store' });
            // Check if the HTTP response status indicates success
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            // Parse the JSON payload from the response
            const payload = await response.json();
            // Update the status state with the new payload
            setStatus(payload);
            // Format current time as HH:MM:SS for history entry
            const ts = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            // Update history: prepend new status entry, remove initial waiting message if present, keep only most recent HISTORY_LIMIT entries
            setHistory((prev) => {
                const next = [`${ts} · ${payload.status}`, ...prev.filter((item) => item !== 'Waiting for first update …')];
                return next.slice(0, HISTORY_LIMIT);
            });
        } catch (err) {
            // Extract error message from Error object or use generic message for non-Error exceptions
            const message = err instanceof Error ? err.message : 'Unknown error';
            // Set error state for UI display
            setError(message);
            // Add error entry to history and maintain HISTORY_LIMIT constraint
            setHistory((prev) => [`Error · ${message}`, ...prev].slice(0, HISTORY_LIMIT));
        } finally {
            // Always clear the updating flag when the request completes, whether success or failure
            setUpdating(false);
        }
    }, [targetEndpoint]);

    // Effect hook to set up initial fetch and periodic polling interval
    // Runs on mount and whenever refresh callback changes (which depends on targetEndpoint)
    useEffect(() => {
        // Perform an immediate status fetch when the hook mounts
        refresh();
        // Set up an interval to automatically refresh status every 15 seconds (15000ms)
        const interval = window.setInterval(refresh, 15000);
        // Clean up: clear the interval when the component unmounts or dependencies change
        return () => window.clearInterval(interval);
    }, [refresh]);

    // Return object with status data, history log, loading state, error state, and manual refresh function
    return { status, history, updating, error, refresh };
}

export type { tStatusSnapshot };

export default useStatusPulse;