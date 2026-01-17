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

import './style/TeaButton.scss';

type ButtonVariant = 'default' | 'primary' | 'secondary' | 'success' | 'danger' | 'ghost';
type ButtonSize = 'sm' | 'md' | 'lg';

interface TeaButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: ButtonVariant;
    size?: ButtonSize;
    icon?: React.ReactNode;
    iconPosition?: 'left' | 'right';
    loading?: boolean;
}

export const TeaButton: React.FC<TeaButtonProps> = ({
    children,
    variant = 'default',
    size = 'md',
    icon,
    iconPosition = 'left',
    loading = false,
    disabled,
    className = '',
    ...props
}) => {
    const classes = ['tea-btn', `tea-btn--${variant}`, `tea-btn--${size}`, loading && 'tea-btn--loading', className]
        .filter(Boolean)
        .join(' ');

    return (
        <button className={classes} disabled={disabled || loading} {...props}>
            {loading && (
                <span className='tea-btn__spinner'>
                    <svg viewBox='0 0 24 24' fill='none' stroke='currentColor' strokeWidth='2'>
                        <circle cx='12' cy='12' r='10' opacity='0.25' />
                        <path d='M12 2a10 10 0 0 1 10 10' />
                    </svg>
                </span>
            )}
            {icon && iconPosition === 'left' && !loading && <span className='tea-btn__icon'>{icon}</span>}
            {children && <span className='tea-btn__text'>{children}</span>}
            {icon && iconPosition === 'right' && !loading && <span className='tea-btn__icon'>{icon}</span>}
        </button>
    );
};

export default TeaButton;
