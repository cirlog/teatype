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

// Components
import { TeaModal } from '@teatype/components';
import { TeaButton } from '@teatype/components';

// API
import { Student } from '../api/students';

interface EditStudentModalProps {
    student: Student | null;
    onSave: (id: string, updates: Partial<Student>) => Promise<void>;
    onClose: () => void;
}

export const EditStudentModal = ({ student, onSave, onClose }: EditStudentModalProps) => {
    const [formData, setFormData] = useState({
        name: '',
        age: 0,
        gender: '',
        height: 0,
        school: '',
    });
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        if (student) {
            setFormData({
                name: student.name,
                age: student.age,
                gender: student.gender,
                height: student.height,
                school: student.school || '',
            });
        }
    }, [student]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSaving(true);
        try {
            await onSave(student!.id, formData);
            onClose();
        } catch {
            // Error is handled by the hook
        } finally {
            setSaving(false);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value, type } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: type === 'number' ? parseInt(value, 10) || 0 : value,
        }));
    };

    const footerContent = (
        <>
            <TeaButton variant='secondary' onClick={onClose} disabled={saving}>
                Cancel
            </TeaButton>
            <TeaButton variant='primary' onClick={handleSubmit} disabled={saving}>
                {saving ? 'Saving...' : 'Save Changes'}
            </TeaButton>
        </>
    );

    return (
        <TeaModal isOpen={student !== null} onClose={onClose} title='Edit Student' footer={footerContent} size='md'>
            <form onSubmit={handleSubmit} className='hsdb-form'>
                <div className='form-group'>
                    <label htmlFor='name'>Name</label>
                    <input type='text' id='name' name='name' value={formData.name} onChange={handleChange} required />
                </div>
                <div className='form-group'>
                    <label htmlFor='age'>Age</label>
                    <input
                        type='number'
                        id='age'
                        name='age'
                        value={formData.age}
                        onChange={handleChange}
                        min={1}
                        max={150}
                        required
                    />
                </div>
                <div className='form-group'>
                    <label htmlFor='gender'>Gender</label>
                    <select id='gender' name='gender' value={formData.gender} onChange={handleChange} required>
                        <option value=''>Select...</option>
                        <option value='male'>Male</option>
                        <option value='female'>Female</option>
                    </select>
                </div>
                <div className='form-group'>
                    <label htmlFor='height'>Height (cm)</label>
                    <input
                        type='number'
                        id='height'
                        name='height'
                        value={formData.height}
                        onChange={handleChange}
                        min={1}
                        max={300}
                        required
                    />
                </div>
                <div className='form-group'>
                    <label htmlFor='school'>School ID</label>
                    <input type='text' id='school' name='school' value={formData.school} onChange={handleChange} />
                </div>
            </form>
        </TeaModal>
    );
};
