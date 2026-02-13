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

type tStorageValue = string | number | boolean | object | null;
type tNestedObject = Record<string, unknown>;

/**
 * Navigates through a nested object using dot-notation path.
 * Returns [parentObject, finalKey] or null if path is invalid.
 */
const traversePath = (
    obj: tNestedObject,
    path: string[],
    createMissing = false,
): [tNestedObject, string] | null => {
    let current = obj;

    for (let i = 0; i < path.length - 1; i++) {
        const key = path[i];

        if (!(key in current)) {
            if (!createMissing) return null;
            current[key] = {};
        }

        const next = current[key];
        if (typeof next !== 'object' || next === null) {
            if (!createMissing) return null;
            current[key] = {};
        }

        current = current[key] as tNestedObject;
    }

    return [current, path[path.length - 1]];
};

/**
 * Retrieves a deeply nested value from an object using dot-notation path.
 */
const getNestedValue = (obj: tNestedObject, path: string[]): unknown => {
    let current: unknown = obj;

    for (const key of path) {
        if (current === null || typeof current !== 'object') return undefined;
        current = (current as tNestedObject)[key];
    }

    return current;
};

/**
 * Abstract base storage adapter defining the common interface.
 */
abstract class StorageAdapter {
    protected abstract read(rootKey: string): tNestedObject | null;
    protected abstract write(rootKey: string, data: tNestedObject): void;
    protected abstract delete(rootKey: string): void;
    protected abstract keys(): string[];

    /**
     * Retrieves a value by key. Supports dot-notation for nested access.
     */
    get<T = unknown>(key: string, fallback: T | null = null): T | null {
        try {
            const segments = key.split('.');
            const rootKey = segments[0];
            const data = this.read(rootKey);

            if (data === null) return fallback;

            if (segments.length === 1) {
                return (data as unknown as T) ?? fallback;
            }

            const value = getNestedValue(data, segments.slice(1));
            return (value as T) ?? fallback;
        } catch {
            return fallback;
        }
    }

    /**
     * Sets a value by key. Supports dot-notation for nested access.
     */
    set(key: string, value: tStorageValue): void {
        try {
            const segments = key.split('.');
            const rootKey = segments[0];

            if (segments.length === 1) {
                this.write(rootKey, value as tNestedObject);
                return;
            }

            const existing = this.read(rootKey) ?? {};
            const result = traversePath(existing, segments.slice(1), true);

            if (result) {
                const [parent, finalKey] = result;
                parent[finalKey] = value;
            }

            this.write(rootKey, existing);
        } catch (err) {
            console.error(`[Store] Failed to set key "${key}":`, err);
        }
    }

    /**
     * Removes a value by key. Supports dot-notation for nested access.
     */
    remove(key: string): void {
        try {
            const segments = key.split('.');
            const rootKey = segments[0];

            if (segments.length === 1) {
                this.delete(rootKey);
                return;
            }

            const data = this.read(rootKey);
            if (!data) return;

            const result = traversePath(data, segments.slice(1));
            if (result) {
                const [parent, finalKey] = result;
                delete parent[finalKey];
                this.write(rootKey, data);
            }
        } catch (err) {
            console.error(`[Store] Failed to remove key "${key}":`, err);
        }
    }

    /**
     * Checks if a key exists in storage.
     */
    has(key: string): boolean {
        return this.get(key) !== null;
    }

    /**
     * Returns all stored data as a flat object.
     */
    abstract all(): tNestedObject;

    /**
     * Clears all stored data.
     */
    abstract clear(): void;

    /**
     * Clears all keys that start with the given prefix.
     * @param prefix - The prefix to match (e.g., 'teatype' matches 'teatype.settings.theme')
     */
    clearByPrefix(prefix: string): void {
        const keysToRemove = this.keys().filter((key) => key.startsWith(prefix));
        for (const key of keysToRemove) {
            this.delete(key);
        }
    }

    /**
     * Returns all keys in storage.
     */
    getKeys(): string[] {
        return this.keys();
    }
}

/**
 * Browser storage adapter for localStorage/sessionStorage.
 */
class BrowserStorageAdapter extends StorageAdapter {
    constructor(private readonly storage: Storage) {
        super();
    }

    protected read(rootKey: string): tNestedObject | null {
        try {
            const raw = this.storage.getItem(rootKey);
            return raw ? JSON.parse(raw) : null;
        } catch {
            return null;
        }
    }

    protected write(rootKey: string, data: tNestedObject): void {
        this.storage.setItem(rootKey, JSON.stringify(data));
    }

    protected delete(rootKey: string): void {
        this.storage.removeItem(rootKey);
    }

    protected keys(): string[] {
        return Object.keys(this.storage);
    }

    all(): tNestedObject {
        const result: tNestedObject = {};

        for (const key of this.keys()) {
            try {
                const raw = this.storage.getItem(key);
                result[key] = raw ? JSON.parse(raw) : null;
            } catch {
                result[key] = null;
            }
        }

        return result;
    }

    clear(): void {
        this.storage.clear();
    }

    /**
     * Clears all keys that start with the given prefix.
     */
    clearByPrefix(prefix: string): void {
        const keysToRemove = this.keys().filter((key) => key.startsWith(prefix));
        for (const key of keysToRemove) {
            this.storage.removeItem(key);
        }
    }

    /**
     * Synchronizes storage with a new state, removing keys not present.
     */
    sync(newState: tNestedObject): void {
        const flatten = (obj: tNestedObject, prefix = ''): Record<string, unknown> => {
            return Object.entries(obj).reduce(
                (acc, [k, v]) => {
                    const path = prefix ? `${prefix}.${k}` : k;
                    if (v && typeof v === 'object' && !Array.isArray(v)) {
                        Object.assign(acc, flatten(v as tNestedObject, path));
                    } else {
                        acc[path] = v;
                    }
                    return acc;
                },
                {} as Record<string, unknown>,
            );
        };

        const currentFlat = flatten(this.all());
        const newFlat = flatten(newState);

        // Remove keys not in new state
        for (const key of Object.keys(currentFlat)) {
            if (!(key in newFlat)) {
                this.remove(key);
            }
        }

        // Set all keys from new state
        for (const [key, value] of Object.entries(newFlat)) {
            this.set(key, value as tStorageValue);
        }
    }
}

/**
 * In-memory storage adapter for runtime-only data.
 */
class MemoryStorageAdapter extends StorageAdapter {
    private data: tNestedObject = {};

    protected read(rootKey: string): tNestedObject | null {
        return (this.data[rootKey] as tNestedObject) ?? null;
    }

    protected write(rootKey: string, data: tNestedObject): void {
        this.data[rootKey] = data;
    }

    protected delete(rootKey: string): void {
        delete this.data[rootKey];
    }

    protected keys(): string[] {
        return Object.keys(this.data);
    }

    all(): tNestedObject {
        return { ...this.data };
    }

    clear(): void {
        this.data = {};
    }

    /**
     * Clears all keys that start with the given prefix.
     */
    clearByPrefix(prefix: string): void {
        const keysToRemove = this.keys().filter((key) => key.startsWith(prefix));
        for (const key of keysToRemove) {
            delete this.data[key];
        }
    }

    /**
     * Checks if memory storage is empty.
     */
    isEmpty(): boolean {
        return Object.keys(this.data).length === 0;
    }
}

/**
 * Unified storage interface providing access to local, session, and memory storage.
 *
 * @example
 * // Local storage (persistent)
 * Store.local.set('user.preferences.theme', 'dark');
 * Store.local.get('user.preferences.theme'); // 'dark'
 *
 * // Session storage (cleared on tab close)
 * Store.session.set('auth.token', 'abc123');
 *
 * // Memory storage (cleared on page refresh)
 * Store.memory.set('cache.data', { items: [] });
 */
const Store = {
    /** Persistent browser localStorage */
    local: new BrowserStorageAdapter(localStorage),

    /** Session-scoped browser sessionStorage */
    session: new BrowserStorageAdapter(sessionStorage),

    /** Runtime-only in-memory storage */
    memory: new MemoryStorageAdapter(),
} as const;

export default Store;

export { Store, StorageAdapter, BrowserStorageAdapter, MemoryStorageAdapter };

export type { tStorageValue, tNestedObject };