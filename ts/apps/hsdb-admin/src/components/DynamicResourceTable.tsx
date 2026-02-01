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

import { useState, useMemo } from 'react';
import { TeaTable, TeaTableColumn, TeaTablePagination } from '@teatype/components';
import { TeaButton } from '@teatype/components';
import { useConfirm } from '@teatype/components';
import { HSDBEntity, HSDBAPIInfo } from '@teatype/api';

interface DynamicResourceTableProps<E extends HSDBEntity> {
    /** API info for this resource */
    apiInfo: HSDBAPIInfo;
    /** Data to display */
    data: E[];
    /** Called when edit is requested */
    onEdit?: (entity: E) => void;
    /** Called when delete is requested */
    onDelete?: (id: string) => void;
    /** Check if a method is allowed */
    isMethodAllowed?: (method: string, isCollection?: boolean) => boolean;
    /** Page size for pagination */
    pageSize?: number;
}

type SortDirection = 'asc' | 'desc' | null;

/**
 * A dynamic table component that renders data based on HSDBAPIInfo schema.
 * Automatically generates columns from the field schema and respects allowed methods.
 */
export function DynamicResourceTable<E extends HSDBEntity>({
    apiInfo,
    data,
    onEdit,
    onDelete,
    isMethodAllowed = () => true,
    pageSize = 100,
}: DynamicResourceTableProps<E>) {
    const [sortKey, setSortKey] = useState<string | null>(null);
    const [sortDirection, setSortDirection] = useState<SortDirection>(null);
    const [currentPage, setCurrentPage] = useState(1);
    const confirm = useConfirm();

    // Generate columns from API info fields
    const columns = useMemo((): TeaTableColumn<E>[] => {
        const cols: TeaTableColumn<E>[] = [];

        // Add columns for each field in the schema
        for (const [fieldName, fieldSchema] of Object.entries(apiInfo.fields)) {
            if (fieldSchema.computed) continue; // Skip computed fields

            cols.push({
                key: fieldName,
                header: formatHeader(fieldName),
                sortable: true,
                render: (row) => {
                    const value = (row as Record<string, unknown>)[fieldName];
                    return formatValue(value, fieldSchema.type);
                },
            });
        }

        // Add actions column if edit or delete is allowed
        const canEdit = isMethodAllowed('PUT', false) || isMethodAllowed('PATCH', false);
        const canDelete = isMethodAllowed('DELETE', false);

        if ((canEdit && onEdit) || (canDelete && onDelete)) {
            cols.push({
                key: 'actions',
                header: 'Actions',
                className: 'actions',
                render: (entity) => (
                    <>
                        {canEdit && onEdit && (
                            <TeaButton
                                size='sm'
                                variant='secondary'
                                onClick={(e) => {
                                    e.stopPropagation();
                                    onEdit(entity);
                                }}
                            >
                                Edit
                            </TeaButton>
                        )}
                        {canDelete && onDelete && (
                            <TeaButton
                                size='sm'
                                variant='danger'
                                onClick={async (e) => {
                                    e.stopPropagation();
                                    const confirmed = await confirm({
                                        title: `Delete ${apiInfo.name}`,
                                        message: `Are you sure you want to delete this ${apiInfo.name.toLowerCase()}? This action cannot be undone.`,
                                        confirmLabel: 'Delete',
                                        variant: 'danger',
                                    });
                                    if (confirmed) {
                                        onDelete(entity.id);
                                    }
                                }}
                            >
                                Delete
                            </TeaButton>
                        )}
                    </>
                ),
            });
        }

        return cols;
    }, [apiInfo, onEdit, onDelete, isMethodAllowed, confirm]);

    // Sort data
    const sortedData = useMemo(() => {
        if (!sortKey || !sortDirection) {
            return data;
        }

        return [...data].sort((a, b) => {
            const aVal = (a as Record<string, unknown>)[sortKey] ?? '';
            const bVal = (b as Record<string, unknown>)[sortKey] ?? '';

            if (typeof aVal === 'number' && typeof bVal === 'number') {
                return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
            }

            const aStr = String(aVal).toLowerCase();
            const bStr = String(bVal).toLowerCase();
            if (sortDirection === 'asc') {
                return aStr.localeCompare(bStr);
            }
            return bStr.localeCompare(aStr);
        });
    }, [data, sortKey, sortDirection]);

    // Paginate data
    const totalPages = Math.ceil(sortedData.length / pageSize);
    const paginatedData = useMemo(() => {
        const start = (currentPage - 1) * pageSize;
        return sortedData.slice(start, start + pageSize);
    }, [sortedData, currentPage, pageSize]);

    const handleSort = (key: string, direction: 'asc' | 'desc' | null) => {
        if (direction === null) {
            setSortKey(null);
            setSortDirection(null);
        } else {
            setSortKey(key);
            setSortDirection(direction);
        }
        setCurrentPage(1);
    };

    return (
        <div className='dynamic-resource-table'>
            <TeaTable
                columns={columns}
                data={paginatedData}
                keyExtractor={(entity) => entity.id}
                sortKey={sortKey}
                sortDirection={sortDirection}
                onSort={handleSort}
                emptyMessage={`No ${apiInfo.name.toLowerCase()}s found`}
                clickableRows
            />

            {totalPages > 1 && (
                <TeaTablePagination
                    currentPage={currentPage}
                    totalPages={totalPages}
                    totalItems={data.length}
                    onPageChange={setCurrentPage}
                />
            )}
        </div>
    );
}

/**
 * Format a field name as a human-readable header
 */
function formatHeader(fieldName: string): string {
    return fieldName
        .replace(/_/g, ' ')
        .replace(/([a-z])([A-Z])/g, '$1 $2')
        .split(' ')
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

/**
 * Format a value based on its type
 */
function formatValue(value: unknown, type: string): string | React.ReactNode {
    if (value === null || value === undefined) {
        return '-';
    }

    switch (type.toLowerCase()) {
        case 'bool':
        case 'boolean':
            return value ? '✓' : '✗';
        case 'datetime':
        case 'dt':
            return new Date(value as string).toLocaleString();
        case 'date':
            return new Date(value as string).toLocaleDateString();
        case 'list':
        case 'array':
            return Array.isArray(value) ? value.join(', ') : String(value);
        case 'dict':
        case 'object':
            return typeof value === 'object' ? JSON.stringify(value) : String(value);
        default:
            return String(value);
    }
}

export default DynamicResourceTable;
