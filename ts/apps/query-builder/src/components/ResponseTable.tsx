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

import React, { useMemo, useState } from 'react';

import { QueryResponse } from '../api/query';

interface ResponseTableProps {
    response: QueryResponse | null;
    loading?: boolean;
}

type SortDirection = 'asc' | 'desc';

export const ResponseTable: React.FC<ResponseTableProps> = ({ response, loading = false }) => {
    const [sortKey, setSortKey] = useState<string | null>(null);
    const [sortDirection, setSortDirection] = useState<SortDirection>('asc');

    // Extract data array from response
    const dataArray = useMemo(() => {
        if (!response?.data) return [];

        // Handle different response shapes
        if (Array.isArray(response.data)) {
            return response.data;
        }
        if (typeof response.data === 'object') {
            // Check for common wrapper keys
            const data = response.data as Record<string, unknown>;
            if (Array.isArray(data.results)) return data.results;
            if (Array.isArray(data.data)) return data.data;
            if (Array.isArray(data.items)) return data.items;
            // If it's a single object, wrap in array
            return [response.data];
        }
        return [];
    }, [response?.data]);

    // Get all unique keys from data
    const columns = useMemo(() => {
        if (dataArray.length === 0) return [];

        const allKeys = new Set<string>();
        dataArray.forEach((item) => {
            if (typeof item === 'object' && item !== null) {
                Object.keys(item).forEach((key) => allKeys.add(key));
            }
        });

        return Array.from(allKeys);
    }, [dataArray]);

    // Sort data
    const sortedData = useMemo(() => {
        if (!sortKey) return dataArray;

        return [...dataArray].sort((a, b) => {
            const aVal = (a as Record<string, unknown>)[sortKey];
            const bVal = (b as Record<string, unknown>)[sortKey];

            if (aVal === null || aVal === undefined) return 1;
            if (bVal === null || bVal === undefined) return -1;

            if (typeof aVal === 'number' && typeof bVal === 'number') {
                return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
            }

            const aStr = String(aVal).toLowerCase();
            const bStr = String(bVal).toLowerCase();
            return sortDirection === 'asc' ? aStr.localeCompare(bStr) : bStr.localeCompare(aStr);
        });
    }, [dataArray, sortKey, sortDirection]);

    const handleSort = (key: string) => {
        if (sortKey === key) {
            setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
        } else {
            setSortKey(key);
            setSortDirection('asc');
        }
    };

    const getSortIndicator = (key: string) => {
        if (sortKey !== key) return ' ↕';
        return sortDirection === 'asc' ? ' ↑' : ' ↓';
    };

    const formatValue = (value: unknown): string => {
        if (value === null || value === undefined) return '-';
        if (typeof value === 'boolean') return value ? 'Yes' : 'No';
        if (typeof value === 'object') return JSON.stringify(value);
        return String(value);
    };

    if (!response && !loading) {
        return (
            <div className='response-table response-table--empty'>
                <div className='response-table__placeholder'>
                    <span className='response-table__placeholder-icon'>📋</span>
                    <p>Execute a query to see results</p>
                </div>
            </div>
        );
    }

    return (
        <div className='response-table'>
            {response && (
                <div className='response-table__meta'>
                    <span
                        className={`response-table__status response-table__status--${response.status >= 400 ? 'error' : 'success'}`}
                    >
                        {response.status} {response.statusText}
                    </span>
                    <span className='response-table__timing'>{response.timing}ms</span>
                    <span className='response-table__count'>
                        {dataArray.length} {dataArray.length === 1 ? 'item' : 'items'}
                    </span>
                </div>
            )}
            <div className='response-table__wrapper'>
                {loading ? (
                    <div className='response-table__loading'>Loading...</div>
                ) : sortedData.length === 0 ? (
                    <div className='response-table__empty-data'>
                        {response?.status && response.status >= 400
                            ? `Error: ${JSON.stringify(response.data)}`
                            : 'No data returned'}
                    </div>
                ) : (
                    <table>
                        <thead>
                            <tr>
                                {columns.map((col) => (
                                    <th key={col} className='sortable' onClick={() => handleSort(col)}>
                                        {col.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
                                        {getSortIndicator(col)}
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {sortedData.map((row, index) => (
                                <tr key={(row as Record<string, unknown>).id?.toString() || index}>
                                    {columns.map((col) => (
                                        <td key={col}>{formatValue((row as Record<string, unknown>)[col])}</td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
};

export default ResponseTable;
