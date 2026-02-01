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

import { useState, useEffect, useMemo } from 'react';
import { TeaModal, TeaButton } from '@teatype/components';
import { HSDBEntity, HSDBAPIInfo, HSDBFieldSchema } from '@teatype/api';

interface DynamicEditModalProps<E extends HSDBEntity> {
    /** API info for this resource */
    apiInfo: HSDBAPIInfo;
    /** Entity to edit (null for create mode) */
    entity: E | null;
    /** Called when save is requested */
    onSave: (id: string | null, data: Partial<E>) => Promise<void>;
    /** Called when modal is closed */
    onClose: () => void;
    /** Whether creating a new entity (vs editing) */
    createMode?: boolean;
}

/**
 * A dynamic edit modal that generates form fields based on HSDBAPIInfo schema.
 */
export function DynamicEditModal<E extends HSDBEntity>({
    apiInfo,
    entity,
    onSave,
    onClose,
    createMode = false,
}: DynamicEditModalProps<E>) {
    const [formData, setFormData] = useState<Record<string, unknown>>({});
    const [saving, setSaving] = useState(false);

    // Get editable fields (non-computed)
    const editableFields = useMemo(() => {
        return Object.entries(apiInfo.fields)
            .filter(([, schema]) => !schema.computed)
            .map(([name, schema]) => ({ name, schema }));
    }, [apiInfo.fields]);

    // Initialize form data from entity or defaults
    useEffect(() => {
        const initialData: Record<string, unknown> = {};

        for (const { name, schema } of editableFields) {
            if (entity) {
                initialData[name] =
                    (entity as Record<string, unknown>)[name] ?? schema.default ?? getDefaultValue(schema.type);
            } else {
                initialData[name] = schema.default ?? getDefaultValue(schema.type);
            }
        }

        setFormData(initialData);
    }, [entity, editableFields]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSaving(true);
        try {
            await onSave(entity?.id ?? null, formData as Partial<E>);
            onClose();
        } catch {
            // Error is handled by the parent
        } finally {
            setSaving(false);
        }
    };

    const handleChange = (fieldName: string, value: unknown, fieldType: string) => {
        let parsedValue = value;

        // Parse value based on type
        switch (fieldType.toLowerCase()) {
            case 'int':
            case 'integer':
                parsedValue = parseInt(value as string, 10) || 0;
                break;
            case 'float':
            case 'number':
                parsedValue = parseFloat(value as string) || 0;
                break;
            case 'bool':
            case 'boolean':
                parsedValue = value === 'true' || value === true;
                break;
        }

        setFormData((prev) => ({
            ...prev,
            [fieldName]: parsedValue,
        }));
    };

    const title = createMode ? `Create ${apiInfo.name}` : `Edit ${apiInfo.name}`;

    const footerContent = (
        <>
            <TeaButton variant='secondary' onClick={onClose} disabled={saving}>
                Cancel
            </TeaButton>
            <TeaButton variant='primary' onClick={handleSubmit} disabled={saving}>
                {saving ? 'Saving...' : createMode ? 'Create' : 'Save Changes'}
            </TeaButton>
        </>
    );

    return (
        <TeaModal
            isOpen={createMode || entity !== null}
            onClose={onClose}
            title={title}
            footer={footerContent}
            size='md'
        >
            <form onSubmit={handleSubmit} className='hsdb-form'>
                {editableFields.map(({ name, schema }) => (
                    <div className='form-group' key={name}>
                        <label htmlFor={name}>
                            {formatLabel(name)}
                            {schema.required && <span className='required'>*</span>}
                        </label>
                        {renderInput(name, schema, formData[name], handleChange)}
                    </div>
                ))}
            </form>
        </TeaModal>
    );
}

/**
 * Get default value for a field type
 */
function getDefaultValue(type: string): unknown {
    switch (type.toLowerCase()) {
        case 'int':
        case 'integer':
        case 'float':
        case 'number':
            return 0;
        case 'bool':
        case 'boolean':
            return false;
        case 'list':
        case 'array':
            return [];
        case 'dict':
        case 'object':
            return {};
        default:
            return '';
    }
}

/**
 * Format a field name as a human-readable label
 */
function formatLabel(fieldName: string): string {
    return fieldName
        .replace(/_/g, ' ')
        .replace(/([a-z])([A-Z])/g, '$1 $2')
        .split(' ')
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

/**
 * Render an input based on field schema
 */
function renderInput(
    name: string,
    schema: HSDBFieldSchema,
    value: unknown,
    onChange: (name: string, value: unknown, type: string) => void,
): React.ReactNode {
    const type = schema.type.toLowerCase();

    switch (type) {
        case 'bool':
        case 'boolean':
            return (
                <select
                    id={name}
                    name={name}
                    value={value ? 'true' : 'false'}
                    onChange={(e) => onChange(name, e.target.value, type)}
                    required={schema.required}
                >
                    <option value='false'>No</option>
                    <option value='true'>Yes</option>
                </select>
            );

        case 'int':
        case 'integer':
            return (
                <input
                    type='number'
                    id={name}
                    name={name}
                    value={value as number}
                    onChange={(e) => onChange(name, e.target.value, type)}
                    required={schema.required}
                    step='1'
                />
            );

        case 'float':
        case 'number':
            return (
                <input
                    type='number'
                    id={name}
                    name={name}
                    value={value as number}
                    onChange={(e) => onChange(name, e.target.value, type)}
                    required={schema.required}
                    step='any'
                />
            );

        case 'datetime':
        case 'dt':
            return (
                <input
                    type='datetime-local'
                    id={name}
                    name={name}
                    value={value ? formatDateTimeLocal(value as string) : ''}
                    onChange={(e) => onChange(name, e.target.value, type)}
                    required={schema.required}
                />
            );

        case 'date':
            return (
                <input
                    type='date'
                    id={name}
                    name={name}
                    value={value as string}
                    onChange={(e) => onChange(name, e.target.value, type)}
                    required={schema.required}
                />
            );

        case 'text':
            return (
                <textarea
                    id={name}
                    name={name}
                    value={value as string}
                    onChange={(e) => onChange(name, e.target.value, type)}
                    required={schema.required}
                    rows={4}
                />
            );

        default:
            return (
                <input
                    type='text'
                    id={name}
                    name={name}
                    value={value as string}
                    onChange={(e) => onChange(name, e.target.value, type)}
                    required={schema.required}
                />
            );
    }
}

/**
 * Format a date string for datetime-local input
 */
function formatDateTimeLocal(dateStr: string): string {
    const date = new Date(dateStr);
    return date.toISOString().slice(0, 16);
}

export default DynamicEditModal;
