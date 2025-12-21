/**
 * @license
 * Copyright (C) 2024-2026 Burak Günaydin
 */

import { apiClient } from './client';

export interface Student {
    id: string;
    name: string;
    age: number;
    gender: string;
    height: number;
    school: string;
    created_at?: string;
    updated_at?: string;
}

export interface ApiListResponse<T> {
    results: T[];
    count: number;
}

// Student API
export const studentsApi = {
    getAll: async (): Promise<Student[]> => {
        const { data } = await apiClient.get<Student[]>('/students');
        return data;
    },

    getById: async (id: string): Promise<Student> => {
        const { data } = await apiClient.get<Student>(`/students/${id}`);
        return data;
    },

    create: async (student: Omit<Student, 'id'>): Promise<Student> => {
        const { data } = await apiClient.post<Student>('/students', student);
        return data;
    },

    update: async (id: string, student: Partial<Student>): Promise<Student> => {
        const { data } = await apiClient.put<Student>(`/students/${id}`, student);
        return data;
    },

    delete: async (id: string): Promise<void> => {
        await apiClient.delete(`/students/${id}`);
    },
};

// Generic API helper
export const createModelApi = <T>(endpoint: string) => ({
    getAll: async (): Promise<T[]> => {
        const { data } = await apiClient.get<T[]>(`/${endpoint}`);
        return data;
    },

    getById: async (id: string): Promise<T> => {
        const { data } = await apiClient.get<T>(`/${endpoint}/${id}`);
        return data;
    },

    create: async (item: Omit<T, 'id'>): Promise<T> => {
        const { data } = await apiClient.post<T>(`/${endpoint}`, item);
        return data;
    },

    update: async (id: string, item: Partial<T>): Promise<T> => {
        const { data } = await apiClient.put<T>(`/${endpoint}/${id}`, item);
        return data;
    },

    delete: async (id: string): Promise<void> => {
        await apiClient.delete(`/${endpoint}/${id}`);
    },
});
