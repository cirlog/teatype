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
import { useMemo, useState } from 'react';

// API
import { Student } from '../api/students';

interface StudentTableProps {
    students: Student[];
    onEdit: (student: Student) => void;
    onDelete: (id: string) => void;
}

type SortKey = 'name' | 'age' | 'gender' | 'height' | 'school';
type SortDirection = 'asc' | 'desc';

const PAGE_SIZE = 100;

export const StudentTable = ({ students, onEdit, onDelete }: StudentTableProps) => {
    const [sortKey, setSortKey] = useState<SortKey>('name');
    const [sortDirection, setSortDirection] = useState<SortDirection>('asc');
    const [currentPage, setCurrentPage] = useState(1);

    const sortedStudents = useMemo(() => {
        return [...students].sort((a, b) => {
            const aVal = a[sortKey] ?? '';
            const bVal = b[sortKey] ?? '';

            if (typeof aVal === 'number' && typeof bVal === 'number') {
                return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
            }

            const aStr = String(aVal).toLowerCase();
            const bStr = String(bVal).toLowerCase();
            if (sortDirection === 'asc') {
                return aStr.localeCompare(bStr);
            }
            return bStr.localeCompare(aStr);
        });
    }, [students, sortKey, sortDirection]);

    const totalPages = Math.ceil(sortedStudents.length / PAGE_SIZE);
    const paginatedStudents = useMemo(() => {
        const start = (currentPage - 1) * PAGE_SIZE;
        return sortedStudents.slice(start, start + PAGE_SIZE);
    }, [sortedStudents, currentPage]);

    const handleSort = (key: SortKey) => {
        if (sortKey === key) {
            setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
        } else {
            setSortKey(key);
            setSortDirection('asc');
        }
        setCurrentPage(1);
    };

    const getSortIndicator = (key: SortKey) => {
        if (sortKey !== key) return ' ↕';
        return sortDirection === 'asc' ? ' ↑' : ' ↓';
    };

    return (
        <div className='student-table'>
            <table>
                <thead>
                    <tr>
                        <th className='sortable' onClick={() => handleSort('name')}>
                            Name{getSortIndicator('name')}
                        </th>
                        <th className='sortable' onClick={() => handleSort('age')}>
                            Age{getSortIndicator('age')}
                        </th>
                        <th className='sortable' onClick={() => handleSort('gender')}>
                            Gender{getSortIndicator('gender')}
                        </th>
                        <th className='sortable' onClick={() => handleSort('height')}>
                            Height (cm){getSortIndicator('height')}
                        </th>
                        <th className='sortable' onClick={() => handleSort('school')}>
                            School ID{getSortIndicator('school')}
                        </th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {paginatedStudents.map((student) => (
                        <tr key={student.id}>
                            <td>{student.name}</td>
                            <td>{student.age}</td>
                            <td>{student.gender}</td>
                            <td>{student.height}</td>
                            <td className='mono'>{student.school ? `${student.school.substring(0, 8)}...` : '-'}</td>
                            <td className='actions'>
                                <button className='btn btn--sm btn--edit' onClick={() => onEdit(student)}>
                                    Edit
                                </button>
                                <button
                                    className='btn btn--sm btn--delete'
                                    onClick={() => {
                                        if (confirm(`Delete ${student.name}?`)) {
                                            onDelete(student.id);
                                        }
                                    }}
                                >
                                    Delete
                                </button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>

            {students.length === 0 && (
                <div className='empty-state'>
                    <p>No students found</p>
                </div>
            )}

            {totalPages > 1 && (
                <div className='pagination'>
                    <button className='btn btn--sm' onClick={() => setCurrentPage(1)} disabled={currentPage === 1}>
                        ««
                    </button>
                    <button
                        className='btn btn--sm'
                        onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                        disabled={currentPage === 1}
                    >
                        «
                    </button>
                    <span className='pagination__info'>
                        Page {currentPage} of {totalPages} ({students.length} total)
                    </span>
                    <button
                        className='btn btn--sm'
                        onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                        disabled={currentPage === totalPages}
                    >
                        »
                    </button>
                    <button
                        className='btn btn--sm'
                        onClick={() => setCurrentPage(totalPages)}
                        disabled={currentPage === totalPages}
                    >
                        »»
                    </button>
                </div>
            )}
        </div>
    );
};
