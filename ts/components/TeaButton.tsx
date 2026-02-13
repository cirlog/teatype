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
import React from 'react';

// Style
import './style/TeaButton.scss';

type tButtonSize = 'small' | 'medium' | 'large';
type tButtonTheme = 'default' | 'primary' | 'secondary' | 'success' | 'danger' | 'ghost';
type tButtonVariant = 'default';

interface iTeaButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    children?: React.ReactNode;
    size?: tButtonSize;
    icon?: React.ReactNode;
    iconPosition?: 'left' | 'right';
    loading?: boolean;
    theme?: tButtonTheme;
    variant?: tButtonVariant;
}

const TeaButton: React.FC<iTeaButtonProps> = ({
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
    // Constants
    const classes = [
        'tea-button',
        `tea-button--${size}`,
        `tea-button--${variant}`,
        loading && 'tea-button--loading',
        className,
    ]
        .filter(Boolean)
        .join(' ');

    return (
        <button className={classes} disabled={disabled || loading} {...props}>
            {loading && (
                <span className='tea-button__spinner'>
                    <svg viewBox='0 0 24 24' fill='none' stroke='currentColor' strokeWidth='2'>
                        <circle cx='12' cy='12' r='10' opacity='0.25' />
                        <path d='M12 2a10 10 0 0 1 10 10' />
                    </svg>
                </span>
            )}

            {icon && iconPosition === 'left' && !loading && <span className='tea-button__icon'>{icon}</span>}

            {children && <span className='tea-button__text'>{children}</span>}

            {icon && iconPosition === 'right' && !loading && <span className='tea-button__icon'>{icon}</span>}
        </button>
    );
};

export default TeaButton;

export { TeaButton };
