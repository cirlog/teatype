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

import React from 'react';

import { buildFullUrl, QueryConfig } from '../api/query';

interface RequestPreviewProps {
    config: QueryConfig;
}

export const RequestPreview: React.FC<RequestPreviewProps> = ({ config }) => {
    const fullUrl = buildFullUrl(config);

    // Parse URL parts for display
    const methodColors: Record<string, string> = {
        GET: 'var(--success)',
        POST: 'var(--accent)',
        PUT: '#f59e0b',
        DELETE: '#ef4444',
        PATCH: '#8b5cf6',
    };

    return (
        <div className='request-preview'>
            <div className='request-preview__method' style={{ backgroundColor: methodColors[config.method] }}>
                {config.method}
            </div>
            <div className='request-preview__url'>
                <span className='request-preview__base'>{config.baseUrl}</span>
                <span className='request-preview__separator'>/</span>
                <span className='request-preview__endpoint'>{config.endpoint}</span>
                <span className='request-preview__separator'>/</span>
                <span className='request-preview__resource'>{config.resource || '?'}</span>
                {config.conditions.length > 0 && (
                    <span className='request-preview__query'>
                        {fullUrl.includes('?') ? fullUrl.substring(fullUrl.indexOf('?')) : ''}
                    </span>
                )}
            </div>
        </div>
    );
};

export default RequestPreview;
