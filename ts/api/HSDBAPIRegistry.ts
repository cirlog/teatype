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

import { HSDBBaseAPI } from './HSDBBaseAPI';
import { HSDBEntity, HSDBFetchOptions, HSDBCreateOptions, HSDBUpdateOptions, HSDBDeleteOptions, HSDBResponse } from './types';

/**
 * Field schema from the HSDB API registry
 */
export interface HSDBFieldSchema {
    type: string;
    required: boolean;
    indexed: boolean;
    unique: boolean;
    computed: boolean;
    default?: unknown;
}

/**
 * Relation schema from the HSDB API registry
 */
export interface HSDBRelationSchema {
    model: string;
    type: 'one' | 'many';
    backref?: string;
}

/**
 * Allowed methods configuration for collection and resource endpoints
 */
export interface HSDBAllowedMethods {
    collection: string[];
    resource: string[];
}

/**
 * API info returned from the HSDB registry endpoint
 */
export interface HSDBAPIInfo {
    name: string;
    resource: string;
    endpoint: string;
    count: number;
    allowedMethods: HSDBAllowedMethods;
    fields: Record<string, HSDBFieldSchema>;
    relations: Record<string, HSDBRelationSchema>;
}

/**
 * Response from the HSDB API registry endpoint
 */
export interface HSDBRegistryResponse {
    apis: HSDBAPIInfo[];
    baseEndpoint: string;
    timestamp: string;
}

/**
 * Dynamic API class interface
 */
export interface DynamicAPI<E extends HSDBEntity = HSDBEntity> {
    /** Resource name (e.g., 'students') */
    resource: string;
    /** API info from registry */
    info: HSDBAPIInfo;
    /** Fetch all entities */
    fetchAll: (options?: HSDBFetchOptions) => Promise<HSDBResponse<E[]>>;
    /** Fetch one entity by ID */
    fetchOne: (id: string, options?: HSDBFetchOptions) => Promise<HSDBResponse<E>>;
    /** Create a new entity */
    create: (data: Partial<E>, options?: HSDBCreateOptions) => Promise<HSDBResponse<E>>;
    /** Update an entity */
    update: (id: string, data: Partial<E>, options?: HSDBUpdateOptions) => Promise<HSDBResponse<E>>;
    /** Delete an entity */
    delete: (id: string, options?: HSDBDeleteOptions) => Promise<HSDBResponse<void>>;
    /** Check if method is allowed */
    isMethodAllowed: (method: string, isCollection?: boolean) => boolean;
}

/**
 * Create a dynamic API class for a given resource
 */
function createDynamicAPIClass(info: HSDBAPIInfo): new () => DynamicAPI {
    class DynamicAPIClass extends HSDBBaseAPI {
        static resource = info.resource;
        static info = info;

        constructor() {
            super();
        }

        get resource() {
            return info.resource;
        }

        get info() {
            return info;
        }

        isMethodAllowed(method: string, isCollection = true): boolean {
            const methods = isCollection ? info.allowedMethods.collection : info.allowedMethods.resource;
            return methods.includes(method.toUpperCase());
        }

        async fetchAll<E extends HSDBEntity = HSDBEntity>(options?: HSDBFetchOptions): Promise<HSDBResponse<E[]>> {
            if (!this.isMethodAllowed('GET', true)) {
                throw new Error(`GET method not allowed on collection for ${info.resource}`);
            }
            return DynamicAPIClass.fetchAll<E>(options);
        }

        async fetchOne<E extends HSDBEntity = HSDBEntity>(id: string, options?: HSDBFetchOptions): Promise<HSDBResponse<E>> {
            if (!this.isMethodAllowed('GET', false)) {
                throw new Error(`GET method not allowed on resource for ${info.resource}`);
            }
            return DynamicAPIClass.fetchOne<E>(id, options);
        }

        async create<E extends HSDBEntity = HSDBEntity>(data: Partial<E>, options?: HSDBCreateOptions): Promise<HSDBResponse<E>> {
            if (!this.isMethodAllowed('POST', true)) {
                throw new Error(`POST method not allowed for ${info.resource}`);
            }
            return DynamicAPIClass.create<E>(data, options);
        }

        async update<E extends HSDBEntity = HSDBEntity>(
            id: string,
            data: Partial<E>,
            options?: HSDBUpdateOptions
        ): Promise<HSDBResponse<E>> {
            const method = options?.partial ? 'PATCH' : 'PUT';
            if (!this.isMethodAllowed(method, false)) {
                throw new Error(`${method} method not allowed for ${info.resource}`);
            }
            return DynamicAPIClass.update<E>(id, data, options);
        }

        async delete(id: string, options?: HSDBDeleteOptions): Promise<HSDBResponse<void>> {
            if (!this.isMethodAllowed('DELETE', false)) {
                throw new Error(`DELETE method not allowed for ${info.resource}`);
            }
            return DynamicAPIClass.delete(id, options);
        }
    }

    return DynamicAPIClass as unknown as new () => DynamicAPI;
}

/**
 * HSDB API Registry
 * 
 * Manages dynamic API clients based on models registered with the HSDB server.
 * Fetches the API registry from the server and creates dynamic API clients
 * that respect allowed methods and provide type-safe operations.
 * 
 * @example
 * ```typescript
 * // Initialize the registry
 * await HSDBAPIRegistry.initialize();
 * 
 * // Get all available APIs
 * const apis = HSDBAPIRegistry.getAPIs();
 * 
 * // Get a specific API by resource name
 * const studentAPI = HSDBAPIRegistry.getAPI('students');
 * if (studentAPI) {
 *     const students = await studentAPI.fetchAll();
 * }
 * 
 * // Check if a method is allowed
 * if (studentAPI?.isMethodAllowed('DELETE', false)) {
 *     await studentAPI.delete('123');
 * }
 * ```
 */
export class HSDBAPIRegistry {
    private static _apis: Map<string, DynamicAPI> = new Map();
    private static _apiInfos: Map<string, HSDBAPIInfo> = new Map();
    private static _initialized = false;
    private static _baseEndpoint = '';
    private static _lastFetched: Date | null = null;

    /**
     * Initialize the registry by fetching API info from the server
     */
    static async initialize(registryEndpoint = 'hsdb/registry/'): Promise<void> {
        try {
            const url = HSDBBaseAPI.getResourceUrl(registryEndpoint);
            const response = await fetch(url);

            if (!response.ok) {
                throw new Error(`Failed to fetch API registry: ${response.status} ${response.statusText}`);
            }

            const data: HSDBRegistryResponse = await response.json();

            this._baseEndpoint = data.baseEndpoint;
            this._apis.clear();
            this._apiInfos.clear();

            for (const apiInfo of data.apis) {
                this._apiInfos.set(apiInfo.resource, apiInfo);
                const APIClass = createDynamicAPIClass(apiInfo);
                this._apis.set(apiInfo.resource, new APIClass());
            }

            this._initialized = true;
            this._lastFetched = new Date(data.timestamp);
        } catch (error) {
            console.error('Failed to initialize HSDB API Registry:', error);
            throw error;
        }
    }

    /**
     * Check if the registry is initialized
     */
    static isInitialized(): boolean {
        return this._initialized;
    }

    /**
     * Get the base endpoint from the server
     */
    static getBaseEndpoint(): string {
        return this._baseEndpoint;
    }

    /**
     * Get all registered APIs
     */
    static getAPIs(): Map<string, DynamicAPI> {
        if (!this._initialized) {
            console.warn('HSDBAPIRegistry not initialized. Call initialize() first.');
        }
        return new Map(this._apis);
    }

    /**
     * Get all API info objects
     */
    static getAPIInfos(): HSDBAPIInfo[] {
        return Array.from(this._apiInfos.values());
    }

    /**
     * Get a specific API by resource name
     */
    static getAPI<E extends HSDBEntity = HSDBEntity>(resource: string): DynamicAPI<E> | undefined {
        if (!this._initialized) {
            console.warn('HSDBAPIRegistry not initialized. Call initialize() first.');
        }
        return this._apis.get(resource) as DynamicAPI<E> | undefined;
    }

    /**
     * Get API info for a specific resource
     */
    static getAPIInfo(resource: string): HSDBAPIInfo | undefined {
        return this._apiInfos.get(resource);
    }

    /**
     * Get all resource names
     */
    static getResourceNames(): string[] {
        return Array.from(this._apis.keys());
    }

    /**
     * Check if a resource exists
     */
    static hasResource(resource: string): boolean {
        return this._apis.has(resource);
    }

    /**
     * Get the timestamp of the last registry fetch
     */
    static getLastFetched(): Date | null {
        return this._lastFetched;
    }

    /**
     * Refresh the registry from the server
     */
    static async refresh(registryEndpoint = 'hsdb/registry/'): Promise<void> {
        this._initialized = false;
        await this.initialize(registryEndpoint);
    }

    /**
     * Clear the registry
     */
    static clear(): void {
        this._apis.clear();
        this._apiInfos.clear();
        this._initialized = false;
        this._lastFetched = null;
    }
}

export default HSDBAPIRegistry;
