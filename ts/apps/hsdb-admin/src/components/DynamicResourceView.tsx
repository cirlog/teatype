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

import { useState } from 'react';
import { HSDBEntity } from '@teatype/api';
import { useDynamicResource } from '../hooks/useAPIRegistry';
import { DynamicResourceTable } from './DynamicResourceTable';
import { DynamicEditModal } from './DynamicEditModal';

interface DynamicResourceViewProps {
    /** Resource name (e.g., 'students') */
    resource: string;
}

/**
 * A complete dynamic view for any HSDB resource.
 *
 * Renders a table with data fetched from the server, with edit/delete actions
 * based on allowed methods from the API registry.
 *
 * @example
 * ```tsx
 * // Render a complete CRUD interface for students
 * <DynamicResourceView resource="students" />
 *
 * // Render a complete CRUD interface for universities
 * <DynamicResourceView resource="universities" />
 * ```
 */
export function DynamicResourceView<E extends HSDBEntity = HSDBEntity>({ resource }: DynamicResourceViewProps) {
    const { data, loading, error, apiInfo, exists, refresh, create, update, remove, isMethodAllowed } =
        useDynamicResource<E>(resource);

    const [editingEntity, setEditingEntity] = useState<E | null>(null);
    const [isCreating, setIsCreating] = useState(false);

    if (!exists) {
        return (
            <div className='dynamic-resource-view dynamic-resource-view--error'>
                <p>Resource "{resource}" not found in API registry.</p>
            </div>
        );
    }

    if (!apiInfo) {
        return (
            <div className='dynamic-resource-view dynamic-resource-view--loading'>
                <p>Loading API info...</p>
            </div>
        );
    }

    const handleEdit = (entity: E) => {
        setEditingEntity(entity);
    };

    const handleSave = async (id: string | null, entityData: Partial<E>) => {
        if (id) {
            await update(id, entityData);
        } else {
            await create(entityData);
        }
    };

    const handleCloseModal = () => {
        setEditingEntity(null);
        setIsCreating(false);
    };

    const canCreate = isMethodAllowed('POST', true);

    return (
        <div className='dynamic-resource-view'>
            <div className='dynamic-resource-view__toolbar'>
                <h2>{apiInfo.name}s</h2>
                <div className='actions'>
                    {canCreate && (
                        <button className='btn btn--accent' onClick={() => setIsCreating(true)}>
                            Create {apiInfo.name}
                        </button>
                    )}
                    <button className='btn btn--primary' onClick={() => refresh()} disabled={loading}>
                        {loading ? 'Loading...' : 'Refresh'}
                    </button>
                </div>
            </div>

            {loading && <div className='loading'>Loading {apiInfo.name.toLowerCase()}s...</div>}

            {error && (
                <div className='error'>
                    Error loading {apiInfo.name.toLowerCase()}s: {error}
                    <button onClick={() => refresh()}>Retry</button>
                </div>
            )}

            {!loading && !error && (
                <DynamicResourceTable
                    apiInfo={apiInfo}
                    data={data}
                    onEdit={handleEdit}
                    onDelete={remove}
                    isMethodAllowed={isMethodAllowed}
                />
            )}

            {/* Edit Modal */}
            {editingEntity && (
                <DynamicEditModal
                    apiInfo={apiInfo}
                    entity={editingEntity}
                    onSave={handleSave}
                    onClose={handleCloseModal}
                />
            )}

            {/* Create Modal */}
            {isCreating && (
                <DynamicEditModal
                    apiInfo={apiInfo}
                    entity={null}
                    onSave={handleSave}
                    onClose={handleCloseModal}
                    createMode
                />
            )}
        </div>
    );
}

export default DynamicResourceView;
