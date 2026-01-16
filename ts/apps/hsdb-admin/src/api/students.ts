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
