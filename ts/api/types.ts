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

/**
 * Query operators supported by HSDB
 */
export type HSDBQueryOperator =
    | 'eq'      // equals (default, no suffix needed)
    | 'ne'      // not equals
    | 'gt'      // greater than
    | 'gte'     // greater than or equal
    | 'lt'      // less than
    | 'lte'     // less than or equal
    | 'contains'// contains (for arrays/strings)
    | 'in';     // in list

/**
 * A single query condition
 */
export interface HSDBQueryCondition {
    field: string;
    operator: HSDBQueryOperator;
    value: string | number | boolean | null;
}

/**
 * Sort configuration
 */
export interface HSDBSortOption {
    field: string;
    direction: 'asc' | 'desc';
}

/**
 * Pagination configuration
 */
export interface HSDBPagination {
    page: number;
    pageSize: number;
}

/**
 * Full query parameters for HSDB requests
 */
export interface HSDBQueryParams {
    /** Filter conditions */
    conditions?: HSDBQueryCondition[];
    /** Sort configuration */
    sort?: HSDBSortOption;
    /** Pagination */
    pagination?: HSDBPagination;
    /** Include relation IDs in response */
    includeRelations?: boolean;
    /** Expand relations to full objects */
    expandRelations?: boolean;
    /** Return only IDs */
    idsOnly?: boolean;
    /** Specific fields to return */
    fields?: string[];
}

/**
 * Configuration for HSDB API client
 */
export interface HSDBConfig {
    /** Protocol (http or https) */
    protocol?: 'http' | 'https';
    /** Server host */
    host?: string;
    /** Server port */
    port?: number;
    /** API endpoint prefix (e.g., 'api/v1') */
    endpoint?: string;
    /** Full base URL (overrides protocol, host, port if provided) */
    baseUrl?: string;
    /** Default timeout in ms */
    timeout?: number;
    /** Default headers */
    headers?: Record<string, string>;
    /** Auth token */
    authToken?: string;
}

/**
 * Standard HSDB API response wrapper
 */
export interface HSDBResponse<T> {
    data: T;
    status: number;
    statusText: string;
    headers: Record<string, string>;
    timing?: number;
}

/**
 * HSDB error response
 */
export interface HSDBError {
    message: string;
    status: number;
    statusText: string;
    data?: unknown;
}

/**
 * Options for fetch operations
 */
export interface HSDBFetchOptions extends HSDBQueryParams {
    /** Custom headers for this request */
    headers?: Record<string, string>;
    /** Request timeout override */
    timeout?: number;
}

/**
 * Options for create operations
 */
export interface HSDBCreateOptions {
    /** Custom headers for this request */
    headers?: Record<string, string>;
    /** Request timeout override */
    timeout?: number;
}

/**
 * Options for update operations
 */
export interface HSDBUpdateOptions {
    /** Custom headers for this request */
    headers?: Record<string, string>;
    /** Request timeout override */
    timeout?: number;
    /** Whether to do a partial update (PATCH) or full replace (PUT) */
    partial?: boolean;
}

/**
 * Options for delete operations
 */
export interface HSDBDeleteOptions {
    /** Custom headers for this request */
    headers?: Record<string, string>;
    /** Request timeout override */
    timeout?: number;
}

/**
 * Model schema returned by HSDB
 */
export interface HSDBModelSchema {
    name: string;
    fields: Record<string, {
        type: string;
        required?: boolean;
        indexed?: boolean;
        default?: unknown;
    }>;
    relations?: Record<string, {
        model: string;
        type: 'one' | 'many';
    }>;
}

/**
 * Base entity interface that all HSDB models extend
 */
export interface HSDBEntity {
    id: string;
    created_at?: string;
    updated_at?: string;
}
