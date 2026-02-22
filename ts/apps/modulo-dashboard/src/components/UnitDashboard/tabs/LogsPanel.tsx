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

import { useEffect, useRef } from 'react';

// Teatype components
import { TeaButton } from '../../../../../../components';

import { useAppLogs, type tLogEntry } from '../../../hooks/useAppLogs';

import './style/LogsPanel.scss';

interface iLogsPanelProps {
    autoScroll?: boolean;
    maxHeight?: string;
}

const getLevelColor = (level: string): string => {
    switch (level.toUpperCase()) {
        case 'ERROR':
            return '#ef4444';
        case 'WARN':
        case 'WARNING':
            return '#f97316';
        case 'INFO':
            return '#10b981';
        case 'DEBUG':
            return '#6366f1';
        case 'DASHBOARD':
            return '#06b6d4';
        default:
            return '#94a3b8';
    }
};

const formatTimestamp = (timestamp: string): string => {
    try {
        const date = new Date(timestamp);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch {
        return timestamp;
    }
};

function LogEntry({ entry }: { entry: tLogEntry }) {
    const levelColor = getLevelColor(entry.level);

    return (
        <div className='log-entry'>
            <span className='log-entry__time'>{formatTimestamp(entry.timestamp)}</span>
            <span className='log-entry__level' style={{ color: levelColor }}>
                [{entry.level}]
            </span>
            <span className='log-entry__message'>{entry.message}</span>
        </div>
    );
}

export function LogsPanel({ autoScroll = true, maxHeight = '400px' }: iLogsPanelProps) {
    const { logs, loading, error, refresh } = useAppLogs();
    const containerRef = useRef<HTMLDivElement>(null);
    const wasScrolledToBottom = useRef(true);

    // Check if scrolled to bottom before update
    useEffect(() => {
        if (!containerRef.current) return;

        const container = containerRef.current;
        const isAtBottom = container.scrollHeight - container.scrollTop <= container.clientHeight + 50;
        wasScrolledToBottom.current = isAtBottom;
    }, [logs]);

    // Auto-scroll to bottom when new logs arrive
    useEffect(() => {
        if (!autoScroll || !containerRef.current || !wasScrolledToBottom.current) return;

        containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }, [logs, autoScroll]);

    return (
        <section className='card logs-panel'>
            <div className='logs-panel__header'>
                <h2>Application Logs</h2>
                <div className='logs-panel__controls'>
                    <span className='logs-panel__count'>{logs.length} entries</span>
                    <TeaButton size='sm' variant='ghost' onClick={refresh} disabled={loading}>
                        {loading ? '...' : '🔄'}
                    </TeaButton>
                </div>
            </div>

            {error && <div className='logs-panel__error'>❌ Failed to fetch logs: {error}</div>}

            <div ref={containerRef} className='logs-panel__container' style={{ maxHeight }}>
                {logs.length === 0 ? (
                    <div className='logs-panel__empty'>No logs available yet...</div>
                ) : (
                    logs.map((entry, idx) => <LogEntry key={`${entry.timestamp}-${idx}`} entry={entry} />)
                )}
            </div>
        </section>
    );
}

export default LogsPanel;
