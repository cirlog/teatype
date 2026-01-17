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

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

import {
    HSDBConfig,
    HSDBQueryParams,
    HSDBQueryCondition,
    HSDBSortOption,
    HSDBResponse,
    HSDBError,
    HSDBFetchOptions,
    HSDBCreateOptions,
    HSDBUpdateOptions,
    HSDBDeleteOptions,
    HSDBEntity,
    HSDBModelSchema,
} from './types';

/**
 * Default configuration for HSDB API
 */
const DEFAULT_CONFIG: Required<Omit<HSDBConfig, 'baseUrl' | 'authToken'>> = {
    protocol: 'http',
    host: 'localhost',
    port: 8080,
    endpoint: '',
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
};

/**
 * Build query string from HSDB query parameters
 */
export function buildQueryString(params: HSDBQueryParams): string {
    const urlParams = new URLSearchParams();

    // Add conditions
    if (params.conditions) {
        for (const condition of params.conditions) {
            if (!condition.field) continue;

            // Build key: field__operator or just field for 'eq'
            const key = condition.operator === 'eq'
                ? condition.field
                : `${condition.field}__${condition.operator}`;

            // Convert value to string
            const value = condition.value === null
                ? 'null'
                : String(condition.value);

            urlParams.append(key, value);
        }
    }

    // Add sort
    if (params.sort) {
        const sortValue = params.sort.direction === 'desc'
            ? `-${params.sort.field}`
            : params.sort.field;
        urlParams.append('sort', sortValue);
    }

    // Add pagination
    if (params.pagination) {
        urlParams.append('page', String(params.pagination.page));
        urlParams.append('page_size', String(params.pagination.pageSize));
    }

    // Add relation options
    if (params.includeRelations) {
        urlParams.append('include_relations', 'true');
    }
    if (params.expandRelations) {
        urlParams.append('expand_relations', 'true');
    }

    // Add ids only
    if (params.idsOnly) {
        urlParams.append('ids_only', 'true');
    }

    // Add fields filter
    if (params.fields && params.fields.length > 0) {
        urlParams.append('fields', params.fields.join(','));
    }

    const queryString = urlParams.toString();
    return queryString ? `?${queryString}` : '';
}

/**
 * Parse query string back to HSDB query parameters
 */
export function parseQueryString(queryString: string): HSDBQueryParams {
    const params: HSDBQueryParams = {};
    const urlParams = new URLSearchParams(queryString.replace(/^\?/, ''));

    const conditions: HSDBQueryCondition[] = [];
    const reservedParams = new Set([
        'sort', 'page', 'page_size', 'include_relations',
        'expand_relations', 'ids_only', 'fields'
    ]);

    urlParams.forEach((value, key) => {
        if (reservedParams.has(key)) return;

        // Parse field__operator or field (default: eq)
        const match = key.match(/^(.+?)__(eq|ne|gt|gte|lt|lte|contains|in)$/);
        const field = match ? match[1] : key;
        const operator = (match ? match[2] : 'eq') as HSDBQueryCondition['operator'];

        // Parse value type
        let parsedValue: string | number | boolean | null = value;
        if (value === 'null') {
            parsedValue = null;
        } else if (value === 'true') {
            parsedValue = true;
        } else if (value === 'false') {
            parsedValue = false;
        } else if (!isNaN(Number(value)) && value !== '') {
            parsedValue = Number(value);
        }

        conditions.push({ field, operator, value: parsedValue });
    });

    if (conditions.length > 0) {
        params.conditions = conditions;
    }

    // Parse sort
    const sort = urlParams.get('sort');
    if (sort) {
        params.sort = {
            field: sort.startsWith('-') ? sort.slice(1) : sort,
            direction: sort.startsWith('-') ? 'desc' : 'asc',
        };
    }

    // Parse pagination
    const page = urlParams.get('page');
    const pageSize = urlParams.get('page_size');
    if (page !== null && pageSize !== null) {
        params.pagination = {
            page: parseInt(page, 10),
            pageSize: parseInt(pageSize, 10),
        };
    }

    // Parse flags
    if (urlParams.get('include_relations') === 'true') {
        params.includeRelations = true;
    }
    if (urlParams.get('expand_relations') === 'true') {
        params.expandRelations = true;
    }
    if (urlParams.get('ids_only') === 'true') {
        params.idsOnly = true;
    }

    // Parse fields
    const fields = urlParams.get('fields');
    if (fields) {
        params.fields = fields.split(',');
    }

    return params;
}

/**
 * HSDB Base API Client
 * 
 * A configurable API client for interacting with HSDB backends.
 * Can be subclassed to create model-specific API clients.
 * 
 * @example
 * ```typescript
 * // Configure the global API client
 * HSDBBaseAPI.configure({
 *     host: 'localhost',
 *     port: 8080,
 *     endpoint: 'api/v1',
 * });
 * 
 * // Create a model-specific API
 * class StudentAPI extends HSDBBaseAPI {
 *     static resource = 'students';
 * }
 * 
 * // Use it
 * const students = await StudentAPI.fetchAll<Student>();
 * const student = await StudentAPI.fetchOne<Student>('123');
 * const newStudent = await StudentAPI.create<Student>({ name: 'John', age: 20 });
 * ```
 */
export class HSDBBaseAPI {
    /** Global configuration */
    private static _config: HSDBConfig = { ...DEFAULT_CONFIG };

    /** Axios instance */
    private static _axiosInstance: AxiosInstance | null = null;

    /** Resource name (override in subclass) */
    static resource: string = '';

    /**
     * Configure the global HSDB API client
     */
    static configure(config: HSDBConfig): void {
        this._config = { ...DEFAULT_CONFIG, ...config };
        this._axiosInstance = null; // Reset axios instance to pick up new config
    }

    /**
     * Get current configuration
     */
    static getConfig(): HSDBConfig {
        return { ...this._config };
    }

    /**
     * Get the base URL from configuration
     */
    static getBaseUrl(): string {
        if (this._config.baseUrl) {
            return this._config.baseUrl.replace(/\/$/, '');
        }

        const protocol = this._config.protocol || DEFAULT_CONFIG.protocol;
        const host = this._config.host || DEFAULT_CONFIG.host;
        const port = this._config.port || DEFAULT_CONFIG.port;

        return `${protocol}://${host}:${port}`;
    }

    /**
     * Get the full URL for a resource
     */
    static getResourceUrl(resource?: string): string {
        const base = this.getBaseUrl();
        const endpoint = (this._config.endpoint || '').replace(/^\/|\/$/g, '');
        const res = (resource || this.resource).replace(/^\/|\/$/g, '');

        const parts = [base];
        if (endpoint) parts.push(endpoint);
        if (res) parts.push(res);

        return parts.join('/');
    }

    /**
     * Get or create the axios instance
     */
    protected static getAxios(): AxiosInstance {
        if (!this._axiosInstance) {
            this._axiosInstance = axios.create({
                baseURL: this.getBaseUrl(),
                timeout: this._config.timeout || DEFAULT_CONFIG.timeout,
                headers: {
                    ...DEFAULT_CONFIG.headers,
                    ...this._config.headers,
                },
            });

            // Add auth token interceptor
            this._axiosInstance.interceptors.request.use((config) => {
                if (this._config.authToken) {
                    config.headers.Authorization = `Bearer ${this._config.authToken}`;
                }
                return config;
            });
        }
        return this._axiosInstance;
    }

    /**
     * Set auth token
     */
    static setAuthToken(token: string | undefined): void {
        this._config.authToken = token;
    }

    /**
     * Make a request and wrap the response
     */
    protected static async request<R>(
        config: AxiosRequestConfig,
        options?: { timeout?: number; headers?: Record<string, string> }
    ): Promise<HSDBResponse<R>> {
        const startTime = performance.now();

        try {
            const axiosConfig: AxiosRequestConfig = {
                ...config,
                timeout: options?.timeout || this._config.timeout,
                headers: {
                    ...config.headers,
                    ...options?.headers,
                },
            };

            const response: AxiosResponse<R> = await this.getAxios()(axiosConfig);
            const endTime = performance.now();

            return {
                data: response.data,
                status: response.status,
                statusText: response.statusText,
                headers: response.headers as Record<string, string>,
                timing: Math.round(endTime - startTime),
            };
        } catch (error) {
            if (axios.isAxiosError(error)) {
                const hsdbError: HSDBError = {
                    message: error.message,
                    status: error.response?.status || 0,
                    statusText: error.response?.statusText || 'Error',
                    data: error.response?.data,
                };
                throw hsdbError;
            }
            throw error;
        }
    }

    // ==================== CRUD Operations ====================

    /**
     * Fetch all entities of this resource type
     * 
     * @example
     * ```typescript
     * // Fetch all students
     * const response = await StudentAPI.fetchAll();
     * 
     * // Fetch with filters
     * const response = await StudentAPI.fetchAll({
     *     conditions: [{ field: 'age', operator: 'gte', value: 18 }],
     *     sort: { field: 'name', direction: 'asc' },
     *     includeRelations: true,
     * });
     * ```
     */
    static async fetchAll<E extends HSDBEntity = HSDBEntity>(
        options?: HSDBFetchOptions
    ): Promise<HSDBResponse<E[]>> {
        const url = this.getResourceUrl();
        const queryString = options ? buildQueryString(options) : '';

        return this.request<E[]>({
            method: 'GET',
            url: `${url}${queryString}`,
        }, options);
    }

    /**
     * Fetch a single entity by ID
     * 
     * @example
     * ```typescript
     * const response = await StudentAPI.fetchOne('123', { expandRelations: true });
     * ```
     */
    static async fetchOne<E extends HSDBEntity = HSDBEntity>(
        id: string,
        options?: HSDBFetchOptions
    ): Promise<HSDBResponse<E>> {
        const url = `${this.getResourceUrl()}/${id}`;
        const queryString = options ? buildQueryString(options) : '';

        return this.request<E>({
            method: 'GET',
            url: `${url}${queryString}`,
        }, options);
    }

    /**
     * Create a new entity
     * 
     * @example
     * ```typescript
     * const response = await StudentAPI.create({
     *     name: 'John Doe',
     *     age: 20,
     *     gender: 'male',
     * });
     * ```
     */
    static async create<E extends HSDBEntity = HSDBEntity>(
        data: Partial<E> | Record<string, unknown>,
        options?: HSDBCreateOptions
    ): Promise<HSDBResponse<E>> {
        const url = this.getResourceUrl();

        return this.request<E>({
            method: 'POST',
            url,
            data,
        }, options);
    }

    /**
     * Update an existing entity
     * 
     * @example
     * ```typescript
     * // Full update (PUT)
     * const response = await StudentAPI.update('123', { name: 'Jane Doe', age: 21 });
     * 
     * // Partial update (PATCH)
     * const response = await StudentAPI.update('123', { age: 22 }, { partial: true });
     * ```
     */
    static async update<E extends HSDBEntity = HSDBEntity>(
        id: string,
        data: Partial<E> | Record<string, unknown>,
        options?: HSDBUpdateOptions
    ): Promise<HSDBResponse<E>> {
        const url = `${this.getResourceUrl()}/${id}`;
        const method = options?.partial ? 'PATCH' : 'PUT';

        return this.request<E>({
            method,
            url,
            data,
        }, options);
    }

    /**
     * Delete an entity
     * 
     * @example
     * ```typescript
     * await StudentAPI.delete('123');
     * ```
     */
    static async delete(
        id: string,
        options?: HSDBDeleteOptions
    ): Promise<HSDBResponse<void>> {
        const url = `${this.getResourceUrl()}/${id}`;

        return this.request<void>({
            method: 'DELETE',
            url,
        }, options);
    }

    // ==================== Query Builder Methods ====================

    /**
     * Create a query builder for this resource
     * Returns a fluent interface for building queries
     * 
     * @example
     * ```typescript
     * const results = await StudentAPI.query()
     *     .where('age', 'gte', 18)
     *     .where('gender', 'eq', 'male')
     *     .sortBy('name', 'asc')
     *     .limit(10)
     *     .includeRelations()
     *     .execute();
     * ```
     */
    static query<E extends HSDBEntity = HSDBEntity>(): HSDBQueryBuilder<E> {
        return new HSDBQueryBuilder<E>(this);
    }

    // ==================== Schema/Metadata Methods ====================

    /**
     * Fetch the schema for this model
     */
    static async fetchSchema(): Promise<HSDBResponse<HSDBModelSchema>> {
        const baseUrl = this.getBaseUrl();
        const endpoint = (this._config.endpoint || '').replace(/^\/|\/$/g, '');

        // HSDB schema endpoint
        const url = endpoint
            ? `${baseUrl}/${endpoint}/hsdb/schema/${this.resource}`
            : `${baseUrl}/hsdb/schema/${this.resource}`;

        return this.request<HSDBModelSchema>({
            method: 'GET',
            url,
        });
    }

    /**
     * Fetch all available models from HSDB
     */
    static async fetchModels(): Promise<HSDBResponse<string[]>> {
        const baseUrl = this.getBaseUrl();
        const endpoint = (this._config.endpoint || '').replace(/^\/|\/$/g, '');

        const url = endpoint
            ? `${baseUrl}/${endpoint}/hsdb/models`
            : `${baseUrl}/hsdb/models`;

        return this.request<string[]>({
            method: 'GET',
            url,
        });
    }

    /**
     * Get the count of entities matching the query
     */
    static async count(options?: HSDBFetchOptions): Promise<HSDBResponse<number>> {
        // For now, fetch all and count - HSDB should add a dedicated count endpoint
        const response = await this.fetchAll({
            ...options,
            idsOnly: true,
        });

        return {
            ...response,
            data: Array.isArray(response.data) ? response.data.length : 0,
        };
    }
}

/**
 * Fluent query builder for HSDB queries
 */
export class HSDBQueryBuilder<T extends HSDBEntity = HSDBEntity> {
    private _apiClass: typeof HSDBBaseAPI;
    private _conditions: HSDBQueryCondition[] = [];
    private _sort?: HSDBSortOption;
    private _pagination?: { page: number; pageSize: number };
    private _includeRelations = false;
    private _expandRelations = false;
    private _idsOnly = false;
    private _fields?: string[];
    private _headers?: Record<string, string>;
    private _timeout?: number;

    constructor(apiClass: typeof HSDBBaseAPI) {
        this._apiClass = apiClass;
    }

    /**
     * Add a filter condition
     */
    where(field: string, operator: HSDBQueryCondition['operator'], value: HSDBQueryCondition['value']): this {
        this._conditions.push({ field, operator, value });
        return this;
    }

    /**
     * Shorthand for equals condition
     */
    eq(field: string, value: HSDBQueryCondition['value']): this {
        return this.where(field, 'eq', value);
    }

    /**
     * Shorthand for greater than condition
     */
    gt(field: string, value: HSDBQueryCondition['value']): this {
        return this.where(field, 'gt', value);
    }

    /**
     * Shorthand for greater than or equal condition
     */
    gte(field: string, value: HSDBQueryCondition['value']): this {
        return this.where(field, 'gte', value);
    }

    /**
     * Shorthand for less than condition
     */
    lt(field: string, value: HSDBQueryCondition['value']): this {
        return this.where(field, 'lt', value);
    }

    /**
     * Shorthand for less than or equal condition
     */
    lte(field: string, value: HSDBQueryCondition['value']): this {
        return this.where(field, 'lte', value);
    }

    /**
     * Shorthand for contains condition
     */
    contains(field: string, value: HSDBQueryCondition['value']): this {
        return this.where(field, 'contains', value);
    }

    /**
     * Set sort order
     */
    sortBy(field: string, direction: 'asc' | 'desc' = 'asc'): this {
        this._sort = { field, direction };
        return this;
    }

    /**
     * Set pagination
     */
    paginate(page: number, pageSize: number): this {
        this._pagination = { page, pageSize };
        return this;
    }

    /**
     * Set limit (page size with page 0)
     */
    limit(count: number): this {
        this._pagination = { page: 0, pageSize: count };
        return this;
    }

    /**
     * Include relation IDs in response
     */
    includeRelations(): this {
        this._includeRelations = true;
        return this;
    }

    /**
     * Expand relations to full objects
     */
    expandRelations(): this {
        this._expandRelations = true;
        this._includeRelations = true;
        return this;
    }

    /**
     * Return only IDs
     */
    idsOnly(): this {
        this._idsOnly = true;
        return this;
    }

    /**
     * Select specific fields
     */
    select(...fields: string[]): this {
        this._fields = fields;
        return this;
    }

    /**
     * Set custom headers
     */
    withHeaders(headers: Record<string, string>): this {
        this._headers = headers;
        return this;
    }

    /**
     * Set timeout
     */
    withTimeout(ms: number): this {
        this._timeout = ms;
        return this;
    }

    /**
     * Build the query parameters object
     */
    build(): HSDBFetchOptions {
        return {
            conditions: this._conditions.length > 0 ? this._conditions : undefined,
            sort: this._sort,
            pagination: this._pagination,
            includeRelations: this._includeRelations || undefined,
            expandRelations: this._expandRelations || undefined,
            idsOnly: this._idsOnly || undefined,
            fields: this._fields,
            headers: this._headers,
            timeout: this._timeout,
        };
    }

    /**
     * Build and return the query string
     */
    toQueryString(): string {
        return buildQueryString(this.build());
    }

    /**
     * Execute the query and return results
     */
    async execute(): Promise<HSDBResponse<T[]>> {
        return this._apiClass.fetchAll<T>(this.build());
    }

    /**
     * Execute and return first result
     */
    async first(): Promise<HSDBResponse<T | null>> {
        const response = await this.limit(1).execute();
        return {
            ...response,
            data: response.data.length > 0 ? response.data[0] : null,
        };
    }

    /**
     * Execute and return count
     */
    async count(): Promise<HSDBResponse<number>> {
        const response = await this.idsOnly().execute();
        return {
            ...response,
            data: response.data.length,
        };
    }
}

export default HSDBBaseAPI;
