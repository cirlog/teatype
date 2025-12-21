/**
 * @license
 * Copyright (C) 2024-2026 Burak Günaydin
 */

import { Student } from '@/api/students';
import './StudentTable.scss';

interface StudentTableProps {
    students: Student[];
    onEdit: (student: Student) => void;
    onDelete: (id: string) => void;
}

export const StudentTable = ({ students, onEdit, onDelete }: StudentTableProps) => {
    return (
        <div className='student-table'>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Age</th>
                        <th>Gender</th>
                        <th>Height (cm)</th>
                        <th>School ID</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {students.map((student) => (
                        <tr key={student.id}>
                            <td>{student.name}</td>
                            <td>{student.age}</td>
                            <td>{student.gender}</td>
                            <td>{student.height}</td>
                            <td className='mono'>{student.school.substring(0, 8)}...</td>
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
        </div>
    );
};
