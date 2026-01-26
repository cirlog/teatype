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

import React, { useState } from 'react';

import { TeaButton } from './TeaButton';
import { TeaModal } from './TeaModal';

import './style/TeaTable.scss';

export interface TeaTableColumn<T> {
    key: string;
    header: string;
    sortable?: boolean;
    render?: (row: T, index: number) => React.ReactNode;
    className?: string;
}

export interface TeaTableProps<T> {
    columns: TeaTableColumn<T>[];
    data: T[];
    keyExtractor: (row: T, index: number) => string | number;
    sortKey?: string;
    sortDirection?: 'asc' | 'desc';
    onSort?: (key: string) => void;
    emptyMessage?: string;
    loading?: boolean;
    className?: string;
    /** Enable clicking rows to view full data in modal */
    clickableRows?: boolean;
}

export function TeaTable<T>({
    columns,
    data,
    keyExtractor,
    sortKey,
    sortDirection,
    onSort,
    emptyMessage = 'No data available',
    loading = false,
    className = '',
    clickableRows = false,
}: TeaTableProps<T>) {
    const [selectedRow, setSelectedRow] = useState<T | null>(null);

    const renderSortIndicator = (column: TeaTableColumn<T>) => {
        if (!column.sortable || sortKey !== column.key) return null;
        return <span className='tea-table__sort-indicator'>{sortDirection === 'asc' ? '↑' : '↓'}</span>;
    };

    const formatValue = (value: unknown): string => {
        if (value === null || value === undefined) return '-';
        if (typeof value === 'object') return JSON.stringify(value, null, 2);
        return String(value);
    };

    return (
        <div className={`tea-table ${className}`}>
            <div className='tea-table__wrapper'>
                <table>
                    <thead>
                        <tr>
                            {columns.map((column) => (
                                <th
                                    key={column.key}
                                    className={`${column.sortable ? 'sortable' : ''} ${column.className || ''}`}
                                    onClick={() => column.sortable && onSort?.(column.key)}
                                >
                                    {column.header}
                                    {renderSortIndicator(column)}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr>
                                <td colSpan={columns.length} className='tea-table__loading'>
                                    Loading...
                                </td>
                            </tr>
                        ) : data.length === 0 ? (
                            <tr>
                                <td colSpan={columns.length} className='tea-table__empty'>
                                    {emptyMessage}
                                </td>
                            </tr>
                        ) : (
                            data.map((row, index) => (
                                <tr
                                    key={keyExtractor(row, index)}
                                    className={clickableRows ? 'tea-table__row--clickable' : ''}
                                    onClick={() => clickableRows && setSelectedRow(row)}
                                >
                                    {columns.map((column) => (
                                        <td key={column.key} className={column.className || ''}>
                                            {column.render
                                                ? column.render(row, index)
                                                : (row as Record<string, unknown>)[column.key]?.toString() || '-'}
                                        </td>
                                    ))}
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>

            {/* Row detail modal */}
            <TeaModal isOpen={selectedRow !== null} onClose={() => setSelectedRow(null)} title='Row Details' size='md'>
                {selectedRow && (
                    <div className='tea-table__row-details'>
                        {Object.entries(selectedRow as Record<string, unknown>).map(([key, value]) => (
                            <div key={key} className='tea-table__row-detail'>
                                <span className='tea-table__row-detail-key'>{key}</span>
                                <span className='tea-table__row-detail-value'>
                                    {typeof value === 'object' ? <pre>{formatValue(value)}</pre> : formatValue(value)}
                                </span>
                            </div>
                        ))}
                    </div>
                )}
            </TeaModal>
        </div>
    );
}

// Pagination component to use with TeaTable
interface TeaTablePaginationProps {
    currentPage: number;
    totalPages: number;
    totalItems: number;
    onPageChange: (page: number) => void;
}

export const TeaTablePagination: React.FC<TeaTablePaginationProps> = ({
    currentPage,
    totalPages,
    totalItems,
    onPageChange,
}) => {
    return (
        <div className='tea-table__pagination'>
            <TeaButton size='sm' onClick={() => onPageChange(1)} disabled={currentPage === 1}>
                «
            </TeaButton>
            <TeaButton size='sm' onClick={() => onPageChange(currentPage - 1)} disabled={currentPage === 1}>
                ‹
            </TeaButton>
            <span className='tea-table__pagination-info'>
                Page {currentPage} of {totalPages} ({totalItems} total)
            </span>
            <TeaButton size='sm' onClick={() => onPageChange(currentPage + 1)} disabled={currentPage === totalPages}>
                ›
            </TeaButton>
            <TeaButton size='sm' onClick={() => onPageChange(totalPages)} disabled={currentPage === totalPages}>
                »
            </TeaButton>
        </div>
    );
};

export default TeaTable;
