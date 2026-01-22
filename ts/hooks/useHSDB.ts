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

// React imports
import { useState, useEffect, useCallback } from 'react';
import toast from 'react-hot-toast';

// API
import { HSDBBaseAPI, HSDBFetchOptions, HSDBError, HSDBEntity } from '@teatype/api';

/**
 * Configuration options for the useHSDB hook
 */
export interface UseHSDBOptions<T extends HSDBEntity> {
    /** The API class to use (must extend HSDBBaseAPI) */
    api: typeof HSDBBaseAPI;
    /** Initial fetch options */
    initialFetchOptions?: HSDBFetchOptions;
    /** Whether to auto-fetch on mount */
    autoFetch?: boolean;
    /** Custom success messages */
    messages?: {
        createSuccess?: string;
        updateSuccess?: string;
        deleteSuccess?: string;
        fetchError?: string;
        createError?: string;
        updateError?: string;
        deleteError?: string;
    };
    /** Transform function for fetched data */
    transform?: (data: T[]) => T[];
}

/**
 * Return type for the useHSDB hook
 */
export interface UseHSDBReturn<T extends HSDBEntity> {
    /** Current data array */
    data: T[];
    /** Loading state */
    loading: boolean;
    /** Error message if any */
    error: string | null;
    /** Refresh/refetch data */
    refresh: (options?: HSDBFetchOptions) => Promise<void>;
    /** Create a new entity */
    create: (entity: Omit<T, 'id'>) => Promise<T>;
    /** Update an existing entity */
    update: (id: string, updates: Partial<T>) => Promise<T>;
    /** Delete an entity */
    remove: (id: string) => Promise<void>;
    /** Set data manually */
    setData: React.Dispatch<React.SetStateAction<T[]>>;
}

/**
 * Generic hook for HSDB API operations
 *
 * @example
 * ```tsx
 * // Define your API class
 * class StudentAPI extends HSDBBaseAPI {
 *     static resource = 'students';
 * }
 *
 * // Use the hook
 * const { data, loading, error, refresh, create, update, remove } = useHSDB<Student>({
 *     api: StudentAPI,
 *     autoFetch: true,
 * });
 * ```
 */
export function useHSDB<T extends HSDBEntity>(options: UseHSDBOptions<T>): UseHSDBReturn<T> {
    const {
        api,
        initialFetchOptions,
        autoFetch = true,
        messages = {},
        transform,
    } = options;

    const [data, setData] = useState<T[]>([]);
    const [loading, setLoading] = useState(autoFetch);
    const [error, setError] = useState<string | null>(null);

    const defaultMessages = {
        createSuccess: 'Created successfully',
        updateSuccess: 'Updated successfully',
        deleteSuccess: 'Deleted successfully',
        fetchError: 'Failed to fetch data',
        createError: 'Failed to create',
        updateError: 'Failed to update',
        deleteError: 'Failed to delete',
        ...messages,
    };

    const fetchData = useCallback(async (fetchOptions?: HSDBFetchOptions) => {
        try {
            setLoading(true);
            setError(null);
            const response = await api.fetchAll<T>(fetchOptions);
            const resultData = transform ? transform(response.data) : response.data;
            setData(resultData);
        } catch (err) {
            const message = (err as HSDBError)?.message || defaultMessages.fetchError;
            setError(message);
            toast.error(message);
        } finally {
            setLoading(false);
        }
    }, [api, transform, defaultMessages.fetchError]);

    const create = useCallback(async (entity: Omit<T, 'id'>): Promise<T> => {
        try {
            const response = await api.create<T>(entity);
            setData((prev) => [...prev, response.data]);
            toast.success(defaultMessages.createSuccess);
            return response.data;
        } catch (err) {
            const message = (err as HSDBError)?.message || defaultMessages.createError;
            toast.error(message);
            throw err;
        }
    }, [api, defaultMessages.createSuccess, defaultMessages.createError]);

    const update = useCallback(async (id: string, updates: Partial<T>): Promise<T> => {
        try {
            const response = await api.update<T>(id, updates, { partial: true });
            setData((prev) => prev.map((item) => (item.id === id ? response.data : item)));
            toast.success(defaultMessages.updateSuccess);
            return response.data;
        } catch (err) {
            const message = (err as HSDBError)?.message || defaultMessages.updateError;
            toast.error(message);
            throw err;
        }
    }, [api, defaultMessages.updateSuccess, defaultMessages.updateError]);

    const remove = useCallback(async (id: string): Promise<void> => {
        try {
            await api.delete(id);
            setData((prev) => prev.filter((item) => item.id !== id));
            toast.success(defaultMessages.deleteSuccess);
        } catch (err) {
            const message = (err as HSDBError)?.message || defaultMessages.deleteError;
            toast.error(message);
            throw err;
        }
    }, [api, defaultMessages.deleteSuccess, defaultMessages.deleteError]);

    useEffect(() => {
        if (autoFetch) {
            fetchData(initialFetchOptions);
        }
    }, [autoFetch]); // Only run on mount

    return {
        data,
        loading,
        error,
        refresh: fetchData,
        create,
        update,
        remove,
        setData,
    };
}

export default useHSDB;
