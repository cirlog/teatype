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
import { useState } from 'react';
import { Toaster } from 'react-hot-toast';

// Components
import { StudentTable } from './components/StudentTable';
import { EditStudentModal } from './components/EditStudentModal';

// Hooks
import { useStudents } from './hooks/useStudents';
import { Student } from './api/students';

// Style
import './style/index.scss';

export default function App() {
    const { students, loading, error, refresh, updateStudent, deleteStudent } = useStudents();
    const [editingStudent, setEditingStudent] = useState<Student | null>(null);

    const handleEdit = (student: Student) => {
        setEditingStudent(student);
    };

    const handleSave = async (id: string, updates: Partial<Student>) => {
        await updateStudent(id, updates);
    };

    const handleCloseModal = () => {
        setEditingStudent(null);
    };

    const stats = {
        total: students.length,
        male: students.filter((s) => s.gender === 'male').length,
        female: students.filter((s) => s.gender === 'female').length,
        avgAge: students.length > 0 ? (students.reduce((sum, s) => sum + s.age, 0) / students.length).toFixed(1) : 0,
    };

    return (
        <div className='hsdb-dashboard'>
            <Toaster position='top-right' />

            <div className='hsdb-dashboard__stats'>
                <div className='stat-card'>
                    <p className='stat-card__label'>Total Students</p>
                    <h2 className='stat-card__value'>{stats.total}</h2>
                </div>
                <div className='stat-card'>
                    <p className='stat-card__label'>Male Students</p>
                    <h2 className='stat-card__value'>{stats.male}</h2>
                </div>
                <div className='stat-card'>
                    <p className='stat-card__label'>Female Students</p>
                    <h2 className='stat-card__value'>{stats.female}</h2>
                </div>
                <div className='stat-card'>
                    <p className='stat-card__label'>Average Age</p>
                    <h2 className='stat-card__value'>{stats.avgAge}</h2>
                </div>
            </div>

            <div className='hsdb-dashboard__content'>
                <div className='hsdb-dashboard__toolbar'>
                    <h2>Students</h2>
                    <div className='actions'>
                        <button className='btn btn--primary' onClick={refresh} disabled={loading}>
                            {loading ? 'Loading...' : 'Refresh'}
                        </button>
                    </div>
                </div>

                {loading && <div className='loading'>Loading students...</div>}

                {error && (
                    <div className='error'>
                        Error loading students: {error}
                        <button onClick={refresh}>Retry</button>
                    </div>
                )}

                {!loading && !error && (
                    <StudentTable students={students} onEdit={handleEdit} onDelete={deleteStudent} />
                )}
            </div>

            <EditStudentModal student={editingStudent} onSave={handleSave} onClose={handleCloseModal} />
        </div>
    );
}

export { App as HSDBAdmin };
