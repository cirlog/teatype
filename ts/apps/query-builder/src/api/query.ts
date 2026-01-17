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

export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';

export type QueryOperator =
    | 'equals'
    | 'not_equals'
    | 'contains'
    | 'starts_with'
    | 'ends_with'
    | 'greater_than'
    | 'less_than'
    | 'greater_or_equal'
    | 'less_or_equal'
    | 'in'
    | 'not_in'
    | 'is_null'
    | 'is_not_null';

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

export interface QueryConfig {
    method: HttpMethod;
    baseUrl: string;
    endpoint: string;
    resource: string;
    conditions: QueryCondition[];
    sort?: SortOption;
    limit?: number;
    offset?: number;
    body?: Record<string, unknown>;
}

export interface QueryResponse<T = unknown> {
    data: T;
    status: number;
    statusText: string;
    headers: Record<string, string>;
    timing: number;
}

export const HTTP_METHODS: HttpMethod[] = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'];

export const QUERY_OPERATORS: { value: QueryOperator; label: string }[] = [
    { value: 'equals', label: '=' },
    { value: 'not_equals', label: '!=' },
    { value: 'contains', label: 'Contains' },
    { value: 'starts_with', label: 'Starts with' },
    { value: 'ends_with', label: 'Ends with' },
    { value: 'greater_than', label: '>' },
    { value: 'less_than', label: '<' },
    { value: 'greater_or_equal', label: '>=' },
    { value: 'less_or_equal', label: '<=' },
    { value: 'in', label: 'In' },
    { value: 'not_in', label: 'Not In' },
    { value: 'is_null', label: 'Is Null' },
    { value: 'is_not_null', label: 'Is Not Null' },
];

export const DEFAULT_RESOURCES = [
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
];

export const buildQueryString = (config: QueryConfig): string => {
    const params = new URLSearchParams();

    // Add conditions as query params
    config.conditions.forEach((condition) => {
        if (condition.field && condition.value) {
            const key = `${condition.field}__${condition.operator}`;
            params.append(key, condition.value);
        }
    });

    // Add sort
    if (config.sort) {
        const sortValue = config.sort.direction === 'desc'
            ? `-${config.sort.field}`
            : config.sort.field;
        params.append('sort', sortValue);
    }

    // Add pagination
    if (config.limit) {
        params.append('limit', config.limit.toString());
    }
    if (config.offset) {
        params.append('offset', config.offset.toString());
    }

    const queryString = params.toString();
    return queryString ? `?${queryString}` : '';
};

export const buildFullUrl = (config: QueryConfig): string => {
    const base = config.baseUrl.replace(/\/$/, '');
    const endpoint = config.endpoint.replace(/^\/|\/$/g, '');
    const resource = config.resource.replace(/^\/|\/$/g, '');
    const queryString = buildQueryString(config);

    return `${base}/${endpoint}/${resource}${queryString}`;
};
