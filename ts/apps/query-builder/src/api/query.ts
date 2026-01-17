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

// Re-export types from the base API package
export type {
    HSDBQueryOperator,
    HSDBQueryCondition as HSDBCondition,
    HSDBSortOption,
    HSDBResponse,
} from '@teatype/api';

export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';

// Map between UI operators and HSDB operators
export type QueryOperator =
    | 'eq'          // equals
    | 'ne'          // not equals
    | 'contains'    // contains
    | 'gt'          // greater than
    | 'lt'          // less than
    | 'gte'         // greater than or equal
    | 'lte'         // less than or equal
    | 'in'          // in list
    | 'is_null'     // is null
    | 'is_not_null';// is not null

export interface QueryCondition {
    id: string;
    field: string;
    operator: QueryOperator;
    value: string;
}

export interface SortOption {
    field: string;
    direction: 'asc' | 'desc';
}

export interface RelationOptions {
    includeRelations: boolean;
    expandRelations: boolean;
}

export interface QueryConfig {
    method: HttpMethod;
    baseUrl: string;
    endpoint: string;
    resource: string;
    conditions: QueryCondition[];
    sort?: SortOption;
    limit?: number;
    offset?: number;
    page?: number;
    body?: Record<string, unknown>;
    relations?: RelationOptions;
}

export interface QueryResponse<T = unknown> {
    data: T;
    status: number;
    statusText: string;
    headers: Record<string, string>;
    timing: number;
}

export const HTTP_METHODS: HttpMethod[] = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'];

export const QUERY_OPERATORS: { value: QueryOperator; label: string; hsdbOperator: string }[] = [
    { value: 'eq', label: '=', hsdbOperator: 'eq' },
    { value: 'ne', label: '!=', hsdbOperator: 'ne' },
    { value: 'contains', label: 'Contains', hsdbOperator: 'contains' },
    { value: 'gt', label: '>', hsdbOperator: 'gt' },
    { value: 'lt', label: '<', hsdbOperator: 'lt' },
    { value: 'gte', label: '>=', hsdbOperator: 'gte' },
    { value: 'lte', label: '<=', hsdbOperator: 'lte' },
    { value: 'in', label: 'In', hsdbOperator: 'in' },
    { value: 'is_null', label: 'Is Null', hsdbOperator: 'eq' },      // value will be 'null'
    { value: 'is_not_null', label: 'Is Not Null', hsdbOperator: 'ne' }, // value will be 'null'
];

export const DEFAULT_RESOURCES = [
    'students',
    'universities',
    'users',
    'posts',
    'comments',
    'products',
    'orders',
    'customers',
];

export const DEFAULT_FIELDS = [
    'id',
    'name',
    'title',
    'description',
    'status',
    'created_at',
    'updated_at',
    'email',
    'type',
    'category',
    'age',
    'gender',
];

/**
 * Build query string from QueryConfig using HSDB format
 */
export const buildQueryString = (config: QueryConfig): string => {
    const params = new URLSearchParams();

    // Add conditions as query params using HSDB format
    config.conditions.forEach((condition) => {
        if (condition.field) {
            // Handle null operators specially
            if (condition.operator === 'is_null') {
                params.append(condition.field, 'null');
            } else if (condition.operator === 'is_not_null') {
                params.append(`${condition.field}__ne`, 'null');
            } else if (condition.value) {
                // For 'eq' operator, don't add suffix (HSDB default)
                const key = condition.operator === 'eq'
                    ? condition.field
                    : `${condition.field}__${condition.operator}`;
                params.append(key, condition.value);
            }
        }
    });

    // Add sort (HSDB format: -field for desc, field for asc)
    if (config.sort) {
        const sortValue = config.sort.direction === 'desc'
            ? `-${config.sort.field}`
            : config.sort.field;
        params.append('sort', sortValue);
    }

    // Add pagination (HSDB uses page + page_size)
    if (config.page !== undefined) {
        params.append('page', config.page.toString());
    }
    if (config.limit) {
        params.append('page_size', config.limit.toString());
    }
    if (config.offset) {
        params.append('offset', config.offset.toString());
    }

    // Add relation options
    if (config.relations?.includeRelations) {
        params.append('include_relations', 'true');
    }
    if (config.relations?.expandRelations) {
        params.append('expand_relations', 'true');
    }

    const queryString = params.toString();
    return queryString ? `?${queryString}` : '';
};

export const buildFullUrl = (config: QueryConfig): string => {
    const base = config.baseUrl.replace(/\/$/, '');
    const endpoint = config.endpoint.replace(/^\/|\/$/g, '');
    const resource = config.resource.replace(/^\/|\/$/g, '');
    const queryString = buildQueryString(config);

    // Build URL parts
    const parts = [base];
    if (endpoint) parts.push(endpoint);
    if (resource) parts.push(resource);

    return parts.join('/') + queryString;
};
