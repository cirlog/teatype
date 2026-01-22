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

// Components
import { TeaTable, TeaTableColumn, TeaTablePagination } from '@teatype/components';
import { TeaButton } from '@teatype/components';

// API
import { Student } from '../api/students';

interface StudentTableProps {
    students: Student[];
    onEdit: (student: Student) => void;
    onDelete: (id: string) => void;
}

type SortKey = 'name' | 'age' | 'gender' | 'height';
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

    const handleSort = (key: string) => {
        if (sortKey === key) {
            setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
        } else {
            setSortKey(key as SortKey);
            setSortDirection('asc');
        }
        setCurrentPage(1);
    };

    const columns: TeaTableColumn<Student>[] = [
        {
            key: 'name',
            header: 'Name',
            sortable: true,
        },
        {
            key: 'age',
            header: 'Age',
            sortable: true,
        },
        {
            key: 'gender',
            header: 'Gender',
            sortable: true,
        },
        {
            key: 'height',
            header: 'Height (cm)',
            sortable: true,
        },
        {
            key: 'actions',
            header: 'Actions',
            className: 'actions',
            render: (student) => (
                <>
                    <TeaButton size='sm' variant='secondary' onClick={() => onEdit(student)}>
                        Edit
                    </TeaButton>
                    <TeaButton
                        size='sm'
                        variant='danger'
                        onClick={() => {
                            if (confirm(`Delete ${student.name}?`)) {
                                onDelete(student.id);
                            }
                        }}
                    >
                        Delete
                    </TeaButton>
                </>
            ),
        },
    ];

    return (
        <div className='student-table'>
            <TeaTable
                columns={columns}
                data={paginatedStudents}
                keyExtractor={(student) => student.id}
                sortKey={sortKey}
                sortDirection={sortDirection}
                onSort={handleSort}
                emptyMessage='No students found'
                rowTooltip={(student) => <code>ID: {student.id}</code>}
            />

            {totalPages > 1 && (
                <TeaTablePagination
                    currentPage={currentPage}
                    totalPages={totalPages}
                    totalItems={students.length}
                    onPageChange={setCurrentPage}
                />
            )}
        </div>
    );
};
