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
import { Toaster } from 'react-hot-toast';
import { TeaConfirmProvider } from '@teatype/components';
import { useAPIRegistry } from '../hooks/useAPIRegistry';
import { DynamicResourceView } from './DynamicResourceView';

/**
 * A dynamic dashboard that auto-generates views for all resources
 * registered in the HSDB API Registry.
 *
 * @example
 * ```tsx
 * // Renders a complete admin dashboard for all registered models
 * <DynamicDashboard />
 * ```
 */
export function DynamicDashboard() {
    const { loading, error, apiInfos, refresh } = useAPIRegistry();
    const [selectedResource, setSelectedResource] = useState<string | null>(null);

    if (loading) {
        return (
            <div className='hsdb-dashboard hsdb-dashboard--loading'>
                <div className='loading'>Loading API Registry...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className='hsdb-dashboard hsdb-dashboard--error'>
                <div className='error'>
                    Failed to load API Registry: {error}
                    <button onClick={refresh}>Retry</button>
                </div>
            </div>
        );
    }

    // If no resource is selected, show the overview
    if (!selectedResource) {
        return (
            <TeaConfirmProvider>
                <div className='hsdb-dashboard'>
                    <Toaster position='top-right' />

                    <div className='hsdb-dashboard__header'>
                        <h1>HSDB Admin</h1>
                        <p>Select a resource to manage</p>
                    </div>

                    <div className='hsdb-dashboard__stats'>
                        {apiInfos.map((info) => (
                            <div
                                key={info.resource}
                                className='stat-card stat-card--clickable'
                                onClick={() => setSelectedResource(info.resource)}
                            >
                                <p className='stat-card__label'>{info.name}s</p>
                                <h2 className='stat-card__value'>{info.count}</h2>
                                <div className='stat-card__methods'>
                                    {info.allowedMethods.collection.map((m) => (
                                        <span key={m} className='method-badge method-badge--collection'>
                                            {m}
                                        </span>
                                    ))}
                                    {info.allowedMethods.resource.map((m) => (
                                        <span key={m} className='method-badge method-badge--resource'>
                                            {m}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className='hsdb-dashboard__info'>
                        <h3>Registered APIs</h3>
                        <table className='api-table'>
                            <thead>
                                <tr>
                                    <th>Model</th>
                                    <th>Resource</th>
                                    <th>Endpoint</th>
                                    <th>Count</th>
                                    <th>Fields</th>
                                </tr>
                            </thead>
                            <tbody>
                                {apiInfos.map((info) => (
                                    <tr
                                        key={info.resource}
                                        className='clickable'
                                        onClick={() => setSelectedResource(info.resource)}
                                    >
                                        <td>{info.name}</td>
                                        <td>
                                            <code>{info.resource}</code>
                                        </td>
                                        <td>
                                            <code>{info.endpoint}</code>
                                        </td>
                                        <td>{info.count}</td>
                                        <td>{Object.keys(info.fields).length} fields</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </TeaConfirmProvider>
        );
    }

    // Show the selected resource view
    return (
        <TeaConfirmProvider>
            <div className='hsdb-dashboard'>
                <Toaster position='top-right' />

                <div className='hsdb-dashboard__breadcrumb'>
                    <button className='btn btn--secondary' onClick={() => setSelectedResource(null)}>
                        ← Back to Dashboard
                    </button>
                </div>

                <DynamicResourceView resource={selectedResource} />
            </div>
        </TeaConfirmProvider>
    );
}

export default DynamicDashboard;
