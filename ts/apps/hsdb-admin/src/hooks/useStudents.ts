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
import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';

// API
import { Student, StudentAPI } from '../api/students';
import { HSDBFetchOptions, HSDBError } from '@teatype/api';

export const useStudents = () => {
    const [students, setStudents] = useState<Student[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchStudents = async (options?: HSDBFetchOptions) => {
        try {
            setLoading(true);
            setError(null);
            const response = await StudentAPI.fetchAll<Student>(options);
            setStudents(response.data);
        } catch (err) {
            const message = (err as HSDBError)?.message || 'Failed to fetch students';
            setError(message);
            toast.error(message);
        } finally {
            setLoading(false);
        }
    };

    const createStudent = async (student: Omit<Student, 'id'>) => {
        try {
            const response = await StudentAPI.create<Student>(student);
            setStudents((prev) => [...prev, response.data]);
            toast.success('Student created successfully');
            return response.data;
        } catch (err) {
            const message = (err as HSDBError)?.message || 'Failed to create student';
            toast.error(message);
            throw err;
        }
    };

    const updateStudent = async (id: string, updates: Partial<Student>) => {
        try {
            const response = await StudentAPI.update<Student>(id, updates, { partial: true });
            setStudents((prev) => prev.map((s) => (s.id === id ? response.data : s)));
            toast.success('Student updated successfully');
            return response.data;
        } catch (err) {
            const message = (err as HSDBError)?.message || 'Failed to update student';
            toast.error(message);
            throw err;
        }
    };

    const deleteStudent = async (id: string) => {
        try {
            await StudentAPI.delete(id);
            setStudents((prev) => prev.filter((s) => s.id !== id));
            toast.success('Student deleted successfully');
        } catch (err) {
            const message = (err as HSDBError)?.message || 'Failed to delete student';
            toast.error(message);
            throw err;
        }
    };

    useEffect(() => {
        fetchStudents();
    }, []);

    return {
        students,
        loading,
        error,
        refresh: fetchStudents,
        createStudent,
        updateStudent,
        deleteStudent,
    };
};
