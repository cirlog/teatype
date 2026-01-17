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

import './style/TeaInput.scss';

interface TeaInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
    label?: string;
    error?: string;
    hint?: string;
}

export const TeaInput: React.FC<TeaInputProps> = ({ label, error, hint, className = '', id, ...props }) => {
    const inputId = id || `tea-input-${Math.random().toString(36).substr(2, 9)}`;

    return (
        <div className={`tea-input-group ${error ? 'tea-input-group--error' : ''} ${className}`}>
            {label && (
                <label htmlFor={inputId} className='tea-input-group__label'>
                    {label}
                </label>
            )}
            <input id={inputId} className='tea-input-group__input' {...props} />
            {error && <span className='tea-input-group__error'>{error}</span>}
            {hint && !error && <span className='tea-input-group__hint'>{hint}</span>}
        </div>
    );
};

interface TeaSelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
    label?: string;
    error?: string;
    hint?: string;
    options: { value: string | number; label: string }[];
}

export const TeaSelect: React.FC<TeaSelectProps> = ({ label, error, hint, options, className = '', id, ...props }) => {
    const selectId = id || `tea-select-${Math.random().toString(36).substr(2, 9)}`;

    return (
        <div className={`tea-input-group ${error ? 'tea-input-group--error' : ''} ${className}`}>
            {label && (
                <label htmlFor={selectId} className='tea-input-group__label'>
                    {label}
                </label>
            )}
            <select id={selectId} className='tea-input-group__select' {...props}>
                {options.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                        {opt.label}
                    </option>
                ))}
            </select>
            {error && <span className='tea-input-group__error'>{error}</span>}
            {hint && !error && <span className='tea-input-group__hint'>{hint}</span>}
        </div>
    );
};

interface TeaTextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
    label?: string;
    error?: string;
    hint?: string;
}

export const TeaTextarea: React.FC<TeaTextareaProps> = ({ label, error, hint, className = '', id, ...props }) => {
    const textareaId = id || `tea-textarea-${Math.random().toString(36).substr(2, 9)}`;

    return (
        <div className={`tea-input-group ${error ? 'tea-input-group--error' : ''} ${className}`}>
            {label && (
                <label htmlFor={textareaId} className='tea-input-group__label'>
                    {label}
                </label>
            )}
            <textarea id={textareaId} className='tea-input-group__textarea' {...props} />
            {error && <span className='tea-input-group__error'>{error}</span>}
            {hint && !error && <span className='tea-input-group__hint'>{hint}</span>}
        </div>
    );
};

export default TeaInput;
