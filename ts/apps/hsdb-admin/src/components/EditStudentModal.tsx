/**
 * @license
 * Copyright (C) 2024-2026 Burak Günaydin
 */

import { useState, useEffect } from 'react';
import { Student } from '@/api/students';
import './EditStudentModal.scss';

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

    if (!student) return null;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSaving(true);
        try {
            await onSave(student.id, formData);
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

    return (
        <div className='modal-overlay' onClick={onClose}>
            <div className='modal' onClick={(e) => e.stopPropagation()}>
                <div className='modal__header'>
                    <h2>Edit Student</h2>
                    <button className='modal__close' onClick={onClose}>
                        ×
                    </button>
                </div>
                <form onSubmit={handleSubmit}>
                    <div className='modal__body'>
                        <div className='form-group'>
                            <label htmlFor='name'>Name</label>
                            <input
                                type='text'
                                id='name'
                                name='name'
                                value={formData.name}
                                onChange={handleChange}
                                required
                            />
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
                            <input
                                type='text'
                                id='school'
                                name='school'
                                value={formData.school}
                                onChange={handleChange}
                            />
                        </div>
                    </div>
                    <div className='modal__footer'>
                        <button type='button' className='btn btn--secondary' onClick={onClose} disabled={saving}>
                            Cancel
                        </button>
                        <button type='submit' className='btn btn--primary' disabled={saving}>
                            {saving ? 'Saving...' : 'Save Changes'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};
