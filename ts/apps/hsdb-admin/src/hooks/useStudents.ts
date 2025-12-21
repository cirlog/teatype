/**
 * @license
 * Copyright (C) 2024-2026 Burak Günaydin
 */

import { useState, useEffect } from 'react';
import { Student, studentsApi } from '@/api/students';
import toast from 'react-hot-toast';

export const useStudents = () => {
    const [students, setStudents] = useState<Student[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchStudents = async () => {
        try {
            setLoading(true);
            setError(null);
            const data = await studentsApi.getAll();
            setStudents(data);
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to fetch students';
            setError(message);
            toast.error(message);
        } finally {
            setLoading(false);
        }
    };

    const createStudent = async (student: Omit<Student, 'id'>) => {
        try {
            const newStudent = await studentsApi.create(student);
            setStudents((prev) => [...prev, newStudent]);
            toast.success('Student created successfully');
            return newStudent;
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to create student';
            toast.error(message);
            throw err;
        }
    };

    const updateStudent = async (id: string, updates: Partial<Student>) => {
        try {
            const updated = await studentsApi.update(id, updates);
            setStudents((prev) => prev.map((s) => (s.id === id ? updated : s)));
            toast.success('Student updated successfully');
            return updated;
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to update student';
            toast.error(message);
            throw err;
        }
    };

    const deleteStudent = async (id: string) => {
        try {
            await studentsApi.delete(id);
            setStudents((prev) => prev.filter((s) => s.id !== id));
            toast.success('Student deleted successfully');
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to delete student';
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
