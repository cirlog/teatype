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

import { QueryCondition, QueryOperator, QUERY_OPERATORS, DEFAULT_FIELDS } from '../api/query';

interface QueryConditionRowProps {
    condition: QueryCondition;
    onUpdate: (id: string, updates: Partial<QueryCondition>) => void;
    onRemove: (id: string) => void;
    fields?: string[];
}

export const QueryConditionRow: React.FC<QueryConditionRowProps> = ({
    condition,
    onUpdate,
    onRemove,
    fields = DEFAULT_FIELDS,
}) => {
    const operatorNeedsValue = !['is_null', 'is_not_null'].includes(condition.operator);

    return (
        <div className='query-condition-row'>
            <select
                className='query-condition-row__field'
                value={condition.field}
                onChange={(e) => onUpdate(condition.id, { field: e.target.value })}
            >
                <option value=''>Select field...</option>
                {fields.map((f) => (
                    <option key={f} value={f}>
                        {f}
                    </option>
                ))}
            </select>
            <select
                className='query-condition-row__operator'
                value={condition.operator}
                onChange={(e) => onUpdate(condition.id, { operator: e.target.value as QueryOperator })}
            >
                {QUERY_OPERATORS.map((op) => (
                    <option key={op.value} value={op.value}>
                        {op.label}
                    </option>
                ))}
            </select>
            {operatorNeedsValue && (
                <input
                    className='query-condition-row__value'
                    type='text'
                    placeholder='Value...'
                    value={condition.value}
                    onChange={(e) => onUpdate(condition.id, { value: e.target.value })}
                />
            )}
            <button
                className='btn btn--danger btn--sm query-condition-row__remove'
                onClick={() => onRemove(condition.id)}
            >
                ×
            </button>
        </div>
    );
};

export default QueryConditionRow;
