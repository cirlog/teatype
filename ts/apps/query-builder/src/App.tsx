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
import { QueryConditionRow } from './components/QueryConditionRow';
import { ResponseTable } from './components/ResponseTable';
import { RequestPreview } from './components/RequestPreview';

// Hooks
import { useQueryBuilder } from './hooks/useQueryBuilder';

// API types
import { HTTP_METHODS, DEFAULT_RESOURCES, DEFAULT_FIELDS } from './api/query';

// Style
import './style/index.scss';

export default function App() {
    const {
        config,
        response,
        loading,
        canExecute,
        setMethod,
        setBaseUrl,
        setEndpoint,
        setResource,
        setLimit,
        setOffset,
        addCondition,
        updateCondition,
        removeCondition,
        execute,
        reset,
        clearResponse,
    } = useQueryBuilder();

    const [showAdvanced, setShowAdvanced] = useState(false);

    return (
        <div className='query-builder'>
            <Toaster position='top-right' />

            {/* Main Content */}
            <div className='query-builder__content'>
                {/* Builder Panel */}
                <div className='query-builder__panel query-builder__panel--builder'>
                    <div className='query-builder__panel-header'>
                        <h2>Request Builder</h2>
                    </div>

                    {/* Basic Config */}
                    <div className='query-builder__section'>
                        <div className='query-builder__row'>
                            <div className='form-group'>
                                <label htmlFor='method'>Method</label>
                                <select
                                    id='method'
                                    value={config.method}
                                    onChange={(e) => setMethod(e.target.value as typeof config.method)}
                                >
                                    {HTTP_METHODS.map((m) => (
                                        <option key={m} value={m}>
                                            {m}
                                        </option>
                                    ))}
                                </select>
                            </div>
                            <div className='form-group'>
                                <label htmlFor='resource'>Resource</label>
                                <select
                                    id='resource'
                                    value={config.resource}
                                    onChange={(e) => setResource(e.target.value)}
                                >
                                    <option value=''>Select resource...</option>
                                    {DEFAULT_RESOURCES.map((r) => (
                                        <option key={r} value={r}>
                                            {r}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        <div className='form-group'>
                            <label htmlFor='baseUrl'>Base URL</label>
                            <input
                                type='text'
                                id='baseUrl'
                                value={config.baseUrl}
                                onChange={(e) => setBaseUrl(e.target.value)}
                                placeholder='http://localhost:8080'
                            />
                        </div>

                        <div className='form-group'>
                            <label htmlFor='endpoint'>Endpoint</label>
                            <input
                                type='text'
                                id='endpoint'
                                value={config.endpoint}
                                onChange={(e) => setEndpoint(e.target.value)}
                                placeholder='api/v1'
                            />
                        </div>
                    </div>

                    {/* Conditions */}
                    <div className='query-builder__section'>
                        <div className='query-builder__section-header'>
                            <h3>Query Conditions</h3>
                            <button className='btn btn--primary btn--sm' onClick={addCondition}>
                                + Add Condition
                            </button>
                        </div>

                        {config.conditions.length === 0 ? (
                            <p className='query-builder__empty-hint'>
                                No conditions yet. Click "Add Condition" to filter your query.
                            </p>
                        ) : (
                            <div className='query-builder__conditions'>
                                {config.conditions.map((condition) => (
                                    <QueryConditionRow
                                        key={condition.id}
                                        condition={condition}
                                        onUpdate={updateCondition}
                                        onRemove={removeCondition}
                                        fields={DEFAULT_FIELDS}
                                    />
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Advanced Options */}
                    <div className='query-builder__section'>
                        <button className='query-builder__toggle' onClick={() => setShowAdvanced(!showAdvanced)}>
                            {showAdvanced ? '▼' : '▶'} Advanced Options
                        </button>

                        {showAdvanced && (
                            <div className='query-builder__advanced'>
                                <div className='query-builder__row'>
                                    <div className='form-group'>
                                        <label htmlFor='limit'>Limit</label>
                                        <input
                                            type='number'
                                            id='limit'
                                            value={config.limit || ''}
                                            onChange={(e) =>
                                                setLimit(e.target.value ? parseInt(e.target.value) : undefined)
                                            }
                                            placeholder='No limit'
                                        />
                                    </div>
                                    <div className='form-group'>
                                        <label htmlFor='offset'>Offset</label>
                                        <input
                                            type='number'
                                            id='offset'
                                            value={config.offset || ''}
                                            onChange={(e) =>
                                                setOffset(e.target.value ? parseInt(e.target.value) : undefined)
                                            }
                                            placeholder='0'
                                        />
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Request Preview */}
                    <div className='query-builder__section query-builder__section--preview'>
                        <h3>Request Preview</h3>
                        <RequestPreview config={config} />
                    </div>

                    {/* Actions */}
                    <div className='query-builder__actions'>
                        <button className='btn btn--primary' onClick={execute} disabled={!canExecute || loading}>
                            {loading ? 'Executing...' : 'Execute Query'}
                        </button>
                        <button className='btn btn--secondary' onClick={clearResponse} disabled={!response}>
                            Clear Response
                        </button>
                        <button className='btn btn--danger' onClick={reset}>
                            Reset All
                        </button>
                    </div>
                </div>

                {/* Response Panel */}
                <div className='query-builder__panel query-builder__panel--response'>
                    <div className='query-builder__panel-header'>
                        <h2>Response</h2>
                    </div>
                    <ResponseTable response={response} loading={loading} />
                </div>
            </div>
        </div>
    );
}

export { App as QueryBuilder };
