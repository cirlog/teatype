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
import { TeaTooltip } from './TeaTooltip';

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
    /** Function to get tooltip content for a row (shown on row hover) */
    rowTooltip?: (row: T, index: number) => React.ReactNode;
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
    rowTooltip,
}: TeaTableProps<T>) {
    const [hoveredRowIndex, setHoveredRowIndex] = useState<number | null>(null);

    const renderSortIndicator = (column: TeaTableColumn<T>) => {
        if (!column.sortable || sortKey !== column.key) return null;
        return <span className='tea-table__sort-indicator'>{sortDirection === 'asc' ? '↑' : '↓'}</span>;
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
                                    className={hoveredRowIndex === index ? 'tea-table__row--hovered' : ''}
                                    onMouseEnter={() => setHoveredRowIndex(index)}
                                    onMouseLeave={() => setHoveredRowIndex(null)}
                                >
                                    {columns.map((column, colIndex) => (
                                        <td key={column.key} className={column.className || ''}>
                                            {colIndex === 0 && rowTooltip ? (
                                                <div className='tea-table__cell-with-tooltip'>
                                                    {column.render
                                                        ? column.render(row, index)
                                                        : (row as Record<string, unknown>)[column.key]?.toString() ||
                                                          '-'}
                                                    {hoveredRowIndex === index && (
                                                        <div className='tea-table__row-tooltip'>
                                                            {rowTooltip(row, index)}
                                                        </div>
                                                    )}
                                                </div>
                                            ) : column.render ? (
                                                column.render(row, index)
                                            ) : (
                                                (row as Record<string, unknown>)[column.key]?.toString() || '-'
                                            )}
                                        </td>
                                    ))}
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
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
