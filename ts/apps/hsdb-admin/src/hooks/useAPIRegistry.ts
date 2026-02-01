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

import { useState, useEffect, useCallback } from 'react';
import toast from 'react-hot-toast';
import {
    HSDBAPIRegistry,
    HSDBAPIInfo,
    DynamicAPI,
    HSDBEntity,
    HSDBError,
    HSDBFetchOptions,
} from '@teatype/api';

interface UseAPIRegistryResult {
    /** Whether the registry is loading */
    loading: boolean;
    /** Error message if loading failed */
    error: string | null;
    /** Whether the registry is initialized */
    initialized: boolean;
    /** All available APIs */
    apis: Map<string, DynamicAPI>;
    /** All API info objects */
    apiInfos: HSDBAPIInfo[];
    /** All resource names */
    resourceNames: string[];
    /** Get a specific API by resource name */
    getAPI: <E extends HSDBEntity = HSDBEntity>(resource: string) => DynamicAPI<E> | undefined;
    /** Get API info by resource name */
    getAPIInfo: (resource: string) => HSDBAPIInfo | undefined;
    /** Refresh the registry */
    refresh: () => Promise<void>;
}

/**
 * Hook to access the HSDB API Registry
 * 
 * Initializes the registry on mount and provides access to all dynamic APIs.
 * 
 * @example
 * ```tsx
 * function Dashboard() {
 *     const { loading, apis, apiInfos, getAPI } = useAPIRegistry();
 *     
 *     if (loading) return <div>Loading APIs...</div>;
 *     
 *     // List all available resources
 *     return (
 *         <ul>
 *             {apiInfos.map(info => (
 *                 <li key={info.resource}>
 *                     {info.name} ({info.count} items)
 *                 </li>
 *             ))}
 *         </ul>
 *     );
 * }
 * ```
 */
export function useAPIRegistry(): UseAPIRegistryResult {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [initialized, setInitialized] = useState(HSDBAPIRegistry.isInitialized());
    const [apis, setApis] = useState<Map<string, DynamicAPI>>(new Map());
    const [apiInfos, setApiInfos] = useState<HSDBAPIInfo[]>([]);
    const [resourceNames, setResourceNames] = useState<string[]>([]);

    const loadRegistry = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);

            if (!HSDBAPIRegistry.isInitialized()) {
                await HSDBAPIRegistry.initialize();
            }

            setApis(HSDBAPIRegistry.getAPIs());
            setApiInfos(HSDBAPIRegistry.getAPIInfos());
            setResourceNames(HSDBAPIRegistry.getResourceNames());
            setInitialized(true);
        } catch (err) {
            const message = (err as Error)?.message || 'Failed to load API registry';
            setError(message);
            toast.error(message);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        loadRegistry();
    }, [loadRegistry]);

    const refresh = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            await HSDBAPIRegistry.refresh();
            setApis(HSDBAPIRegistry.getAPIs());
            setApiInfos(HSDBAPIRegistry.getAPIInfos());
            setResourceNames(HSDBAPIRegistry.getResourceNames());
            toast.success('API registry refreshed');
        } catch (err) {
            const message = (err as Error)?.message || 'Failed to refresh API registry';
            setError(message);
            toast.error(message);
        } finally {
            setLoading(false);
        }
    }, []);

    const getAPI = useCallback(<E extends HSDBEntity = HSDBEntity>(resource: string) => {
        return HSDBAPIRegistry.getAPI<E>(resource);
    }, []);

    const getAPIInfo = useCallback((resource: string) => {
        return HSDBAPIRegistry.getAPIInfo(resource);
    }, []);

    return {
        loading,
        error,
        initialized,
        apis,
        apiInfos,
        resourceNames,
        getAPI,
        getAPIInfo,
        refresh,
    };
}

interface UseDynamicResourceResult<E extends HSDBEntity> {
    /** Data from the resource */
    data: E[];
    /** Whether data is loading */
    loading: boolean;
    /** Error message if any */
    error: string | null;
    /** API info for this resource */
    apiInfo: HSDBAPIInfo | undefined;
    /** Whether the resource API exists */
    exists: boolean;
    /** Refresh data */
    refresh: (options?: HSDBFetchOptions) => Promise<void>;
    /** Create a new entity */
    create: (data: Partial<E>) => Promise<E | undefined>;
    /** Update an entity */
    update: (id: string, data: Partial<E>) => Promise<E | undefined>;
    /** Delete an entity */
    remove: (id: string) => Promise<boolean>;
    /** Check if a method is allowed */
    isMethodAllowed: (method: string, isCollection?: boolean) => boolean;
}

/**
 * Hook to interact with a dynamic HSDB resource
 * 
 * Automatically fetches data and provides CRUD operations based on allowed methods.
 * 
 * @example
 * ```tsx
 * function StudentList() {
 *     const {
 *         data: students,
 *         loading,
 *         create,
 *         update,
 *         remove,
 *         isMethodAllowed
 *     } = useDynamicResource<Student>('students');
 *     
 *     if (loading) return <div>Loading...</div>;
 *     
 *     return (
 *         <div>
 *             {isMethodAllowed('POST') && (
 *                 <button onClick={() => create({ name: 'New Student' })}>
 *                     Add Student
 *                 </button>
 *             )}
 *             <ul>
 *                 {students.map(student => (
 *                     <li key={student.id}>
 *                         {student.name}
 *                         {isMethodAllowed('DELETE', false) && (
 *                             <button onClick={() => remove(student.id)}>Delete</button>
 *                         )}
 *                     </li>
 *                 ))}
 *             </ul>
 *         </div>
 *     );
 * }
 * ```
 */
export function useDynamicResource<E extends HSDBEntity = HSDBEntity>(
    resource: string,
    autoFetch = true
): UseDynamicResourceResult<E> {
    const [data, setData] = useState<E[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const { initialized, getAPI, getAPIInfo } = useAPIRegistry();

    const api = getAPI<E>(resource);
    const apiInfo = getAPIInfo(resource);
    const exists = !!api;

    const fetchData = useCallback(async (options?: HSDBFetchOptions) => {
        if (!api) {
            setLoading(false);
            setError(`Resource '${resource}' not found in API registry`);
            return;
        }

        try {
            setLoading(true);
            setError(null);
            const response = await api.fetchAll(options);
            setData(response.data as E[]);
        } catch (err) {
            const message = (err as HSDBError)?.message || `Failed to fetch ${resource}`;
            setError(message);
            toast.error(message);
        } finally {
            setLoading(false);
        }
    }, [api, resource]);

    useEffect(() => {
        if (initialized && autoFetch && api) {
            fetchData();
        } else if (initialized && !api) {
            setLoading(false);
            setError(`Resource '${resource}' not found`);
        }
    }, [initialized, autoFetch, api, fetchData, resource]);

    const create = useCallback(async (entityData: Partial<E>): Promise<E | undefined> => {
        if (!api) {
            toast.error(`Resource '${resource}' not found`);
            return undefined;
        }

        try {
            const response = await api.create(entityData);
            const newEntity = response.data as E;
            setData((prev) => [...prev, newEntity]);
            toast.success(`${resource} created successfully`);
            return newEntity;
        } catch (err) {
            const message = (err as HSDBError)?.message || `Failed to create ${resource}`;
            toast.error(message);
            throw err;
        }
    }, [api, resource]);

    const update = useCallback(async (id: string, entityData: Partial<E>): Promise<E | undefined> => {
        if (!api) {
            toast.error(`Resource '${resource}' not found`);
            return undefined;
        }

        try {
            const response = await api.update(id, entityData, { partial: true });
            const updatedEntity = response.data as E;
            setData((prev) => prev.map((item) => (item.id === id ? updatedEntity : item)));
            toast.success(`${resource} updated successfully`);
            return updatedEntity;
        } catch (err) {
            const message = (err as HSDBError)?.message || `Failed to update ${resource}`;
            toast.error(message);
            throw err;
        }
    }, [api, resource]);

    const remove = useCallback(async (id: string): Promise<boolean> => {
        if (!api) {
            toast.error(`Resource '${resource}' not found`);
            return false;
        }

        try {
            await api.delete(id);
            setData((prev) => prev.filter((item) => item.id !== id));
            toast.success(`${resource} deleted successfully`);
            return true;
        } catch (err) {
            const message = (err as HSDBError)?.message || `Failed to delete ${resource}`;
            toast.error(message);
            throw err;
        }
    }, [api, resource]);

    const isMethodAllowed = useCallback((method: string, isCollection = true): boolean => {
        return api?.isMethodAllowed(method, isCollection) ?? false;
    }, [api]);

    return {
        data,
        loading,
        error,
        apiInfo,
        exists,
        refresh: fetchData,
        create,
        update,
        remove,
        isMethodAllowed,
    };
}

export default useAPIRegistry;
